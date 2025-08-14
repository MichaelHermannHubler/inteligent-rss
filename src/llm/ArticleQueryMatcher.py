
from vllm import LLM
from vllm.sampling_params import SamplingParams

class ArticleQueryMatcher:
    def __init__(self, model_name="mistralai/Mistral-7B-v0.1"):
        """
        Initialize the model and tokenizer.
        """
        
        self.model_name = model_name

        self.sampling_params = SamplingParams(max_tokens=4096)

        # note that running Ministral 8B on a single GPU requires 24 GB of GPU RAM
        # If you want to divide the GPU requirement over multiple devices, please add *e.g.* `tensor_parallel=2`
        #self.llm = LLM(model=model_name, tokenizer_mode="mistral", config_format="mistral", load_format="mistral")
        self.llm = LLM(model="microsoft/Phi-3-mini-128k-instruct", gpu_memory_utilization=0.9, max_model_len=4096)


    def check_match(self, article_text: str, query: str) -> bool:
        """
        Check if the article text matches the query using the model.

        Args:
            article_text (str): The text from the news article.
            query (str): The query to match against the article.
            max_length (int): Maximum length of the input tokens.

        Returns:
            bool: True if the article text matches the query, False otherwise.
        """
        # Combine article and query into a single prompt
        prompt = f"Does the following article text answer or relate to the query?\n\nArticle: {article_text}\n\nQuery: {query}\n\nAnswer only with 'Yes' or 'No':"

        messages = [
            {
                "role": "user",
                "content": prompt
            },
        ]

        outputs = self.llm.chat(messages, sampling_params=self.sampling_params)

        # Check if the response indicates a match
        return "Yes" in outputs[0].outputs[0].text
    