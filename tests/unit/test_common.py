import src.common as cmn

def test_always_passes():
    acc = cmn.get_context_param("dev", "account")
    assert ( acc != None and acc == '817409382164')