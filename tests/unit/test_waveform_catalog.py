from scripts.cmp180_waveform_catalog import _parent_pattern, parse_catalog_response


def test_parse_catalog_response_extracts_all_waveform_bandwidths():
    response = (
        '123,456,"a_BW20_test.wv,BIN,10","b_BW160_test.wv,BIN,20",'
        '"notes.txt,ASC,5"'
    )
    records = parse_catalog_response(response)
    assert records[0]["bandwidth_mhz"] == 20
    assert records[1]["bandwidth_mhz"] == 160
    assert records[2]["bandwidth_mhz"] is None


def test_parent_pattern_handles_instrument_windows_path():
    assert _parent_pattern('"D:\\Waveforms\\selected_BW320.wv"') == "D:/Waveforms/*.wv"
