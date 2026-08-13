# CMP180 Automation GUI — Initial Specification

The GUI is a planned project deliverable. It will call the same application services
as the CLI; it will not contain SCPI strings or measurement logic in UI event handlers.

## Screens

1. **Dashboard** — CMP180 reachability, session state, identity, firmware, WLAN
   capability, active run and latest errors.
2. **Connection** — resource, backend, timeout, connect/disconnect and doctor output.
3. **WLAN Profile** — standard, band, channel/frequency, bandwidth, receive mode,
   RF connection, attenuation, nominal power, trigger and analysis settings.
4. **Single Measurement** — preflight summary, DUT readiness confirmation, start,
   cancel, progress, EVM/power/frequency-error cards and artifacts.
5. **Sweep** — one-axis sweep editor, point preview, estimated duration, retry policy,
   progress table and live plot.
6. **Results** — run history, filters, detail view, CMsquares baseline comparison,
   CSV/JSON/PNG/HTML export.
7. **Diagnostics** — command trace, status/error queue, discovery report and sanitized
   support bundle.

## Safety and behavior

- Settings are validated before a session-changing action.
- Start displays an exact preflight summary and blocks unverified profiles.
- Reset/preset and arbitrary SCPI are excluded from the normal GUI.
- Cancel performs deterministic workflow cleanup and preserves completed points.
- Invalid results are displayed as invalid, never as numeric zero.
- UI remains responsive while measurements run in a worker/service layer.
- A run has one immutable resolved configuration and unique Run ID.

## Delivery sequence

1. Measurement domain models and fake transport.
2. CMP180 connection/discovery service.
3. Verified WLAN single-measurement service.
4. CLI and automated tests over the same services.
5. Desktop or local-web GUI shell.
6. Sweep, live progress, plots and run history.
7. Packaging, user testing and release.

The GUI framework decision is deferred until the core service boundary is stable.
Current candidates are PySide6 for a native Windows desktop application or a local
web application for faster UI iteration. The choice does not change the measurement
core or artifact formats.

