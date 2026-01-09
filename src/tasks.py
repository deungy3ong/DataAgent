""" Custom tasks based on Task from crewai """

import os
import yaml

from crewai import Task

from src.agents import Agents

current_dir = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.dirname(current_dir)

config_path = os.path.join(current_dir, "task_config.yaml")
result_path = os.path.join(root_path, "results")

class TaskFactory:
    def __init__(self,
                 dataset_cleanname:str,
                 dataset_path:str,
                 result_path:str=result_path,
                 config_path:str = config_path):
        self.dataset_cleanname = dataset_cleanname # Name without suffix
        self.dataset_path = dataset_path
        self.result_path = result_path
        
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                content = file.read()
            self.config = yaml.safe_load(
                content.replace("{result_path}", result_path) \
                    .replace("{dataset_name}", self.dataset_cleanname)\
                    .replace("{dataset_path}", dataset_path)
                    )
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Task configuration file not found: {self.config_path}") from e
        
    def create_task(self,
                    agent: Agents,
                    query: str,
                    history: str,
                    task_name: str) -> Task:
        """ General functions to create a task for agent """
        
        task_config = self.config.get(task_name,{})
        if not task_config:
            raise ValueError(f"Task '{self.task_name}' configuration is not found in task_config.yaml .")
        description = task_config.get("description", "").format(
            dataset_path = self.dataset_path,
            user_query = query,
            context = history
        )
        expected_output = task_config.get("expected_output", "")
        output_file = task_config.get("output_path", "").format(
            dataset_name = self.dataset_cleanname
        )
        
        return Task(
            description = description,
            agent = agent,
            expected_output = expected_output,
            output_file = output_file
        )