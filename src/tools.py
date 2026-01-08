# Custom Tools
from crewai.tools import BaseTool

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
            # local_scope = {}
            local_scope = {
                "pd": pd, 
                "np": np, 
                "plt": plt, 
                "sns": sns, 
                "sqlite3": sqlite3
            }
            #exec_globals = { "matplotlib": matplotlib, "scipy": scipy, "pandas": pandas, "pd": pd, "np": np, "sns": sns, "plt": plt, "pearsonr":pearsonr} 
            exec(code, globals(), local_scope)  # Execute the code
            result = local_scope.get('result', 'Execution completed.')
            if len(result) > 2000: # Output truncated due to context limits
                return result[:2000] + "\n[Output truncated due to context limits...]"
            return result
            # return str(local_scope.get('result', 'Execution completed.'))
        
        except Exception as e:
            return f"Error executing code: {str(e)}"