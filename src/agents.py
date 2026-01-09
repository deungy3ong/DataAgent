""" Create agents based on configuration using Agent from crewai """

import yaml
import os
from pathlib import Path
from typing import List

from crewai import Agent
from src.tools import PythonREPLTool
from langchain_openai import ChatOpenAI

current_dir = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.dirname(current_dir)
config_path = os.path.join(current_dir, "agent_config.yaml")


class Agents:
    """A class to generate agents based on configuration using Agent from crewai"""
    
    def __init__(self, 
                 dataset_cleanname:str,
                 api_key:str,
                 api_org: str,
                 model: str="gpt-4o",
                 temperature: int = 1.0,
                 config_path: str = config_path) ->None:
        self.dataset_cleanname = dataset_cleanname
        
        # Create the folder to store results if not existing
        self.result_path = root_path + "/results/" + Path(dataset_cleanname).stem.split('.')[0]
        os.makedirs(os.path.join(self.result_path, "images"), exist_ok=True)
        
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                content = file.read()
            self.config = yaml.safe_load(
                content.replace("{result_path}", str(self.result_path)) \
                    .replace("{dataset_name}", str(self.dataset_cleanname))
                    )
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Agent configuration file not found: {self.config_path}") from e
        
        self.model = ChatOpenAI(
            api_key = api_key,
            organization=api_org,
            model = model,
            temperature = temperature,
        )
        
        
    def create_agent(self, 
                     agent_name:str, 
                     verbose:bool = True,
                     tools: List=[PythonREPLTool()]) ->Agent:
        """A general method to create an agent"""
        
        agent_config = self.config.get(agent_name,{})
        if not agent_config:
            raise ValueError(f"Agent '{self.agent_name}' configuration is not found in agent_config.yaml .")
        
        role = agent_config.get("role")
        goal = agent_config.get("goal")
        backstory = agent_config.get("backstory")
        allow_code_execution = agent_config.get("allow_code_execution")
        
        return Agent(
            role = role,
            goal = goal,
            backstory = backstory,
            llm = self.model,
            tools = tools,
            allow_code_execution = allow_code_execution,
            verbose = verbose
        )