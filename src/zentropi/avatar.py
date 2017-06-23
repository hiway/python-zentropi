# coding=utf-8
import yaml
from .agent import Agent


class Avatar(Agent):
    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        self._rules_path = 'avatar.yml'
        self.load_rules()

    def _get_rules(self, rules_path):
        rules = {}
        with open(rules_path) as rules_file:
            rules = yaml.safe_load(rules_file)
        return rules

    def save_rules(self, rules_path=None):
        pass

    def load_rules(self, rules_path=None):
        rules = self._get_rules(rules_path or self._rules_path)
        print(rules)
