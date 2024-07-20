import pytest
from pigeon_transitions import BaseMachine, RootMachine


def test_to_callable():
    class TestMachine(BaseMachine):
        def __init__(self):
            self.parent = None

        def method1(self):
            pass

        def method2(self):
            pass

    test_machine = TestMachine()

    initial_data = [
        {
            "t1": 3,
            "func_tag": "method2",
            "tag_test": "two",
        },
        ["one", "two", "three"],
        {
            "test_tag": 1,
            "func_tag": "method1",
        },
        {
            "func_tag": "method3",
        },
        {
            "other_func_tag": "method1",
            "not_func_tag": "method1",
        },
    ]

    final_data = [
        {
            "t1": 3,
            "func_tag": [test_machine.method2],
            "tag_test": "two",
        },
        ["one", "two", "three"],
        {
            "test_tag": 1,
            "func_tag": [test_machine.method1],
        },
        {
            "func_tag": ["method3"],
        },
        {
            "other_func_tag": [test_machine.method1],
            "not_func_tag": "method1",
        },
    ]

    assert (
        test_machine._to_callable(initial_data, ["func_tag", "other_func_tag"])
        == final_data
    )


def test_getattr(mocker):
    test_machine = BaseMachine()
    test_machine.parent = mocker.MagicMock()
    test_machine.parent.parent.parent = None

    assert test_machine.state == test_machine.parent.parent.state


def test_add_machine_states(mocker):
    super_func = mocker.MagicMock()
    mocker.patch("pigeon_transitions.base.Machine._add_machine_states", super_func)
    mocker.patch(
        "pigeon_transitions.base.Machine.get_global_name",
        mocker.MagicMock(return_value="test_name"),
    )
    test_machine = BaseMachine()

    states = mocker.MagicMock()
    test_machine._add_machine_states(states, "test_arg")

    super_func.assert_called_with(states, "test_arg")
    assert states.parent == test_machine
    assert test_machine._children == {"test_name": states}


def test_client(mocker):
    test_machine = BaseMachine()
    test_machine.parent = mocker.MagicMock()
    test_machine.parent.parent = None
    test_machine.parent._get_current_machine.return_value = test_machine

    assert test_machine.client == test_machine.parent._client

    test_machine.parent._get_current_machine.return_value = "another_machine"

    assert test_machine.client is None


def test_on_machine_enter(mocker):
    class Child(BaseMachine):
        def __init__(self, **args):
            self.test_method = mocker.MagicMock()
            super().__init__(**args)

    child2 = Child(
        states=[
            "five",
            "six",
        ],
        initial="five",
        on_enter="test_method",
    )

    child1 = Child(
        states=[
            "three",
            {
                "name": "four",
                "children": child2,
            },
        ],
        initial="three",
        transitions=[
            {
                "source": "three",
                "dest": "four",
                "trigger": "go",
            },
        ],
        on_enter="test_method",
    )

    machine = RootMachine(
        states=[
            "one",
            {
                "name": "two",
                "children": child1,
            },
        ],
        initial="one",
        transitions=[
            {
                "source": "one",
                "dest": "two",
                "trigger": "start",
            },
        ],
    )

    child1.test_method.assert_not_called()
    child2.test_method.assert_not_called()

    assert machine.start()

    child1.test_method.assert_called_once()
    child2.test_method.assert_not_called()

    assert machine.go()

    child1.test_method.assert_called_once()
    child2.test_method.assert_called_once()


def test_var_to_func():

    class Root(RootMachine):
        def __init__(self):
            self.condition = False
            super().__init__(
                states=[
                    "one",
                    "two",
                ],
                initial="one",
                transitions=[
                    {
                        "source": "one",
                        "dest": "two",
                        "trigger": "go",
                        "conditions": "condition",
                    },
                ],
            )

    machine = Root()
    assert machine.state == "one"
    assert not machine.go()
    assert machine.state == "one"
    machine.condition = True
    assert machine.go()
    assert machine.state == "two"
