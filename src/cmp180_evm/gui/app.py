"""Tkinter GUI - "Config & Connection" screen.

Scope for this first version (agreed with the user): load/validate config
files and test the CMP180 connection (mock or real), plus preview a dry run.
It does not run any real measurement workflow yet, because
baseline/power-sweep/frequency-sweep workflows haven't been implemented in
the backend yet either (SPEC.MD Phase 3+). This screen calls the exact same
`cmp180_evm.actions` functions as the CLI, so no logic is duplicated between
the two front ends — once workflows exist, this window gains a second tab
that reuses them the same way.

Information architecture: the "Results" area is a Notebook with a
human-readable "Result" tab (icon + status + labelled fields, built from
`actions.py`'s structured return values) and a "Technical log" tab (the
full timestamped, color-tagged text history) so day-to-day use doesn't
require reading raw Python attribute names, while troubleshooting detail
is still one click away.
"""

import queue
import re
import sys
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from cmp180_evm import actions
from cmp180_evm.gui import state as gui_state


def _default_configs_dir() -> Path:
    """Locate the configs/ folder next to wherever this is actually running from.

    Running from source (`python -m cmp180_evm.gui`): configs/ lives at the repo root.
    Running as a PyInstaller --onefile exe: configs/ is expected next to the .exe
    (shipped alongside it, not bundled read-only inside it, so users can edit
    the YAML files without rebuilding).
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / "configs"
    return Path(__file__).resolve().parents[3] / "configs"


CONFIGS_DIR = _default_configs_dir()
DEFAULT_INSTRUMENT_CONFIG = CONFIGS_DIR / "instrument.example.yaml"
DEFAULT_WLAN_CONFIG = CONFIGS_DIR / "wlan_baseline.example.yaml"

# (title, body) shown by the "?" help button next to each action.
_HELP_TEXT = {
    "validate_instrument": (
        "Validate instrument config",
        "檢查左上角選擇的 instrument config YAML 能否正確載入，以及欄位是否合法"
        "（例如連線位址、Generator/Analyzer port 設定）。\n\n"
        "不會連線到儀器，純粹檢查檔案內容。\n\n"
        "範例：選好 configs/instrument.example.yaml 後按下此按鈕，"
        "成功會在「Result」分頁看到 OK 與各項設定摘要；"
        "若 YAML 格式錯誤或漏填必要欄位，會顯示 INVALID 與錯誤原因。",
    ),
    "validate_wlan": (
        "Validate WLAN config",
        "檢查左上角選擇的 WLAN baseline config YAML 能否正確載入，"
        "以及頻段/頻率是否互相匹配、欄位是否合法。\n\n"
        "不會連線到儀器，純粹檢查檔案內容。\n\n"
        "範例：選好 configs/wlan_baseline.example.yaml 後按下此按鈕，"
        "成功會看到 Band、Center frequency、Generator power 等摘要。",
    ),
    "dry_run": (
        "Dry run",
        "預覽如果真的執行量測，程式會依序做哪些事情"
        "（連線、設定頻率/功率、量測、存檔等）——完全不會送出任何指令到儀器，"
        "純粹是步驟預覽，適合在還沒接硬體、或想先確認設定對不對時使用。\n\n"
        "範例：按下後「Result」分頁會列出一份編號步驟清單，"
        "例如「1. Connect to ...」「2. Set frequency 6105.0 MHz」...",
    ),
    "test_connection": (
        "Test connection",
        "使用左上角選擇的 instrument config，嘗試連線到儀器並讀取身分字串"
        "（*IDN?）、選配項（*OPT?）、目前的錯誤佇列。\n\n"
        "勾選「Use mock instrument」時使用內建的模擬儀器，不需要真實硬體、"
        "也不會有任何風險；取消勾選則會嘗試連到 config 裡設定的真實 IP，"
        "這屬於會真的碰觸硬體的操作。\n\n"
        "範例：勾選 Mock 後按下此按鈕，應該在 1 秒內看到 Connected + "
        "一組假的 IDN 字串（CMP180-MOCK）。",
    ),
}


def _classify_log_line(text: str) -> str:
    """Pick an output_text tag for a log line based on its content. Pure function."""
    if text.startswith("---"):
        return "heading"
    if re.search(r"\b(FAILED|INVALID|ERROR)\b", text):
        return "error"
    if re.search(r"\bOK\b", text) or "Connected successfully" in text:
        return "success"
    return "info"


def _check_path_exists(path_str: str) -> bool:
    """Whether a config-path Entry's current value points at a real file."""
    if not path_str.strip():
        return False
    try:
        return Path(path_str).is_file()
    except OSError:
        return False


