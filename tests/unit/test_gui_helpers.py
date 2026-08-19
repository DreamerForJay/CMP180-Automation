from pathlib import Path

from cmp180_evm.gui.app import _check_path_exists, _classify_log_line, _split_field_message


def test_classify_log_line_heading():
    assert _classify_log_line("--- validate-config: foo.yaml ---") == "heading"


def test_classify_log_line_failed_is_error():
    assert _classify_log_line("FAILED: could not connect") == "error"


def test_classify_log_line_invalid_is_error():
    assert _classify_log_line("INVALID") == "error"


def test_classify_log_line_error_word_is_error():
    assert _classify_log_line("SCPI ERROR queue not empty") == "error"


def test_classify_log_line_ok_is_success():
    assert _classify_log_line("OK (instrument)") == "success"


def test_classify_log_line_connected_successfully_is_success():
    assert _classify_log_line("Connected successfully (mock)") == "success"


def test_classify_log_line_plain_text_is_info():
    assert _classify_log_line("  routing.generator_port = RF1.1 (confirmed=True)") == "info"


def test_check_path_exists_true_for_real_file(tmp_path: Path):
    config = tmp_path / "instrument.yaml"
    config.write_text("instrument: {}", encoding="utf-8")

    assert _check_path_exists(str(config)) is True


def test_check_path_exists_false_for_missing_file(tmp_path: Path):
    missing = tmp_path / "does_not_exist.yaml"

    assert _check_path_exists(str(missing)) is False


def test_check_path_exists_false_for_directory(tmp_path: Path):
    assert _check_path_exists(str(tmp_path)) is False


def test_check_path_exists_false_for_blank_string():
    assert _check_path_exists("") is False
    assert _check_path_exists("   ") is False


def test_split_field_message_with_label():
    assert _split_field_message("Generator port: RF1.1 (confirmed)") == (
        "Generator port",
        "RF1.1 (confirmed)",
    )


def test_split_field_message_without_colon_falls_back_to_empty_label():
    assert _split_field_message("just a plain message") == ("", "just a plain message")
