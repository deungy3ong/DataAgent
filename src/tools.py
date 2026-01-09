"""Custom tools for agents based on BaseTool from crewai """

import io
import os
import yaml
from contextlib import redirect_stdout

from crewai.tools import BaseTool

current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, "plot_fig.yaml")

class PythonREPLTool(BaseTool):
    """
    Custom tool to execute Python code and return the result.
    """
    name: str = "PythonREPL"
    description: str = (
        "Executes Python code and returns output."
    )
    
    def _run(self, code: str) -> str:
        """
        Runs the provided Python code and returns the output.
        
        Args:
        code (str): Python code to execute.

        Returns:
        str: Output of the executed code or error message.
        """
        try:
            # Use exec for running the code within a safe scope
            # Create a dictionary to store the execution environment
            import sqlite3
            import pandas as pd
            import numpy as np
            import matplotlib.pyplot as plt
            import seaborn as sns
            import statsmodels.api as sm
            from scipy import stats
            local_scope = {
                "pd": pd, 
                "np": np, 
                "plt": plt, 
                "sns": sns, 
                "sqlite3": sqlite3,
                "stats": stats
            }
            stdout_buffer = io.StringIO()
            with redirect_stdout(stdout_buffer):
                exec(code, globals(), local_scope)
            printed_output = stdout_buffer.getvalue().strip()
            result = local_scope.get('result', printed_output)
            
            if not result:
                result = "Execution completed."
            result = str(result)

            # Output truncated due to context limits
            if len(result) > 2000: 
                return result[:2000] + "\n[Output truncated due to context limits...]"
            return result
        
        except Exception as e:
            return f"Error executing code: {str(e)}"
        
class StyleConfigTool(BaseTool):
    """
    Custom tool to get plot arguments configuration.
    """
    name: str = "StyleConfig"
    description: str = (
        "Get corresponding plot parameters configuration from plot_fig.yaml."
        "Input should be one of: 'line', 'bar', 'scatter', 'heatmap', or 'general' (for figsize/dpi). "
        "Returns a dictionary of parameters to be used in matplotlib/seaborn functions."
    )
    
    def _run(self, 
             plot_type: str,
             config_path:str = config_path) -> str:
        """
        Get corresponding plot parameters configuration from plot_fig.yaml.
        
        Args:
        plot_type (str): plot type.

        Returns:
        str: Returns a dictionary of parameters to be used in matplotlib/seaborn functions.
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Plot configuration file not found: {config_path}") from e
        
        styles = config.get("company_style", {})
        
        if plot_type in ['line', 'bar', 'scatter', 'heatmap']:
            basic = styles.get("plot_types", {}).get("basic")
            params = styles.get("plot_types", {}).get(plot_type, {})
            
            return str({"basic": basic, "params": params})
        
        else:
            return f"Error: Unknown chart type '{plot_type}'. Available: line, bar, scatter, heatmap."