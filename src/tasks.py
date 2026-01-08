import os
import yaml
from crewai import Task

current_dir = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.dirname(os.path.dirname(current_dir))
config_path = os.path.join(current_dir, "task_config.yaml")

class TaskFactory:
    def __init__(self, 
                 config_path:str = config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                self.config = yaml.safe_load(file)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Task configuration file is not found: {self.config_path}") from e

    def create_analysis_task(self, agent, user_query, dataset_path):
        analysis_config = self.config.get("analysis_task", {})
        if not analysis_config:
            raise ValueError(f"analysis_task configuration is not found in task_config.yaml .")
        
        description = analysis_config.get("description", "").replace("{user_query}", user_query) 
        expected_output = analysis_config.get("expected_output", "").replace("{dataset_path}", dataset_path)
        return Task(
            description=description,
            expected_output=expected_output,
            agent=agent
        )

    def create_visualization_task(self, agent, analysis_task, output_path):
        visualization_config = self.config.get("visualization_task", {})
        if not visualization_config:
            raise ValueError(f"visualization_task configuration is not found in task_config.yaml .")
        
        description = visualization_config.get("description", "").replace("{output_path}", output_path) 
        expected_output = visualization_config.get("expected_output", "")
        return Task(
            description=description,
            expected_output=expected_output,
            agent=agent,
            context=[analysis_task],
            # output_file=output_path
        )

    @staticmethod
    def create_report_task(agent, analysis_task, visualization_task, dataset_name, output_path):
        print(output_path+f"/{dataset_name}.md")
        dataset_name = dataset_name.split('.')[0]
        return Task(
            description=(
                f"1. Review the Statistical Insights from the Analyst (Task 1).\n"
                f"2. Review the Image Paths and Visual Trends from the Visualizer (Task 2).\n"
                "3. Synthesize these into a cohesive Markdown report.\n"
                "4. Embed images using the relative paths provided.\n"
                f"5. Save the final file as '{dataset_name}.md' in the {output_path}."
            ),
            expected_output="A professional Markdown report saved to the disk, confirming the file path.",
            agent=agent,
            context=[analysis_task, visualization_task],
            # output_path = "/Users/deungy3ong/Documents/GitHub/DataAgent/results/chinook/chinook.md"
            output_file=output_path+f"/{dataset_name}.md"
        )