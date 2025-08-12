import os
from typing import List, Dict, Any, Optional
from llama_cpp import Llama
from ..base_source import RSSItem


class LLMProcessor:
    """Processes RSS content using a local LLM"""
    
    def __init__(self, model_path: str, query: str, max_tokens: int = 512):
        """
        Initialize the LLM processor
        
        Args:
            model_path: Path to the local LLM model file
            query: The query to search for in content
            max_tokens: Maximum tokens for LLM response
        """
        self.model_path = model_path
        self.query = query
        self.max_tokens = max_tokens
        self.llm = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the local LLM"""
        try:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
            
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=2048,
                n_threads=4,
                verbose=False
            )
            print(f"LLM initialized successfully with model: {self.model_path}")
            
        except Exception as e:
            print(f"Error initializing LLM: {e}")
            self.llm = None
    
    def process_item(self, item: RSSItem) -> Optional[Dict[str, Any]]:
        """
        Process a single RSS item with the LLM
        
        Args:
            item: RSS item to process
            
        Returns:
            Processing result or None if processing failed
        """
        if not self.llm:
            print("LLM not initialized, skipping processing")
            return None
        
        try:
            # Create prompt for the LLM
            prompt = self._create_prompt(item)
            
            # Get LLM response
            response = self.llm(
                prompt,
                max_tokens=self.max_tokens,
                temperature=0.1,
                stop=["\n\n", "###"]
            )
            
            # Extract the generated text
            generated_text = response['choices'][0]['text'].strip()
            
            # Parse the response
            result = self._parse_llm_response(generated_text, item)
            
            return result
            
        except Exception as e:
            print(f"Error processing item '{item.title}': {e}")
            return None
    
    def _create_prompt(self, item: RSSItem) -> str:
        """Create a prompt for the LLM"""
        prompt = f"""### Task: Analyze the following RSS content for relevance to the query: "{self.query}"

### Content:
Title: {item.title}
Description: {item.description}
Content: {item.content[:1000]}...

### Instructions:
1. Determine if this content is relevant to the query: "{self.query}"
2. Provide a relevance score from 0-100 (0 = not relevant, 100 = highly relevant)
3. Explain why it is or isn't relevant
4. Extract any key information related to the query
5. Provide a brief summary

### Response Format:
Relevance Score: [0-100]
Relevance: [Yes/No/Partially]
Explanation: [Brief explanation]
Key Information: [Extracted key points]
Summary: [Brief summary]

### Analysis:"""
        
        return prompt
    
    def _parse_llm_response(self, response: str, item: RSSItem) -> Dict[str, Any]:
        """Parse the LLM response into structured data"""
        try:
            # Extract relevance score
            score_line = [line for line in response.split('\n') if 'Relevance Score:' in line]
            score = 0
            if score_line:
                try:
                    score_text = score_line[0].split(':')[1].strip()
                    score = int(score_text)
                except (ValueError, IndexError):
                    pass
            
            # Extract relevance
            relevance_line = [line for line in response.split('\n') if 'Relevance:' in line]
            relevance = "Unknown"
            if relevance_line:
                try:
                    relevance = relevance_line[0].split(':')[1].strip()
                except IndexError:
                    pass
            
            # Extract explanation
            explanation_line = [line for line in response.split('\n') if 'Explanation:' in line]
            explanation = ""
            if explanation_line:
                try:
                    explanation = explanation_line[0].split(':')[1].strip()
                except IndexError:
                    pass
            
            # Extract key information
            key_info_line = [line for line in response.split('\n') if 'Key Information:' in line]
            key_info = ""
            if key_info_line:
                try:
                    key_info = key_info_line[0].split(':')[1].strip()
                except IndexError:
                    pass
            
            # Extract summary
            summary_line = [line for line in response.split('\n') if 'Summary:' in line]
            summary = ""
            if summary_line:
                try:
                    summary = summary_line[0].split(':')[1].strip()
                except IndexError:
                    pass
            
            return {
                'item_guid': item.guid,
                'item_title': item.title,
                'item_source': item.source,
                'query': self.query,
                'relevance_score': score,
                'relevance': relevance,
                'explanation': explanation,
                'key_information': key_info,
                'summary': summary,
                'llm_response': response,
                'processed_at': item.published.isoformat()
            }
            
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            return {
                'item_guid': item.guid,
                'item_title': item.title,
                'item_source': item.source,
                'query': self.query,
                'relevance_score': 0,
                'relevance': 'Error',
                'explanation': f'Error parsing response: {e}',
                'key_information': '',
                'summary': '',
                'llm_response': response,
                'processed_at': item.published.isoformat()
            }
    
    def process_items(self, items: List[RSSItem]) -> List[Dict[str, Any]]:
        """
        Process multiple RSS items
        
        Args:
            items: List of RSS items to process
            
        Returns:
            List of processing results
        """
        results = []
        for item in items:
            result = self.process_item(item)
            if result:
                results.append(result)
        
        return results 