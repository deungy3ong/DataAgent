# Access Verify
import os
from src.registry import DATASET_REGISTRY, USER_PERMISSIONS

class SecurityVerify:

    @staticmethod
    def verify_access(username, dataset_name):
        """Unified access control entry point"""
        allowed_datasets = USER_PERMISSIONS.get(username, [])
        if not allowed_datasets:
            return False, f"User {username} is not open for any dataset."
        
        if dataset_name in allowed_datasets:
            return True, DATASET_REGISTRY.get(dataset_name)
        return False, f"Dataset {dataset_name} is not accessed."
