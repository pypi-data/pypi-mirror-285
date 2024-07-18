import argparse
import socket
from collections.abc import Mapping, Sequence
from copy import deepcopy

import yaml
from parse import *


class Apter(argparse.Namespace):
    def __init__(self, kvs, root=None, **kwargs):
        super(Apter, self).__init__(**kwargs)
        self.kvs = kvs
        self.root = kvs if root is None else root
        self.add_env_config()

    def add_env_config(self):
        self.add_mapping('ENV.hostname', socket.gethostname())

    @staticmethod
    def load_yaml(stream):
        return Apter(yaml.load(stream, Loader=yaml.SafeLoader))

    def __getitem__(self, item):
        value = self.kvs[item]
        if isinstance(value, str):
            return self.__resolve__(self.kvs[item])
        elif isinstance(value, Mapping):
            return Apter(value, self.root)
        elif isinstance(value, Sequence):
            new_sequence = []
            for seq_item in value:
                if isinstance(seq_item, Mapping):
                    new_sequence.append(Apter(seq_item, self.root))
                else:
                    new_sequence.append(self.__resolve__(seq_item))
            return new_sequence
        return value

    def __getattr__(self, item):
        return self[item]

    def __setitem__(self, key, value):
        super(Apter, self).__setattr__(key, value)
        if self.kvs is not None and key in self.kvs:
            self.kvs[key] = value

    def __setattr__(self, key, value):
        super(Apter, self).__setattr__(key, value)
        if self.kvs is not None and key in self.kvs:
            self.kvs[key] = value

    def add_mapping(self, key, value):
        path = key.split('.')
        final_key = path[-1]
        path = path[:-1]
        entry = self.root
        for subkey in path:
            if subkey in entry:
                entry = entry[subkey]
            else:
                entry[subkey] = {}
                entry = entry[subkey]
        entry[final_key] = value

    def get(self, key, default):
        path = key.split('.')
        parent = self.kvs
        for subkey in path:
            if subkey in parent:
                parent = parent[subkey]
            else:
                return default
        return parent

    def __resolve__(self, value):
        while search('${{{}}}', value) is not None:
            for reference in findall('${{{}}}', value):
                ref_value = self.root
                for path_element in reference.fixed[0].split('.'):
                    ref_value = ref_value[path_element]
                value = value.replace('${' + reference.fixed[0] + '}', ref_value)
        return value

    def overlay(self, config):
        for key, value in config.kvs.items():
            self.__recursiveset__(key, value)

    def __recursiveset__(self, key, value):
        if isinstance(value, Mapping):
            for subkey in value:
                self.__recursiveset__('.'.join([key, subkey]), value[subkey])
        else:
            self.add_mapping(key, value)

    def to_user_config_str(self):
        user_config = deepcopy(self.kvs)
        user_config.pop('ENV', None)
        return yaml.safe_dump(user_config, default_flow_style=False)

    def to_resolved_user_config_str(self):
        return self.__resolve__(self.to_user_config_str())

    def to_resolved_str(self):
        return self.__resolve__(str(self))

    def items(self):
        return iter(self.kvs.items())

    def __str__(self):
        return yaml.safe_dump(self.kvs, default_flow_style=False)

    def __repr__(self):
        return "config={}; root={}".format(yaml.dump(self.kvs), yaml.dump(self.root))

    def __contains__(self, item):
        return item in self.kvs
