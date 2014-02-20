import os
import yaml
import json


def read_file(file_name):
    path = os.path.join(os.path.dirname(__file__), '..', '..')
    file_name = os.path.abspath(os.path.join(path, file_name))
    return open(file_name, 'rb')

def read_yaml(file_name):
    return yaml.load(read_file(file_name).read())

def read_json(file_name):
    return json.load(read_file(file_name))
