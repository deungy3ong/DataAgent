# Access Verify
import os

class SecurityVerify:
    # Basic path configuration
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    RESULT_PATH = os.path.join(BASE_DIR, "output_reports")
    
    # Dataset Registry
    # Add new KV for an easy integration
    DATASET_REGISTRY = {
        "chinook.db": os.path.join(BASE_DIR, "datas/chinook.db"),
        "northwind_small.sqlite": os.path.join(BASE_DIR, "datas/northwind_small.sqlite"),
        "datas/sakila.db": os.path.join(BASE_DIR, "datas/sakila.db")
    }

    # User Restriction
    USER_PERMISSIONS = {
        "admin": ["chinook.db", "northwind_small.sqlite", "datas/sakila.db"],
        "userC": ["chinook.db"],
        "userN": ["northwind_small.sqlite"],
        "userS": ["datas/sakila.db"]
    }

    @classmethod
    def verify_access(cls, username, dataset_name):
        """Unified access control entry point"""
        allowed_datasets = cls.USER_PERMISSIONS.get(username, [])
        if not allowed_datasets:
            return False, f"User {username} is not open for any dataset."
        
        if dataset_name in allowed_datasets:
            return True, cls.DATASET_REGISTRY.get(dataset_name)
        return False, f"Dataset {dataset_name} is not accessed."

# # Dataset Registry
# # Add new KV for an easy integration
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# DATASET_REGISTRY = {
#     "chinook_data": os.path.join(BASE_DIR, "datas/chinook.db"),
#     "northwind_small_data": os.path.join(BASE_DIR, "datas/northwind_small.sqlite"),
#     "sakila_sample_data": os.path.join(BASE_DIR, "datas/sakila.db")
# }

# # User Restriction
# USER_PERMISSIONS = {
#     "admin": ["chinook_data", "northwind_small_data", "sakila_sample_data"],
#     "userC": ["chinook_data"],
#     "userN": ["northwind_small_data"],
#     "userS": ["sakila_sample_data"]
# }

# class SecurityVerify:
#     @staticmethod
#     def verify_access(username: str, dataset_full_name: str) -> tuple[bool, str]:
#         """检查用户是否有权访问特定数据集"""
#         if dataset_full_name not in DATASET_REGISTRY:
#             return False, f"Error: Dataset '{dataset_full_name}' does not exist."
        
#         allowed_dbs = USER_PERMISSIONS.get(username, [])
#         if dataset_full_name in allowed_dbs:
#             return True, DATASET_REGISTRY[dataset_full_name]
        
#         return False, f"Access Denied: User '{username}' acts on '{dataset_full_name}'."

#     @staticmethod
#     def get_company_style_config():
#         """定义统一的公司绘图风格"""
#         return {
#             "style": "seaborn-v0_8-whitegrid",
#             "palette": "deep",
#             "font": "sans-serif",
#             "context": "talk" 
#         }