""" 
    3 Test cases to test the functionalities and correctness of the Agent

      -  Test 1: Test the Database access permissions
      -  Test 2: Test the custom tool PythonREPLTool's functionalities
      -  Test 3: Test if the agents can return a correct answer

"""

import unittest
from unittest.mock import patch
import os
from src.registry import USER_PERMISSIONS
from src.tools import PythonREPLTool
from src.flow import DataAnalysisFlow

api_key = os.getenv("OPENAI_API_KEY")
api_org = os.getenv("OPENAI_ORG")

class TestAgents(unittest.TestCase):
    """Test functionalities and correctness of Agents"""
    
    
    def testUserRestriction(self):
        print("\n 🩺[Test 1] Testing Database Access Permissions...")
        
        def check_access(user_name, db_name):
            allowed_dbs = USER_PERMISSIONS.get(user_name, [])
            return db_name in allowed_dbs
        
        self.assertTrue(check_access("userC", "chinook.db"), "UserC should access chinook.db")
        self.assertFalse(check_access("userC", "sakila.db"), "UserC should not access sakila.db")
        self.assertFalse(check_access("userN", "sakila.db"), "UserC should not access sakila.db")
        self.assertTrue(check_access("userN", "northwind_small.sqlite"), "UserC should access cnorthwind_small.sqlite")
        self.assertTrue(check_access("userS", "sakila.db"), "UserC should access sakila.db")
        self.assertFalse(check_access("useS", "northwind_small.sqlite"), "UserC should not access northwind_small.sqlite")
        self.assertTrue(check_access("admin", "chinook.db"), "admin should access chinook.db")
        self.assertTrue(check_access("admin", "northwind_small.sqlite"), "admin should access northwind_small.sqlite")
        self.assertTrue(check_access("admin", "sakila.db"), "admin should access sakila.db")
        
        print("   -> ✅Pass [Test 1]: User Restriction logic is secure.")
    
    
    def testPythonREPLTool(self):
        """Test if the python execuation tool executes code successfully"""
        
        
        print("\n 🩺[Test 2] Testing PythonREPLTool...")
        
        tool = PythonREPLTool()
        test_code = """import pandas as pd
df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
print(df['a'].sum() + df['b'].sum())
        """

        result=tool._run(test_code).strip()
        self.assertEqual(result, "10", f"REPL Tool returned unexpected result: {result}")
        
        print("   -> ✅Pass [Test 2]: PythonREPLTool executed code successfully.")
       
       
    @patch('builtins.input', side_effect=['3','']) 
    def testGroundFactAccuracy(self, mock_input):
        print("\n 🩺[Test 3] Testing Ground Fact Accuracy (Chinook.db)...")
        
        query = "Which customer spent the most on album purchases? Only return the first name and last name"
        
        flow = DataAnalysisFlow(user="userC", 
                                dataset_name="chinook", 
                                dataset_path="/Users/deungy3ong/Documents/GitHub/DataAgent/datas/chinook.db", 
                                query=query,
                                api_key=api_key,
                                api_org=api_org,
                                agent_verbose=False,
                                crew_verbose=False)
        
        try:
            output=str(flow.kickoff())
            self.assertIsNotNone(output)
            # # assert file
            # self.assertTrue(os.path.exists(os.path.join(flow.state.result_path, f"chinook.md")))
            self.assertIn("Helena Holý", output)
        except Exception as e:
            self.fail(f"Flow execution failed even with mocked input: {e}")
        
        print("   -> ✅Pass [Test 3]: Flow completed automatically using mock inputs.")
        
if __name__ == '__main__':
    unittest.main()   
        
        
        