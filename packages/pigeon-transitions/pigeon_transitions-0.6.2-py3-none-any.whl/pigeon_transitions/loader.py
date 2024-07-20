from .config import PigeonTransitionsConfig
from .base import RootMachine
from yaml import safe_load
from copy import copy
from pigeon.utils import setup_logging


class MachineLoader:
    def __init__(self):
        self.machines = {}
        self._logger = setup_logging("pigeon-transitions")
        setup_logging("transitions")

    def load(self, config):
        for i in range(len(config)):
            for name, machine in config.items():
                if self.is_initialized(name):
                    continue
                if self.can_init(machine):
                    self.init_machine(machine, name)
            if self.all_initialized(config):
                for machine in self.machines.values():
                    if isinstance(machine, RootMachine):
                        return machine
        raise RecursionError("Unable to load state machine.")

    def all_initialized(self, config):
        return len(self.machines) == len(config)

    @staticmethod
    def has_children(machine):
        for state in machine.states:
            if "children" in state:
                return True
        return False

    @staticmethod
    def iter_children(machine):
        if machine.states is None:
            return []
        for state in machine.states:
            if "children" in state:
                yield state["children"]

    def children_initialized(self, machine):
        for child in self.iter_children(machine):
            if child not in self.machines:
                return False
        return True

    def can_init(self, machine):
        return self.children_initialized(machine)

    def is_initialized(self, name):
        return name in self.machines

    def init_machine(self, machine, name):
        kwargs = machine._as_dict
        del kwargs["type"]
        for state in kwargs.get("states", []):
            if not isinstance(state, dict):
                continue
            if "children" in state:
                state["children"] = self.machines[state["children"]]
        kwargs["logger"] = self._logger
        kwargs["name"] = name
        self.machines[name] = machine.type(**kwargs)


class Loader:
    @classmethod
    def load(cls, config):
        machine = MachineLoader().load(config.machines)
        return machine

    @classmethod
    def from_string(cls, config):
        return cls.load(PigeonTransitionsConfig(**safe_load(config)))

    @classmethod
    def from_file(cls, confg_file):
        with open(confg_file) as f:
            return cls.from_string(f.read())
