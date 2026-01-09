""" Main file setups the command line interface """

import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
api_org = os.getenv("OPENAI_ORG")

from src.flow import DataAnalysisFlow
from src.security import SecurityVerify

# ========================== CLI =======================
def main():
    print("====== 📊 Autonomous AI Data Analysis Agent (Flow Mode) ======\n")

    try:
        # 1 Initialization
        user = input("👤 Step 1: Username: ").strip()
        dataset_name = input("📂 Step 2: Dataset (e.g., chinook.db): ").strip() 
        query = input("💡 Step 3: Analysis Query: \n").strip() 
        
        # 2 Access Check
        print(f"--- Authenticating User: {user} ---")
        is_allowed, access_result = SecurityVerify.verify_access(user, dataset_name)
        if not is_allowed:
            raise PermissionError(f"SECURITY ALERT: {access_result}")       
        print(f"--- Access Granted. Loading {dataset_name}... ---")
        
        
        print("\n🚀 Starting Flow...")
        
        # 3. Initialize flow
        flow = DataAnalysisFlow(user=user, 
                                dataset_name=dataset_name, 
                                dataset_path=access_result, 
                                query=query,
                                api_key=api_key,
                                api_org=api_org)
        
        # 4. Run the flow
        flow.kickoff()
        
        print("\n★ Flow Finished ★")

    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
    
    # user="admin"
    # dataset_name="chinook.db"
    
    # print("\n🚀 Starting Flow...")
    # query="Tell me how many tables in the dataset?"
    # is_allowed, dataset_path = SecurityVerify.verify_access(user, dataset_name)
    # flow = DataAnalysisFlow(user=user, 
    #                         dataset_name=dataset_name, 
    #                         dataset_path = dataset_path,
    #                         query=query,
    #                         api_key=api_key,
    #                         api_org=api_org)
    # flow.kickoff()
    # print("\n★ Flow Finished ★")