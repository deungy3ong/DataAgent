# import os
import sys
from dotenv import load_dotenv
from pydantic import BaseModel
from src.tools import PythonREPLTool, StyleConfigTool
from crewai_tools import RagTool
from crewai.flow.flow import Flow, listen, start, router, or_
from crewai import Crew, Process

from src.security import SecurityVerify
from src.agents import Agents
from src.tasks import TaskFactory

# load_dotenv()

class DataState(BaseModel):
    """ State type check """
    # Basic information
    user: str = ""
    dataset_name: str = ""
    dataset_path: str = "" # Store the dataset
    result_path: str = "" # Store the results
    query: str = ""
    
    # Intermediate results
    analysis_output: str = ""
    viz_output: str = ""
    
    # Additional instructions given to the visualization and analysis by the user.
    analysis_feedback: str = ""
    viz_feedback: str = ""

class DataAnalysisFlow(Flow[DataState]):

    def __init__(self, 
                 user:str, 
                 dataset_name:str, 
                 dataset_path:str, 
                 query:str,
                 api_key:str,
                 api_org:str):
        super().__init__()
        # 0.1 Initialization
        self.state.user = user
        self.state.dataset_name = dataset_name
        self.state.query = query
        
        # # 0.2 Access Check
        # print(f"--- Authenticating User: {user} ---")
        # is_allowed, access_result = SecurityVerify.verify_access(user, dataset_name)
        # if not is_allowed:
        #     raise PermissionError(f"SECURITY ALERT: {access_result}")
        
        self.state.dataset_path = dataset_path # Path of the dataset
        # print(f"--- Access Granted. Loading {dataset_name}... ---")
        
        # 1 Initialize Agents
        
        # api_key = os.getenv("OPENAI_API_KEY")
        # api_org = os.getenv("OPENAI_ORG")    
        self.agents_manager = Agents(self.state.dataset_path, 
                                     api_key, 
                                     api_org)
        self.ana_agent = self.agents_manager.create_agent("analysis_agent")
        self.viz_agent = self.agents_manager.create_agent("visualization_agent",
                                                          tools = [PythonREPLTool(), StyleConfigTool()])
        self.rep_agent = self.agents_manager.create_agent("report_agent",
                                                          tools=[RagTool()])
        
        self.state.result_path = self.agents_manager.result_path # path storing the results
        
        # 2 Initialize tasks
        self.tasks_factory = TaskFactory()
        

    # ================= FLOW =================

    @start()
    def start_flow(self):
        """Flow Entrance"""
        print("\n🔵 [Started] Triggering Data Analysis...")
        return "start_analysis"

    # Step 1: Analysis
    @listen(or_(start_flow, "retry_analysis", "restart_analysis"))
    def run_analysis(self):
        print(f"\n🧐 Analyst is thinking... (Query: {self.state.query})")
        
        task = self.tasks_factory.create_analysis_task(
            self.ana_agent, 
            self.state.query, 
            self.state.dataset_path
        )
        crew = Crew(
            agents=[self.ana_agent], 
            tasks=[task], 
            verbose=True)
        result = crew.kickoff()
        
        self.state.analysis_output = str(result)
        return result

    # Step 2: Review analysis results
    @router(run_analysis)
    def review_analysis(self):
        print("\n" + "="*40)
        print("📊 Analysis Insights:\n")
        print(self.state.analysis_output)
        print("="*40 + "\n")

        print("👉 User Feedback Required:")
        print("  [1] Proceed to Visualization (y)")
        print("  [2] Retry Analysis with new query (retry)")
        choice = input("Select option (1/y/2/retry): ").strip().lower()

        if choice == '2' or choice=='retry':
            new_query = input("Enter new query/instructions: ").strip()
            if new_query:
                self.state.query = new_query
            return "retry_analysis" 
        elif choice == '1' or choice=='y':
            return "proceed_to_viz"
        else:
            raise ValueError(f"❌ Unexpected user input '{choice}', please select option (1/2/3).")

    # Step 3: Visualization
    @listen(or_("proceed_to_viz", "retry_viz"))
    def run_visualization(self):
        print(f"\n🎨 Visualizer is working... (Instructions: {self.state.viz_feedback})")
        
        task = self.tasks_factory.create_visualization_task(
            self.viz_agent, 
            analysis_result=self.state.analysis_output, 
            output_path=self.state.result_path + "/images",
            user_feedback=self.state.viz_feedback 
        )
        crew = Crew(
            agents=[self.viz_agent], 
            tasks=[task], 
            verbose=True)
        result = crew.kickoff()
        
        self.state.viz_output = str(result)
        return result

    # Step 4: Review visualization results
    @router(run_visualization)
    def review_visualization(self):
        print("\n" + "="*40)
        print("🖼️ Visualization Done. Check your 'images' folder.")
        print(self.state.viz_output)
        print("="*40 + "\n")
        
        print("👉 What's next?")
        print("  [1] Generate Final Report (report)")
        print("  [2] Request different plots (new_plots)")
        print("  [3] Redo Analysis (restart)")
        choice = input("Select option (1/report/2/new_plots/3/restart): ").strip().lower()

        if choice == '2' or choice == 'new_plots':
            self.state.viz_feedback = input("Enter instructions for new plots: ").strip()
            return "retry_viz" 
        elif choice == '3' or choice == 'restart':
            new_query = input("Enter new query for analysis: ").strip()
            if new_query:
                self.state.query = new_query
            self.state.viz_feedback = "" 
            return "restart_analysis" 
        elif choice == '1' or choice == 'report':
            return "proceed_to_rep" 
        else:
            raise ValueError(f"❌ Unexpected user input '{choice}', please select option (1/report/2/new_plots/3/restart).")

    # Step 5: Report
    @listen("proceed_to_rep")
    def generate_report(self):
        print("\n📝 Generating Final Report...")
        
        task = self.tasks_factory.create_report_task(
            agent=self.rep_agent,
            query = self.state.query,
            analysis_result=self.state.analysis_output,
            visualization_result=self.state.viz_output,
            dataset_name=self.state.dataset_name
        )
        crew = Crew(agents=[self.rep_agent], tasks=[task], verbose=True)
        result = crew.kickoff()
        
        print(f"\n✅ Report Generated Successfully at {self.state.result_path}")
        return result


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

if __name__ == "__main__":
    # main()
    
    user="admin"
    dataset_name="chinook.db"
    
    print("\n🚀 Starting Flow...")
    query="Analysis the dataset and generate a report."
    flow = DataAnalysisFlow(user, dataset_name, query)
    flow.kickoff()
    print("\n★ Flow Finished ★")