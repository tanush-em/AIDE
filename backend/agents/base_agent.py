from abc import ABC, abstractmethod
from typing import Dict, Any, List
import asyncio
import time

class BaseAgent(ABC):
    """Base class for all RAG agents"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.status = "idle"
        self.last_execution_time = None
        self.execution_count = 0
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return results"""
        pass
    
    def update_status(self, status: str):
        """Update agent status"""
        self.status = status
    
    def record_execution(self):
        """Record execution statistics"""
        self.last_execution_time = time.time()
        self.execution_count += 1
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status information"""
        return {
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'last_execution_time': self.last_execution_time,
            'execution_count': self.execution_count
        }
    
    async def execute_with_status(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent with status tracking"""
        try:
            self.update_status("processing")
            result = await self.process(input_data)
            self.update_status("completed")
            self.record_execution()
            return result
        except Exception as e:
            self.update_status("error")
            raise e
