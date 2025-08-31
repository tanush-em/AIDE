from .base_agent import BaseAgent
from typing import Dict, Any, List
from ..rag.vector_store import FAISSVectorStore

class KnowledgeRetrievalAgent(BaseAgent):
    """Agent responsible for retrieving relevant knowledge from the vector store"""
    
    def __init__(self, vector_store: FAISSVectorStore):
        super().__init__(
            name="Knowledge Retrieval Agent",
            description="Retrieves relevant documents and information from the knowledge base"
        )
        self.vector_store = vector_store
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve relevant knowledge based on the query"""
        query = input_data.get('query', '')
        query_analysis = input_data.get('query_analysis', {})
        max_results = input_data.get('max_results', 5)
        threshold = input_data.get('threshold', 0.7)
        
        # Perform similarity search
        search_results = self.vector_store.similarity_search(
            query=query,
            k=max_results,
            threshold=threshold
        )
        
        # Process and rank results
        processed_results = self._process_search_results(search_results, query_analysis)
        
        # Determine if we have sufficient information
        sufficiency = self._assess_information_sufficiency(processed_results, query_analysis)
        
        return {
            'query': query,
            'search_results': processed_results,
            'total_results': len(processed_results),
            'information_sufficiency': sufficiency,
            'search_metadata': {
                'max_results_requested': max_results,
                'similarity_threshold': threshold,
                'query_domains': query_analysis.get('domains', []),
                'query_intent': query_analysis.get('intent', '')
            }
        }
    
    def _process_search_results(self, search_results: List[Dict[str, Any]], query_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process and enhance search results"""
        processed_results = []
        
        for result in search_results:
            # Calculate relevance score based on multiple factors
            relevance_score = self._calculate_relevance_score(result, query_analysis)
            
            # Extract key information
            key_info = self._extract_key_information(result['content'], query_analysis)
            
            processed_result = {
                'content': result['content'],
                'metadata': result['metadata'],
                'similarity_score': result['similarity_score'],
                'relevance_score': relevance_score,
                'key_information': key_info,
                'rank': result['rank'],
                'source': result['metadata']['source'],
                'category': result['metadata']['category']
            }
            
            processed_results.append(processed_result)
        
        # Sort by relevance score
        processed_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return processed_results
    
    def _calculate_relevance_score(self, result: Dict[str, Any], query_analysis: Dict[str, Any]) -> float:
        """Calculate a comprehensive relevance score"""
        base_score = result['similarity_score']
        
        # Boost score based on domain match
        query_domains = query_analysis.get('domains', [])
        result_category = result['metadata']['category']
        
        domain_boost = 0.0
        if query_domains and result_category in query_domains:
            domain_boost = 0.2
        
        # Boost score based on content length (prefer more detailed content)
        content_length = len(result['content'])
        length_boost = min(content_length / 1000, 0.1)  # Max 0.1 boost for long content
        
        # Boost score based on recency (if metadata has timestamp)
        recency_boost = 0.0
        if 'last_modified' in result['metadata'].get('original_metadata', {}):
            # Simple recency boost - could be more sophisticated
            recency_boost = 0.05
        
        final_score = base_score + domain_boost + length_boost + recency_boost
        return min(final_score, 1.0)
    
    def _extract_key_information(self, content: str, query_analysis: Dict[str, Any]) -> List[str]:
        """Extract key information from content based on query analysis"""
        key_info = []
        
        # Extract sentences containing query terms
        query_terms = query_analysis.get('entities', {}).get('academic_terms', [])
        sentences = content.split('.')
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(term in sentence_lower for term in query_terms):
                key_info.append(sentence.strip())
        
        # If no specific terms found, extract first few sentences
        if not key_info and sentences:
            key_info = [sent.strip() for sent in sentences[:2] if sent.strip()]
        
        return key_info[:3]  # Limit to 3 key pieces of information
    
    def _assess_information_sufficiency(self, results: List[Dict[str, Any]], query_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess if we have sufficient information to answer the query"""
        if not results:
            return {
                'sufficient': False,
                'reason': 'No relevant documents found',
                'suggestion': 'Try rephrasing your query or ask about a different topic'
            }
        
        # Check if we have high-quality results
        high_quality_results = [r for r in results if r['relevance_score'] > 0.8]
        
        if len(high_quality_results) >= 2:
            return {
                'sufficient': True,
                'reason': f'Found {len(high_quality_results)} high-quality relevant documents',
                'confidence': 'high'
            }
        elif len(results) >= 2:
            return {
                'sufficient': True,
                'reason': f'Found {len(results)} relevant documents',
                'confidence': 'medium'
            }
        else:
            return {
                'sufficient': False,
                'reason': 'Limited relevant information found',
                'suggestion': 'Consider asking a more specific question or check if the topic is covered in our knowledge base'
            }