def _split_field_message(message: str) -> tuple[str, str]:
    """Split an actions.py "Label: value" description string into a
    (label, value) pair for two-column rendering. Falls back to an empty
    label if the message doesn't follow that convention."""
    label, sep, value = message.partition(": ")
    return (label, value) if sep else ("", message)


_SUMMARY_STYLES = {
    "success": ("#d9f0e3", "#1a7f37", "✓"),  # check mark
    "error": ("#fbe1e1", "#c62828", "✗"),  # cross mark
    "running": ("#e8eef7", "#31517a", "…"),  # ellipsis
    "info": ("#eeeeee", "#555555", "•"),  # bullet
}


class Cmp180GuiApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self._apply_style()

        root.title("CMP180 WLAN EVM Automation - Config & Connection")
        root.geometry("900x700")
        root.minsize(820, 620)

        self._state_path = gui_state.default_state_path()
        defaults = gui_state.GuiState(
            instrument_config_path=str(DEFAULT_INSTRUMENT_CONFIG),
            wlan_config_path=str(DEFAULT_WLAN_CONFIG),
            use_mock=True,
        )
        loaded = gui_state.load_state(self._state_path, defaults)

        self.instrument_config_var = tk.StringVar(value=loaded.instrument_config_path)
        self.wlan_config_var = tk.StringVar(value=loaded.wlan_config_path)
        self.use_mock_var = tk.BooleanVar(value=loaded.use_mock)

        self._buttons: list[ttk.Button] = []
        # Keyed by id(variable): tk.StringVar isn't hashable, so it can't be
        # a dict key directly, but its identity is stable for the app's life.
        self._path_entries: dict[int, ttk.Entry] = {}
        self._path_status_labels: dict[int, ttk.Label] = {}
        self._worker_queue: "queue.Queue[tuple]" = queue.Queue()
        self._busy = False
        self._last_test_used_mock = True

        self._build_widgets()
        self._set_connection_status(connected=False)

        for var in (self.instrument_config_var, self.wlan_config_var):
            self._update_path_status(var)
        for var in (self.instrument_config_var, self.wlan_config_var):
            var.trace_add("write", lambda *_a, v=var: self._on_path_var_changed(v))
        self.use_mock_var.trace_add("write", lambda *_a: self._save_state())
        self.use_mock_var.trace_add("write", lambda *_a: self._update_mode_hint())
        self._update_mode_hint()

        root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._poll_after_id = self.root.after(100, self._poll_worker_queue)

    # -- style / persistence ------------------------------------------------

    def _apply_style(self) -> None:
        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("TButton", padding=6)
        style.configure("TLabelframe", padding=8)
        style.configure("TLabelframe.Label", font=("TkDefaultFont", 9, "bold"))
        style.configure("Invalid.TEntry", fieldbackground="#fde8e8")

    def _on_path_var_changed(self, variable: tk.StringVar) -> None:
        self._update_path_status(variable)
        self._save_state()

    def _save_state(self) -> None:
        gui_state.save_state(
            self._state_path,
            gui_state.GuiState(
                instrument_config_path=self.instrument_config_var.get(),
                wlan_config_path=self.wlan_config_var.get(),
                use_mock=self.use_mock_var.get(),
            ),
        )

    def _on_close(self) -> None:
        self._save_state()
        self.root.after_cancel(self._poll_after_id)
        self.root.destroy()

    # -- layout -----------------------------------------------------------

    def _build_widgets(self) -> None:
        padding = {"padx": 8, "pady": 4}

        self._build_status_banner()

        config_frame = ttk.LabelFrame(self.root, text="Configuration files")
        config_frame.pack(fill="x", **padding)

        self._add_path_row(
            config_frame, "Instrument / routing config:", self.instrument_config_var, row=0
        )
        self._add_path_row(config_frame, "WLAN baseline config:", self.wlan_config_var, row=1)
        config_frame.columnconfigure(1, weight=1)

        self._build_actions(padding)
        self._build_results_notebook(padding)

        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill="x", padx=8, pady=(0, 4))
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(status_frame, textvariable=self.status_var).pack(side="left")
        self.progress = ttk.Progressbar(status_frame, mode="indeterminate", length=160)
        self.progress.pack(side="right")

        ttk.Button(self.root, text="Clear results", command=self._clear_output).pack(
            anchor="e", padx=8, pady=(0, 8)
        )

    def _build_status_banner(self) -> None:
        self.connection_status_var = tk.StringVar(value="● Not connected")
        self.connection_banner = tk.Label(
            self.root,
            textvariable=self.connection_status_var,
            font=("TkDefaultFont", 10, "bold"),
            anchor="w",
            padx=10,
            pady=6,
        )
        self.connection_banner.pack(fill="x")

    def _set_connection_status(self, connected: bool, mock: bool | None = None) -> None:
        if not connected:
            self.connection_status_var.set("● Not connected")
            self.connection_banner.configure(bg="#e0e0e0", fg="#555555")
        elif mock:
            self.connection_status_var.set("● Connected — Mock instrument")
            self.connection_banner.configure(bg="#d9f0e3", fg="#1a7f37")
        else:
            self.connection_status_var.set("● Connected — REAL HARDWARE")
            self.connection_banner.configure(bg="#fff4d6", fg="#8a6100")

    def _build_actions(self, padding) -> None:
        action_frame = ttk.LabelFrame(self.root, text="Actions")
        action_frame.pack(fill="x", **padding)

        self._add_action(
            action_frame, 0, 0,
            "Validate instrument config", self._on_validate_instrument,
            "Checks the YAML loads and fields are valid", "validate_instrument",
        )
        self._add_action(
            action_frame, 0, 1,
            "Validate WLAN config", self._on_validate_wlan,
            "Checks the YAML loads and fields are valid", "validate_wlan",
        )
        self._add_action(
            action_frame, 0, 2,
            "Dry run", self._on_dry_run,
            "Preview only — sends nothing to the instrument", "dry_run",
        )

        ttk.Separator(action_frame, orient="horizontal").grid(
            row=2, column=0, columnspan=3, sticky="ew", padx=6, pady=4
        )

        ttk.Checkbutton(
            action_frame, text="Use mock instrument (no real hardware)", variable=self.use_mock_var
        ).grid(row=3, column=0, columnspan=2, padx=6, pady=(2, 0), sticky="w")
        self.mode_hint_var = tk.StringVar()
        self.mode_hint_label = ttk.Label(
            action_frame, textvariable=self.mode_hint_var, font=("TkDefaultFont", 8)
        )
        self.mode_hint_label.grid(row=4, column=0, columnspan=2, padx=6, pady=(0, 8), sticky="w")

        self._add_action(
            action_frame, 3, 2,
            "Test connection", self._on_test_connection,
            "Connects and reads instrument identity", "test_connection",
        )

        for column in range(3):
            action_frame.columnconfigure(column, weight=1)

    def _add_action(
        self, parent, row: int, col: int, text: str, command, caption: str, help_key: str
    ) -> ttk.Button:
        cell = ttk.Frame(parent)
        cell.grid(row=row, column=col, padx=6, pady=(6, 0), sticky="ew")
        cell.columnconfigure(0, weight=1)

        btn = ttk.Button(cell, text=text, command=command)
        btn.grid(row=0, column=0, sticky="ew")
        help_title, help_body = _HELP_TEXT[help_key]
        ttk.Button(
            cell, text="?", width=2, command=lambda: self._show_help(help_title, help_body)
        ).grid(row=0, column=1, padx=(4, 0))

        ttk.Label(
            parent, text=caption, foreground="#666666", font=("TkDefaultFont", 8)
        ).grid(row=row + 1, column=col, padx=6, pady=(0, 8), sticky="w")

        self._buttons.append(btn)
        return btn

    def _show_help(self, title: str, body: str) -> None:
        messagebox.showinfo(title, body)

    def _update_mode_hint(self) -> None:
        if self.use_mock_var.get():
            self.mode_hint_var.set("Mock mode — safe, no hardware required")
            self.mode_hint_label.configure(foreground="#1a7f37")
        else:
            self.mode_hint_var.set("⚠ Real hardware mode — will attempt a live connection")
            self.mode_hint_label.configure(foreground="#b35c00")

    def _build_results_notebook(self, padding) -> None:
        container = ttk.LabelFrame(self.root, text="Results")
        container.pack(fill="both", expand=True, **padding)

        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill="both", expand=True, padx=4, pady=4)

        self.summary_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.summary_tab, text="Result")

        self.summary_status_frame = tk.Frame(self.summary_tab, pady=10, padx=10)
        self.summary_status_frame.pack(fill="x")
        self.summary_status_var = tk.StringVar()
        self.summary_status_label = tk.Label(
            self.summary_status_frame,
            textvariable=self.summary_status_var,
            font=("TkDefaultFont", 12, "bold"),
            anchor="w",
        )
        self.summary_status_label.pack(fill="x")
        self.summary_subtitle_label: tk.Label | None = None

        self.summary_fields_frame = ttk.Frame(self.summary_tab, padding=10)
        self.summary_fields_frame.pack(fill="both", expand=True)

        self._set_summary_status("info", "No results yet", "Run an action above to see results here.")

        log_tab = ttk.Frame(self.notebook)
        self.notebook.add(log_tab, text="Technical log")

        self.output_text = tk.Text(log_tab, wrap="word", state="disabled")
        scrollbar = ttk.Scrollbar(log_tab, command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scrollbar.set)
        self.output_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.output_text.tag_configure("success", foreground="#1a7f37")
        self.output_text.tag_configure("error", foreground="#c62828")
        self.output_text.tag_configure("info", foreground="#333333")
        self.output_text.tag_configure(
            "heading", foreground="#0b5fa5", font=("TkDefaultFont", 9, "bold")
        )

    def _add_path_row(
        self, parent: ttk.LabelFrame, label: str, variable: tk.StringVar, row: int
    ) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, padx=6, pady=4, sticky="w")
        entry = ttk.Entry(parent, textvariable=variable)
        entry.grid(row=row, column=1, padx=6, pady=4, sticky="ew")
        entry.bind("<FocusOut>", lambda _e, v=variable: self._update_path_status(v))
        ttk.Button(
            parent, text="Browse...", command=lambda: self._browse(variable)
        ).grid(row=row, column=2, padx=6, pady=4)
        status_label = ttk.Label(parent, text="", foreground="#c62828")
        status_label.grid(row=row, column=3, padx=6, pady=4, sticky="w")

        self._path_entries[id(variable)] = entry
        self._path_status_labels[id(variable)] = status_label

    # -- helpers ------------------------------------------------------------

    def _browse(self, variable: tk.StringVar) -> None:
        initial_dir = CONFIGS_DIR if CONFIGS_DIR.exists() else Path.cwd()
        path = filedialog.askopenfilename(
            initialdir=str(initial_dir),
            filetypes=[("YAML files", "*.yaml *.yml"), ("All files", "*.*")],
        )
        if path:
            variable.set(path)

    def _update_path_status(self, variable: tk.StringVar) -> None:
        ok = _check_path_exists(variable.get())
        self._path_status_labels[id(variable)].configure(text="" if ok else "not found")
        self._path_entries[id(variable)].configure(style="TEntry" if ok else "Invalid.TEntry")

    def _log(self, text: str) -> None:
        timestamp = time.strftime("%H:%M:%S")
        self.output_text.configure(state="normal")
        self.output_text.insert("end", f"[{timestamp}] {text}\n", _classify_log_line(text))
        self.output_text.configure(state="disabled")
        self.output_text.see("end")

    def _clear_output(self) -> None:
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.configure(state="disabled")
        self._set_summary_status("info", "No results yet", "Run an action above to see results here.")
        self._render_summary_fields([])

    # -- result summary tab --------------------------------------------------

    def _set_summary_status(self, kind: str, title: str, subtitle: str = "") -> None:
        bg, fg, icon = _SUMMARY_STYLES[kind]
        self.summary_status_frame.configure(bg=bg)
        self.summary_status_label.configure(bg=bg, fg=fg)
        self.summary_status_var.set(f"{icon}  {title}")
        if subtitle:
            if self.summary_subtitle_label is None:
                self.summary_subtitle_label = tk.Label(
                    self.summary_status_frame,
                    text=subtitle,
                    bg=bg,
                    fg=fg,
                    font=("TkDefaultFont", 9),
                    anchor="w",
                )
                self.summary_subtitle_label.pack(fill="x")
            else:
                self.summary_subtitle_label.configure(text=subtitle, bg=bg, fg=fg)
                self.summary_subtitle_label.pack(fill="x")
        elif self.summary_subtitle_label is not None:
            self.summary_subtitle_label.pack_forget()

    def _render_summary_fields(self, rows: list[tuple[str, str]]) -> None:
        for widget in self.summary_fields_frame.winfo_children():
            widget.destroy()
        for i, (label, value) in enumerate(rows):
            ttk.Label(
                self.summary_fields_frame, text=label, font=("TkDefaultFont", 9, "bold")
            ).grid(row=i, column=0, sticky="nw", padx=(0, 12), pady=2)
            ttk.Label(
                self.summary_fields_frame, text=value, wraplength=560, justify="left"
            ).grid(row=i, column=1, sticky="w", pady=2)

    # -- background execution ------------------------------------------------

    def _set_busy(self, busy: bool, label: str = "") -> None:
        self._busy = busy
        for btn in self._buttons:
            btn.state(["disabled"] if busy else ["!disabled"])
        if busy:
            self.status_var.set(label)
            self.progress.start(10)
            self.root.config(cursor="watch")
        else:
            self.status_var.set("Ready")
            self.progress.stop()
            self.root.config(cursor="")

    def _run_in_background(self, func, on_success, label: str) -> None:
        if self._busy:
            return
        self._set_busy(True, label)
        thread = threading.Thread(target=self._worker_entry, args=(func, on_success), daemon=True)
        thread.start()

    def _worker_entry(self, func, on_success) -> None:
        # Runs on a background thread. Must never touch a Tk widget/variable
        # directly here — only `func()` and putting the result on the queue.
        try:
            result = func()
            self._worker_queue.put(("success", on_success, result))
        except Exception as exc:  # surfaced to the log/messagebox on the main thread
            self._worker_queue.put(("error", None, exc))

    def _poll_worker_queue(self) -> None:
        try:
            while True:
                kind, callback, payload = self._worker_queue.get_nowait()
                try:
                    if kind == "success":
                        callback(payload)
                    else:
                        self._log(f"FAILED: {payload}")
                        messagebox.showerror("Operation failed", str(payload))
                        self._set_summary_status("error", "Operation failed", str(payload))
                        self._render_summary_fields([])
                finally:
                    self._set_busy(False)
        except queue.Empty:
            pass
        self._poll_after_id = self.root.after(100, self._poll_worker_queue)

    # -- actions --------------------------------------------------------

    def _on_validate_instrument(self) -> None:
        self._run_validate(Path(self.instrument_config_var.get()))

    def _on_validate_wlan(self) -> None:
        self._run_validate(Path(self.wlan_config_var.get()))

    def _run_validate(self, path: Path) -> None:
        self._log(f"--- validate-config: {path} ---")
        self.notebook.select(self.summary_tab)
        self._set_summary_status("running", f"Validating {path.name}…")
        self._render_summary_fields([])
        self._run_in_background(
            lambda: actions.validate_config(path),
            lambda result: self._handle_validate_result(path, result),
            label="Validating...",
        )

    def _handle_validate_result(self, path: Path, result: actions.ValidationResult) -> None:
        self._log(f"OK ({result.kind})" if result.ok else "INVALID")
        for message in result.messages:
            self._log(f"  {message}")
        if result.ok:
            self._set_summary_status(
                "success", f"{path.name} is valid", f"Config kind: {result.kind}"
            )
        else:
            self._set_summary_status("error", f"{path.name} is invalid", "See details below")
        self._render_summary_fields([_split_field_message(m) for m in result.messages])

    def _on_dry_run(self) -> None:
        self._log("--- dry-run ---")
        self.notebook.select(self.summary_tab)
        instrument_path = Path(self.instrument_config_var.get())
        wlan_path = Path(self.wlan_config_var.get())
        self._set_summary_status("running", "Building dry run preview…")
        self._render_summary_fields([])
        self._run_in_background(
            lambda: actions.dry_run_steps(instrument_path, wlan_path),
            self._handle_dry_run_result,
            label="Building dry run...",
        )

    def _handle_dry_run_result(self, steps: list[str]) -> None:
        for step in steps:
            self._log(step)
        self._set_summary_status(
            "info", "Dry run preview", "No commands were sent to the instrument"
        )
        self._render_summary_fields([(f"{i + 1}.", step) for i, step in enumerate(steps)])

    def _on_test_connection(self) -> None:
        use_mock = self.use_mock_var.get()
        self._last_test_used_mock = use_mock
        path = Path(self.instrument_config_var.get())
        self._log(f"--- test-connection (mock={use_mock}) ---")
        self.notebook.select(self.summary_tab)
        self._set_summary_status("running", "Testing connection…")
        self._render_summary_fields([])
        self._run_in_background(
            lambda: actions.test_connection(path, use_mock=use_mock),
            self._handle_connection_result,
            label="Testing connection...",
        )

    def _handle_connection_result(self, result: actions.ConnectionResult) -> None:
        if not result.ok:
            self._log(f"FAILED: {result.message}")
            messagebox.showerror("Connection failed", result.message)
            self._set_summary_status("error", "Connection failed", result.message)
            self._render_summary_fields([])
            self._set_connection_status(connected=False)
            return
        self._log(result.message)
        self._log(f"  IDN: {result.idn}")
        self._log(f"  OPT: {result.options}")
        self._log(f"  Error queue: {result.errors or 'empty'}")
        self._set_summary_status(
            "success",
            "Connected",
            "Mock instrument" if self._last_test_used_mock else "REAL HARDWARE",
        )
        self._render_summary_fields(
            [
                ("Instrument ID", result.idn or "—"),
                ("Options", result.options or "—"),
                ("Error queue", ", ".join(result.errors) if result.errors else "Empty"),
            ]
        )
        self._set_connection_status(connected=True, mock=self._last_test_used_mock)


def main() -> None:
    root = tk.Tk()
    Cmp180GuiApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
