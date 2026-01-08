import os

""" Manage the Data access"""

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Dataset Registry
# Add new KV for an easy integration
DATASET_REGISTRY = {
    "chinook.db": os.path.join(BASE_DIR, "datas/chinook.db"),
    "northwind_small.sqlite": os.path.join(BASE_DIR, "datas/northwind_small.sqlite"),
    "sakila.db": os.path.join(BASE_DIR, "datas/sakila.db")
}

# User Restriction
USER_PERMISSIONS = {
    "admin": ["chinook.db", "northwind_small.sqlite", "sakila.db"],
    "userC": ["chinook.db"],
    "userN": ["northwind_small.sqlite"],
    "userS": ["sakila.db"]
}