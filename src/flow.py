""" Create a multi-agent collaboration workflow based on flow from crewai"""

import sys
from typing import List
from pydantic import BaseModel

from crewai_tools import RagTool
from crewai.flow.flow import Flow, listen, start, router, or_
from crewai import Crew


from src.tools import PythonREPLTool, StyleConfigTool
from src.agents import Agents
from src.tasks import TaskFactory


class InteractionRecord(BaseModel):
    """ Storing history interaction """
    # step: int  
    query: str
    result: str

class DataState(BaseModel):
    """ State type check """
    # Basic information
    user: str = ""
    dataset_name: str = "" # dataset name without suffix (i.e. chinook)
    dataset_path: str = "" # path storing the dataset
    result_path: str = "" # path storing the results
    query: str = ""
    
    # Intermediate results
    output: str = "" # output of each run
    history: List[InteractionRecord] = [] # conversation history
    

class DataAnalysisFlow(Flow[DataState]):
    """ 
    Class defining how analysis_agent, visualization_agent and human interact 
    """

    def __init__(self, 
                 user:str, 
                 dataset_name:str, 
                 dataset_path:str, 
                 query:str,
                 api_key:str,
                 api_org:str,
                 agent_verbose:bool = False,
                 crew_verbose:bool = True) -> None:
        super().__init__()
        
        # 1. Class Initialization
        self.state.user = user
        self.state.dataset_name = dataset_name.split(".")[0] 
        self.state.query = query
        self.state.dataset_path = dataset_path 
        
        self.agent_verbose = agent_verbose # whether to display detailed log of agent (default: False)
        self.crew_verbose = crew_verbose # whether to display detailed log of crew (default: True)
        
        # 2. Initialize Agents   
        agents_team = Agents(
            dataset_cleanname=self.state.dataset_name, 
            api_key=api_key, 
            api_org=api_org)
        # - analysis agent
        self.ana_agent = agents_team.create_agent(
            agent_name = "analysis_agent",
            tools=[PythonREPLTool(), RagTool()],
            verbose = self.agent_verbose)
        # - visualization agent
        self.viz_agent = agents_team.create_agent(
            "visualization_agent",
            tools = [PythonREPLTool(), StyleConfigTool()],
            verbose = self.agent_verbose)
        self.state.result_path = agents_team.result_path # path storing the results
        
        # 2 Initialize tasks
        self.tasks_factory = TaskFactory(
            dataset_cleanname=self.state.dataset_name,
            dataset_path=self.state.dataset_path
            )

# =========================== FLOW ===========================

    # --- Flow start ---
    @start()
    def start_flow(self):
        """Flow Entrance"""
        print("\n🔵 [Started] Triggering Data Analysis...")
        return "start_analysis"
    
    # --- [analysis_agent] Analyze data ---
    # Based on query and conversation history
    @listen(or_(start_flow, "analysis"))
    def run_analysis(self):
        print(f"\n🧐 Data Analyst is thinking... (Query: {self.state.query})")
        
        history_str = "\n".join([f"Query: {h.query}\nResult: {h.result}" for h in self.state.history])
        
        crew = Crew(
            agents = [self.ana_agent],
            tasks = [self.tasks_factory.create_task(
                query = self.state.query,
                history = history_str,
                task_name="analysis_task", 
                agent=self.ana_agent)],
                verbose = self.crew_verbose
        )
        
        self.state.output = str(crew.kickoff())
        self.state.history.append(InteractionRecord(query=self.state.query,
                                                result = self.state.output))
        return self.state.output
    
    # --- [visualization_agent] Visualize data ---
    # Based on query and conversation history
    @listen(or_("plot"))
    def run_visualization(self):
        print(f"\n🧑‍🎨 Visualizer is thinking... (Query: {self.state.query})")
        
        history_str = "\n".join([f"Query: {h.query}\nResult: {h.result}" for h in self.state.history])
        
        crew = Crew(
            agents = [self.viz_agent],
            tasks = [self.tasks_factory.create_task(
                query = self.state.query,
                history = history_str,
                task_name="visualization_task", 
                agent=self.viz_agent)],
                verbose = self.crew_verbose
        )
        self.state.output = str(crew.kickoff())
        self.state.history.append(InteractionRecord(query=self.state.query,
                                                result = self.state.output))
        return self.state.output
      
    # --- [human] Review and comment results ---
    # Given the results returned by analysis_agent or visualization_agent,
    # choose whether to 
    #   1.further analysis, 2. further visualize, 3. final report, or 4.quite the system
    @router(or_(run_analysis, run_visualization))
    def review_result(self):
        print("\n" + "="*40)
        print("📊 Analysis Insights:\n")
        print(self.state.output)
        print("="*40 + "\n")
        
        while True:
            print("👉 User Feedback Required:")
            print("  [1] Analysis with query (analysis)")
            print("  [2] Visualization with query (plot)")
            print("  [3] Proceed to final report (report)")
            print("  [q] Quit/Exit system (exit)")
            
            choice = input("Select option (1/analysis/2/plot/3/report): ").strip().lower()

            if choice in ['1', 'analysis']:
                new_query = input("Enter new query: ").strip()
                if new_query:
                    self.state.query = new_query
                return "analysis" 
            
            elif choice in ['2', 'plot']:
                new_query = input("Enter plot query: ").strip()
                if new_query:
                    self.state.query = new_query
                return "plot" 
            
            elif choice in ['3', 'report']:
                new_query = input("Anything want to add to the report? (Enter to skip): ").strip()
                if new_query:
                    self.state.query = new_query
                return "report"

            elif choice in ['q', 'c', 'exit']:
                print("👋 Exiting system. Goodbye!")
                sys.exit(0)

            else:
                print(f"\n❌ Invalid input '{choice}'. please select option (1/analysis/2/plot/3/report).\n")
        
    # --- [analysis_agent] Report ---
    # Based on query and all conversation history
    @listen(or_("report"))
    def run_report(self):
        # if self.state.report_generated:
        #     return self.state.output
        print("\n📝 Generating Final Report...")
        crew = Crew(
            agents = [self.ana_agent],
            tasks = [self.tasks_factory.create_task(
                query = self.state.query,
                history = self.state.history,
                task_name="report_task", 
                agent=self.ana_agent)]
        )
        self.state.output = str(crew.kickoff())
        print(f"\n✅ Report Generated Successfully at {self.state.result_path}")
        return self.state.output
    
    

# ================= CLI =================
def main():
    print("====== 📊 Autonomous AI Data Analysis Agent (Flow Mode) ======\n")

    try:
        user = input("👤 Step 1: Username: ").strip()
        dataset_name = input("📂 Step 2: Dataset (e.g., chinook.db): ").strip() 
        query = input("💡 Step 3: Analysis Query: ").strip() 

        print("\n🚀 Starting Flow...")
        
        # Initialize
        flow = DataAnalysisFlow(user, dataset_name, query)
        flow.kickoff()
        
        print("\n★ Flow Finished ★")

    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\n❌ Error: {e}")