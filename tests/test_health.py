from pyuubin.health import get_health, update_health


def test_health_updates():

    update_health("status.threads.1", "test")
    update_health("start_date", "something")
    update_health("some.thing", "to test")
    health = get_health()

    assert health["status"]["threads"]["1"] == "test"
    assert health["some"]["thing"] == "to test"
    assert health["start_date"] == "something"

