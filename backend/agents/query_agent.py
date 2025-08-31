import sys
import os
from typing import Dict, Any
import re

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent

class QueryUnderstandingAgent(BaseAgent):
    """Agent responsible for understanding and analyzing user queries"""
    
    def __init__(self):
        super().__init__(
            name="Query Understanding Agent",
            description="Analyzes user queries to understand intent and extract key information"
        )
        self.academic_keywords = {
            'attendance': ['attendance', 'present', 'absent', 'mark', 'record'],
            'leave': ['leave', 'vacation', 'sick', 'personal', 'emergency', 'request'],
            'events': ['event', 'meeting', 'seminar', 'workshop', 'conference', 'schedule'],
            'grades': ['grade', 'score', 'mark', 'result', 'performance', 'evaluation'],
            'procedures': ['procedure', 'process', 'step', 'how to', 'guide', 'instruction'],
            'rules': ['rule', 'policy', 'regulation', 'requirement', 'standard']
        }
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and analyze the user query"""
        query = input_data.get('query', '').lower()
        
        # Extract query intent
        intent = self._extract_intent(query)
        
        # Identify relevant domains
        domains = self._identify_domains(query)
        
        # Extract key entities
        entities = self._extract_entities(query)
        
        # Determine query complexity
        complexity = self._assess_complexity(query)
        
        return {
            'original_query': input_data.get('query', ''),
            'intent': intent,
            'domains': domains,
            'entities': entities,
            'complexity': complexity,
            'processed_query': query,
            'confidence': self._calculate_confidence(query, domains)
        }
    
    def _extract_intent(self, query: str) -> str:
        """Extract the primary intent of the query"""
        intent_patterns = {
            'information_request': ['what', 'how', 'when', 'where', 'why', 'tell me', 'explain'],
            'procedure_request': ['how to', 'steps', 'process', 'procedure'],
            'status_check': ['status', 'check', 'verify', 'confirm'],
            'rule_inquiry': ['rule', 'policy', 'requirement', 'allowed', 'permitted'],
            'help_request': ['help', 'assist', 'support', 'guide']
        }
        
        for intent, patterns in intent_patterns.items():
            if any(pattern in query for pattern in patterns):
                return intent
        
        return 'general_inquiry'
    
    def _identify_domains(self, query: str) -> list:
        """Identify relevant academic domains"""
        domains = []
        
        for domain, keywords in self.academic_keywords.items():
            if any(keyword in query for keyword in keywords):
                domains.append(domain)
        
        return domains if domains else ['general']
    
    def _extract_entities(self, query: str) -> Dict[str, Any]:
        """Extract key entities from the query"""
        entities = {
            'time_mentions': [],
            'numeric_values': [],
            'academic_terms': []
        }
        
        # Extract time mentions
        time_patterns = [
            r'\d+\s*(days?|weeks?|months?|years?)',
            r'(today|tomorrow|yesterday|next|last)',
            r'\d{1,2}:\d{2}\s*(am|pm)?'
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, query)
            entities['time_mentions'].extend(matches)
        
        # Extract numeric values
        numeric_matches = re.findall(r'\d+', query)
        entities['numeric_values'] = [int(match) for match in numeric_matches]
        
        # Extract academic terms
        academic_terms = []
        for domain_keywords in self.academic_keywords.values():
            for keyword in domain_keywords:
                if keyword in query:
                    academic_terms.append(keyword)
        
        entities['academic_terms'] = list(set(academic_terms))
        
        return entities
    
    def _assess_complexity(self, query: str) -> str:
        """Assess the complexity of the query"""
        word_count = len(query.split())
        
        if word_count < 5:
            return 'simple'
        elif word_count < 15:
            return 'moderate'
        else:
            return 'complex'
    
    def _calculate_confidence(self, query: str, domains: list) -> float:
        """Calculate confidence in understanding the query"""
        base_confidence = 0.5
        
        # Increase confidence based on domain identification
        if domains and domains != ['general']:
            base_confidence += 0.3
        
        # Increase confidence based on query length
        if len(query.split()) >= 3:
            base_confidence += 0.1
        
        # Increase confidence if academic terms are found
        academic_terms_found = sum(1 for domain_keywords in self.academic_keywords.values() 
                                 for keyword in domain_keywords if keyword in query)
        if academic_terms_found > 0:
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
