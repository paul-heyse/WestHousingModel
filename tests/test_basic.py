from west_housing_model import ping


def test_ping():
    assert ping() == "pong"
