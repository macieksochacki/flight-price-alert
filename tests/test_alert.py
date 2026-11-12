from alert import should_alert


def test_empty_history():
    assert should_alert(700, []) == True


def test_min_historic():
    assert should_alert(700, [800, 750]) == True


def test_min_equal():
    assert should_alert(700, [800, 700]) == False


def test_higher():
    assert should_alert(700, [800, 600]) == False
