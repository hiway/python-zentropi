# coding=utf-8
from zentropi import run_agents
from .{{cookiecutter.agent_module_name}} import {{cookiecutter.agent_class_name}}


def main():
    {{cookiecutter.agent_module_name}} = {{cookiecutter.agent_class_name}}(name='{{cookiecutter.agent_name}}')
    run_agents({{cookiecutter.agent_module_name}}, shell=True)
