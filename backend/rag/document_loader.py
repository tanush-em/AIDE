import json
import csv
import os
from typing import List, Dict, Any
from pathlib import Path
import pandas as pd

class DocumentLoader:
    """Loads and processes documents from the knowledge base"""
    
    def __init__(self, knowledge_base_path: str):
        self.knowledge_base_path = Path(knowledge_base_path)
        self.supported_formats = ['.txt', '.json', '.csv', '.md']
    
    def load_all_documents(self) -> List[Dict[str, Any]]:
        """Load all documents from the knowledge base"""
        documents = []
        
        for file_path in self.knowledge_base_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                try:
                    doc = self.load_document(file_path)
                    if doc:
                        documents.append(doc)
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
        
        return documents
    
    def load_document(self, file_path: Path) -> Dict[str, Any]:
        """Load a single document based on its file type"""
        suffix = file_path.suffix.lower()
        
        if suffix == '.json':
            return self._load_json(file_path)
        elif suffix == '.csv':
            return self._load_csv(file_path)
        elif suffix == '.txt':
            return self._load_text(file_path)
        elif suffix == '.md':
            return self._load_markdown(file_path)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")
    
    def _load_json(self, file_path: Path) -> Dict[str, Any]:
        """Load JSON document"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Flatten JSON structure for better processing
        content = self._flatten_json(data)
        
        return {
            'source': str(file_path),
            'title': data.get('title', file_path.stem),
            'category': data.get('category', 'general'),
            'content': content,
            'metadata': {
                'file_type': 'json',
                'file_size': file_path.stat().st_size,
                'last_modified': file_path.stat().st_mtime
            }
        }
    
    def _load_csv(self, file_path: Path) -> Dict[str, Any]:
        """Load CSV document"""
        df = pd.read_csv(file_path)
        
        # Convert DataFrame to structured text
        content_lines = []
        for _, row in df.iterrows():
            line_parts = []
            for col, value in row.items():
                if pd.notna(value):
                    line_parts.append(f"{col}: {value}")
            content_lines.append(" | ".join(line_parts))
        
        content = "\n".join(content_lines)
        
        return {
            'source': str(file_path),
            'title': file_path.stem,
            'category': 'data',
            'content': content,
            'metadata': {
                'file_type': 'csv',
                'columns': list(df.columns),
                'rows': len(df),
                'file_size': file_path.stat().st_size,
                'last_modified': file_path.stat().st_mtime
            }
        }
    
    def _load_text(self, file_path: Path) -> Dict[str, Any]:
        """Load text document"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            'source': str(file_path),
            'title': file_path.stem,
            'category': 'text',
            'content': content,
            'metadata': {
                'file_type': 'txt',
                'file_size': file_path.stat().st_size,
                'last_modified': file_path.stat().st_mtime
            }
        }
    
    def _load_markdown(self, file_path: Path) -> Dict[str, Any]:
        """Load markdown document"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            'source': str(file_path),
            'title': file_path.stem,
            'category': 'markdown',
            'content': content,
            'metadata': {
                'file_type': 'md',
                'file_size': file_path.stat().st_size,
                'last_modified': file_path.stat().st_mtime
            }
        }
    
    def _flatten_json(self, obj: Any, prefix: str = '') -> str:
        """Flatten JSON object into readable text"""
        if isinstance(obj, dict):
            lines = []
            for key, value in obj.items():
                current_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, (dict, list)):
                    lines.append(f"{current_key}:")
                    lines.append(self._flatten_json(value, current_key))
                else:
                    lines.append(f"{current_key}: {value}")
            return "\n".join(lines)
        elif isinstance(obj, list):
            lines = []
            for i, item in enumerate(obj):
                current_key = f"{prefix}[{i}]"
                if isinstance(item, (dict, list)):
                    lines.append(f"{current_key}:")
                    lines.append(self._flatten_json(item, current_key))
                else:
                    lines.append(f"{current_key}: {item}")
            return "\n".join(lines)
        else:
            return str(obj)
