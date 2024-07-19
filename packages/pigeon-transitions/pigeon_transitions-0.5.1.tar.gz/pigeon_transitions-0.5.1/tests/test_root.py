from pigeon_transitions import RootMachine, BaseMachine
import pytest


def test_constructor(mocker):
    init = mocker.MagicMock()
    mocker.patch("pigeon_transitions.base.BaseMachine.__init__", init)

    test_machine = RootMachine(
        1,
        2,
        three=3,
        four=4,
    )

    assert test_machine._client is None
    assert test_machine.parent is None
    assert test_machine._collected == {}
    init.assert_called_with(1, 2, model="self", three=3, four=4)


def test_add_client(mocker):
    pigeon = mocker.MagicMock()
    mocker.patch("pigeon_transitions.base.Pigeon", pigeon)

    class TestMachine(RootMachine):
        pass

    test_machine = TestMachine()
    test_machine.add_client(
        host="1.2.3.4", port=4321, username="user", password="passcode"
    )

    pigeon.assert_called_with("TestMachine", host="1.2.3.4", port=4321)
    pigeon().connect.assert_called_with(username="user", password="passcode")
    pigeon().subscribe_all.assert_called_with(test_machine._message_callback)


def test_message_callback(mocker):
    mocker.patch("pigeon_transitions.base.setup_logging", mocker.MagicMock())

    class Child(BaseMachine):
        def __init__(self):
            self._mock_callback = mocker.MagicMock()
            super().__init__(
                states=[
                    "test",
                ],
                initial="test",
            )

        def message_callback(self, msg, topic):
            self._mock_callback(msg, topic)

    child2 = Child()
    child3 = Child()

    class Root(RootMachine):
        def __init__(self):
            self._mock_callback = mocker.MagicMock()
            super().__init__(
                states=[
                    "one",
                    {
                        "name": "two",
                        "children": child2,
                    },
                    {
                        "name": "three",
                        "children": child3,
                    },
                ],
                initial="one",
                transitions=[
                    {
                        "source": "one",
                        "dest": "two",
                        "trigger": "change",
                    },
                    {
                        "source": "two",
                        "dest": "three",
                        "trigger": "change",
                    },
                ],
            )
            self._client = mocker.MagicMock()

        def message_callback(self, msg, topic):
            self._mock_callback(msg, topic)

    root = Root()

    assert root.state == "one"

    root._message_callback("some_data", "topic1")
    root.change()

    assert root.state == "two_test"

    root._message_callback("some_other_data", "topic2")
    root.change()

    assert root.state == "three_test"

    root._message_callback("some_new_data", "topic1")

    root._mock_callback.assert_has_calls(
        [
            mocker.call("some_data", "topic1"),
            mocker.call("some_other_data", "topic2"),
            mocker.call("some_new_data", "topic1"),
        ],
    )

    child2._mock_callback.assert_called_once_with("some_other_data", "topic2")

    child3._mock_callback.assert_called_once_with("some_new_data", "topic1")

    child3._mock_callback.side_effect = Exception
    root._message_callback("other_data", "topic3")
    root._logger.warning.assert_called_with(
        "Callback for a message on topic 'topic3' with data 'other_data' resulted in an exception:",
        exc_info=True,
    )
    root._mock_callback.assert_called_with("other_data", "topic3")

    assert root._collected == {
        "topic1": "some_new_data",
        "topic2": "some_other_data",
        "topic3": "other_data",
    }
    assert root.get_collected("topic1") == "some_new_data"
    assert root.get_collected("topic2") == "some_other_data"
    assert root.get_collected("topic3") == "other_data"
    assert root.get_collected("topic4") is None


def test_get_current_machine(mocker):
    state_list = ["machine1", "machine2", "state"]
    test_machine = RootMachine()
    test_machine.state = test_machine.separator.join(state_list)
    test_machine._children = {
        "machine1": mocker.MagicMock(_children={"machine2": "the value"})
    }
    assert test_machine._get_current_machine() == "the value"
