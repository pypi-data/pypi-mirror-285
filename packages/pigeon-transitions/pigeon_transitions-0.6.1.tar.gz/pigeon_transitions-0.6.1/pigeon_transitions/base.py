from transitions.extensions import HierarchicalGraphMachine as Machine
from transitions.extensions.states import add_state_features, Timeout
from transitions.core import listify, EventData, Event
from pigeon import Pigeon
from pigeon.utils import setup_logging, call_with_correct_args


@add_state_features(Timeout)
class BaseMachine(Machine):
    def __init__(
        self,
        *args,
        states=None,
        transitions=None,
        model=[],
        logger=None,
        on_enter=None,
        before_state_change=None,
        after_state_change=None,
        prepare_event=None,
        finalize_event=None,
        on_exception=None,
        on_final=None,
        **kwargs,
    ):
        self.parent = None
        self._children = {}
        self._on_enter = self._get_callables(on_enter)
        super().__init__(
            *args,
            states=self._to_callable(states, ["on_enter", "on_exit", "on_timeout"]),
            transitions=self._to_callable(
                transitions, ["prepare", "conditions", "unless", "before", "after"]
            ),
            model=model,
            auto_transitions=False,
            show_conditions=True,
            before_state_change=self._get_callables(before_state_change),
            after_state_change=self._get_callables(after_state_change),
            prepare_event=self._get_callables(prepare_event),
            finalize_event=self._get_callables(finalize_event),
            on_exception=self._get_callables(on_exception),
            on_final=self._get_callables(on_final),
            **kwargs,
        )
        self._logger = logger if logger is not None else setup_logging(__name__)

    def _remap_state(self, state, remap):
        ret = super()._remap_state(state, remap)
        for old_state in remap.keys():
            del self.states[old_state]
        return ret

    def _to_callable(self, data, callbacks):
        if data is None:
            return data
        for el in data:
            if isinstance(el, dict):
                for callback in callbacks:
                    if callback in el:
                        el[callback] = self._get_callables(el[callback])
        return data

    def _get_callable(self, func):
        if isinstance(func, str):
            tmp = getattr(self, func, func)
            if callable(tmp):
                return tmp
            return func
        if not callable(func):
            return lambda: func
        return func

    def _get_callables(self, funcs):
        if funcs is None:
            return []
        return [self._get_callable(func) for func in listify(funcs)]

    def _add_machine_states(self, state, remap):
        state.parent = self
        self._children[self.get_global_name()] = state
        super()._add_machine_states(state, remap)

    def _add_dict_state(self, state, *args, **kwargs):
        if "on_enter" not in state:
            state["on_enter"] = []
        if "children" in state and isinstance(state["children"], BaseMachine):
            state["on_enter"] += state["children"]._on_enter
        return super()._add_dict_state(state, *args, **kwargs)

    def message_callback(self):
        pass

    @property
    def root(self):
        root = self
        while root.parent is not None:
            root = root.parent
        return root

    @property
    def client(self):
        if self._current_machine():
            return self.root._client
        return None

    def _current_machine(self):
        return self.root._get_current_machine() == self

    def __getattr__(self, name):
        if self.parent is None:
            return super().__getattr__(name)
        return getattr(self.root, name)


class RootMachine(BaseMachine):
    def __init__(self, *args, **kwargs):
        self._client = None
        self.parent = None
        self._collected = {}
        super().__init__(*args, model=RootMachine.self_literal, **kwargs)

    def add_client(
        self, service=None, host="127.0.0.1", port=61616, username=None, password=None
    ):
        self._client = Pigeon(
            service if service is not None else self.__class__.__name__,
            host=host,
            port=port,
        )
        self._client.connect(username=username, password=password)
        self._client.subscribe_all(self._message_callback)

    def save_graph(self, path):
        extension = path.split(".")[-1].lower()
        self.get_graph().render(format=extension, cleanup=True, outfile=path)

    def _get_machine(self, state):
        child = self
        for state in state.split(self.separator)[:-1]:
            child = child._children[state]
        return child

    def _get_current_machine(self):
        return self._get_machine(self.state)

    def _get_current_machines(self):
        yield self._get_current_machine()
        state_list = self.state.split(self.separator)
        for i in range(1, len(state_list)):
            yield self._get_machine(self.separator.join(state_list[:-i]))

    def _get_state_obj(self, state):
        state_list = state.split(self.separator)
        state_obj = self
        while len(state_list):
            state_obj = state_obj.states[state_list.pop(0)]
        return state_obj

    def _message_callback(self, msg, topic, *args, **kwargs):
        self._collect(topic, msg)
        for machine in self._get_current_machines():
            try:
                call_with_correct_args(
                    machine.message_callback, msg, topic, *args, **kwargs
                )
            except Exception as e:
                self._logger.warning(
                    f"Callback for a message on topic '{topic}' with data '{msg}' resulted in an exception:",
                    exc_info=True,
                )

    def _collect(self, topic, msg):
        self._collected[topic] = msg

    def get_collected(self, topic):
        self._client._ensure_topic_exists(topic)
        return self._collected.get(topic, None)

    def _get_initial_states(self):
        states = [self.states[self.initial]]
        while len(states[-1].states):
            states.append(states[-1].states[states[-1].initial])
        return states

    def _start(self):
        for state in self._get_initial_states():
            state.enter(
                EventData(
                    state, Event("_start", self), self, self, args=[], kwargs={}
                )
            )

    def _run(self):
        self._start()
        while True:
            pass

    def resolve_callable(self, func, event_data):
        updated_func = func
        if isinstance(func, str):
            current_machine = self._get_machine(event_data.state.name)
            if hasattr(current_machine, func):
                updated_func = getattr(current_machine, func)
                if not callable(updated_func):
                    tmp = updated_func
                    updated_func = lambda: tmp
        return super().resolve_callable(updated_func, event_data)
