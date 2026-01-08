# Main Workflow
import os
from dotenv import load_dotenv
load_dotenv()

from crewai import Crew, Process

from src.security import SecurityVerify
from src.agents import Agents
from src.tasks import TaskFactory

def data_analysis_pipeline(user:str, 
                           dataset_name: str,
                           query: str):
    print(f"--- Authenticating User: {user} ---")
    
    # 1. Access Check
    is_allowed, result = SecurityVerify.verify_access(user, dataset_name)
    if not is_allowed:
        return f"SECURITY ALERT: {result}"
    
    data_filepath = result
    print(f"--- Access Granted. Loading {dataset_name} from {data_filepath} ---")

    # 2. Initialize Agents
    api_key = os.getenv("OPENAI_API_KEY")
    api_org = os.getenv("OPENAI_ORG")
    agents = Agents(data_filepath, 
                    api_key, 
                    api_org)
    analyst_agent = agents.create_agent(agent_name="analysis_agent")
    viz_agent = agents.create_agent(agent_name="visualization_agent")
    rep_agent = agents.create_agent(agent_name="report_agent")

    # 3. Initialize Tasks
    tasks = TaskFactory()
    analysis_task = tasks.create_analysis_task(analyst_agent, query, data_filepath)
    viz_task = tasks.create_visualization_task(viz_agent, analysis_task, agents.result_path+"/images")
    rep_task = tasks.create_report_task(rep_agent, analysis_task, viz_task, dataset_name.split('.')[0], agents.result_path)
    

    # 4. Create Crew
    crew = Crew(
        agents=[analyst_agent, viz_agent, rep_agent],
        tasks=[analysis_task, viz_task, rep_task],
        process=Process.sequential
    )

    # 5. Execuate
    final_output = crew.kickoff()
    print(f"--- Data analysis finished! ---")
    # return final_output

# =============== CLI =================
import sys
import os

def main():
    print("====== 📊 Autonomous AI Data Analysis Agent Assistant ======\n\n")
    print("Welcome! I will help you with the analysis process:).\n \n \n")

    try:
        # 1. Get arguments
        user = input("👤 Step 1: Please enter your username: ").strip()
        while not user:
            user = input("Username cannot be empty. Please enter: ").strip()

        print(f"\n📂 Step 2: Please enter the dataset name that you want to analysis, e.g. chinook.db.")
        dataset_name = input("Please enter the dataset name: ").strip()
        while not dataset_name:
            dataset_name = input("Dataset name cannot be empty: ").strip()

        print(f"\n💡 Step 3: What would you like to know or visualize?")
        query = input("Enter your analysis query: ").strip()
        while not query:
            query = input("Query cannot be empty: ").strip()

        #  2. Information Check
        print("\n" + "-"*40)
        print(f"Summary of your request:")
        print(f" - User: {user}")
        print(f" - Dataset: {dataset_name}")
        print(f" - Query: {query}")
        print("-"*40 + "\n")

        confirm = input("Confirm and start analysis? (y/n): ").lower()
        if confirm != 'y':
            print("Operation cancelled.")
            return

        # 3. Call agents workflow
        print("\n🚀 Agents are starting to work... please wait.\n")
        result = data_analysis_pipeline(
            user=user, 
            dataset_name=dataset_name, 
            query=query
        )
        
        print("\n" + "★"*30)
        print("Final Result Summary:")
        print(result)
        print("★"*30)

    except KeyboardInterrupt:
        print("\n\nExiting gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")

if __name__ == "__main__":
    # main()
    print(data_analysis_pipeline(
        user="admin", 
        dataset_name="chinook.db", 
        query="Analysis the dataset and generate a report."
    ))