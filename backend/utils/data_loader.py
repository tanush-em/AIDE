"""
Data loader utility for loading data from CSV, Excel, and JSON files
"""
import pandas as pd
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DataLoader:
    """Utility class for loading data from various file formats"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.cache = {}
    
    def load_csv(self, filename: str, cache: bool = True) -> pd.DataFrame:
        """Load data from CSV file"""
        filepath = os.path.join(self.data_dir, filename)
        
        if cache and filename in self.cache:
            return self.cache[filename]
        
        try:
            if not os.path.exists(filepath):
                logger.warning(f"CSV file not found: {filepath}")
                return pd.DataFrame()
            
            df = pd.read_csv(filepath)
            if cache:
                self.cache[filename] = df
            logger.info(f"Loaded CSV file: {filename} with {len(df)} rows")
            return df
        except Exception as e:
            logger.error(f"Error loading CSV file {filename}: {str(e)}")
            return pd.DataFrame()
    
    def load_excel(self, filename: str, sheet_name: str = None, cache: bool = True) -> pd.DataFrame:
        """Load data from Excel file"""
        filepath = os.path.join(self.data_dir, filename)
        cache_key = f"{filename}_{sheet_name}" if sheet_name else filename
        
        if cache and cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            if not os.path.exists(filepath):
                logger.warning(f"Excel file not found: {filepath}")
                return pd.DataFrame()
            
            df = pd.read_excel(filepath, sheet_name=sheet_name)
            if cache:
                self.cache[cache_key] = df
            logger.info(f"Loaded Excel file: {filename} with {len(df)} rows")
            return df
        except Exception as e:
            logger.error(f"Error loading Excel file {filename}: {str(e)}")
            return pd.DataFrame()
    
    def load_json(self, filename: str, cache: bool = True) -> Dict[str, Any]:
        """Load data from JSON file"""
        filepath = os.path.join(self.data_dir, filename)
        
        if cache and filename in self.cache:
            return self.cache[filename]
        
        try:
            if not os.path.exists(filepath):
                logger.warning(f"JSON file not found: {filepath}")
                return {}
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if cache:
                self.cache[filename] = data
            logger.info(f"Loaded JSON file: {filename}")
            return data
        except Exception as e:
            logger.error(f"Error loading JSON file {filename}: {str(e)}")
            return {}
    
    def save_csv(self, filename: str, data: pd.DataFrame) -> bool:
        """Save DataFrame to CSV file"""
        try:
            filepath = os.path.join(self.data_dir, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            data.to_csv(filepath, index=False)
            logger.info(f"Saved CSV file: {filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving CSV file {filename}: {str(e)}")
            return False
    
    def save_json(self, filename: str, data: Dict[str, Any]) -> bool:
        """Save data to JSON file"""
        try:
            filepath = os.path.join(self.data_dir, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved JSON file: {filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving JSON file {filename}: {str(e)}")
            return False
    
    def clear_cache(self):
        """Clear the data cache"""
        self.cache.clear()
        logger.info("Data cache cleared")
    
    def get_file_info(self, filename: str) -> Dict[str, Any]:
        """Get information about a data file"""
        filepath = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(filepath):
            return {"exists": False}
        
        stat = os.stat(filepath)
        return {
            "exists": True,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "extension": os.path.splitext(filename)[1].lower()
        }

# Global data loader instance
data_loader = DataLoader()
