import os
from pathlib import Path
import yaml
from crewai import Task

current_dir = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.dirname(current_dir)
# print(root_path)
# print(os.path.dirname(current_dir))
# print(os.path.join(os.path.dirname(current_dir), "results/task_config.yaml"))

config_path = os.path.join(current_dir, "task_config.yaml")
result_path = os.path.join(root_path, "results")
# print(f"config_path: {config_path}")
# print(f"result_path: {result_path}")
dataset_name="dino"
print(os.path.join(result_path, f"{dataset_name}.md"))
class TaskFactory:
    def __init__(self, 
                 config_path:str = config_path,
                 result_path:str = result_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                self.config = yaml.safe_load(file)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Task configuration file is not found: {self.config_path}") from e
        
        self.result_path = result_path

    def create_analysis_task(self, agent, 
                             user_query:str,
                             dataset_path:str):
        analysis_config = self.config.get("analysis_task", {})
        if not analysis_config:
            raise ValueError(f"analysis_task configuration is not found in task_config.yaml .")
        
        description = analysis_config.get("description", "").replace("{user_query}", user_query) \
                                                            .replace("{dataset_path}", dataset_path)
        expected_output = analysis_config.get("expected_output", "")

        return Task(
            description=description,
            expected_output=expected_output,
            agent=agent
        )

    def create_visualization_task(self, 
                                  agent, 
                                  analysis_result:str, 
                                  output_path:str,
                                  user_feedback: str = ""):
        visualization_config = self.config.get("visualization_task", {})
        if not visualization_config:
            raise ValueError(f"visualization_task configuration is not found in task_config.yaml .")
        
        description = visualization_config.get("description", "").replace("{output_path}", output_path) 
        expected_output = visualization_config.get("expected_output", "")
        return Task(
            description=(
                f"{description}\n\n"
                f"--- CONTEXT FROM ANALYST ---\n{analysis_result}\n"
                f"--- USER FEEDBACK/INSTRUCTIONS ---\n{user_feedback}"
            ),
            expected_output=expected_output,
            agent=agent,
            # context=[analysis_result],
            # output_file=output_path
        )

    def create_report_task(self, agent, 
                           query,
                           analysis_result, 
                           visualization_result, 
                           dataset_name):
        report_config = self.config.get("report_task", {})
        if not report_config:
            raise ValueError(f"report_task configuration is not found in task_config.yaml .")
        dataset_name = dataset_name.split('.')[0]
        
        description = report_config.get("description", "").replace("{dataset_name}", dataset_name) \
                                                        .replace("{output_path}", self.result_path)
        expected_output = report_config.get("expected_output", "")
        
        return Task(
            description=(
                f"{description}\n\n"
                f"--- CONTEXT FROM ANALYST ---\n{analysis_result}\n"
                f"--- CONTEXT FROM Visualizer ---\n{visualization_result}"
                f"--- CONTEXT FROM User Query ---\n{query}"
            ),
            expected_output=expected_output,
            agent=agent,
            # output_path=os.path.join(self.result_path, f"{dataset_name}.md")
            # context=[analysis_result, visualization_result],
            output_file=f"./results/{dataset_name}/{dataset_name}.md"
        )