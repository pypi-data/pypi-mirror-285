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

    child3 = Child(
        states=[
            "eight",
            "nine",
        ],
        initial="eight",
        on_enter="test_method",
        transitions=[
            {
                "source": "eight",
                "dest": "nine",
                "trigger": "change",
            },
        ],
    )

    child2 = Child(
        states=[
            {
                "name": "five",
                "children": child3,
                "remap": {
                    "nine": "six",
                },
            },
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
                "remap": {
                    "six": "seven",
                },
            },
            "seven",
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
                "remap": {
                    "seven": "one",
                },
            },
        ],
        initial="one",
        transitions=[
            {
                "source": "one",
                "dest": "two",
                "trigger": "start",
            },
            {
                "source": "one",
                "dest": "two_four_five",
                "trigger": "jump",
            },
        ],
    )

    child1.test_method.assert_not_called()
    child2.test_method.assert_not_called()
    child3.test_method.assert_not_called()

    assert machine.start()
    assert machine.state == "two_three"

    child1.test_method.assert_called_once()
    child2.test_method.assert_not_called()
    child3.test_method.assert_not_called()

    assert machine.go()
    assert machine.state == "two_four_five_eight"

    child1.test_method.assert_called_once()
    child2.test_method.assert_called_once()
    child3.test_method.assert_called_once()

    assert machine.change()
    assert machine.state == "one"

    child1.test_method.reset_mock()
    child2.test_method.reset_mock()
    child3.test_method.reset_mock()

    assert machine.jump()
    assert machine.state == "two_four_five_eight"

    child1.test_method.assert_called_once()
    child2.test_method.assert_called_once()
    child3.test_method.assert_called_once()


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


def test_str_conditions_nested():

    class Child(BaseMachine):
        def __init__(self, **kwargs):
            self.condition = False
            super().__init__(**kwargs)

    child = Child(
        states=[
            "two",
            "three",
        ],
        initial="two",
        transitions=[
            {
                "source": "two",
                "dest": "three",
                "trigger": "change",
                "conditions": "condition",
            },
        ],
    )

    root = RootMachine(
        states=[
            {
                "name": "one",
                "children": child,
            },
        ],
        initial="one",
    )

    assert root.state == "one_two"
    assert not root.change()
    assert root.state == "one_two"
    child.condition = True
    assert root.change()
    assert root.state == "one_three"
