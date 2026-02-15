import yaml
from typing import Dict
from pathlib import Path


class PromptLoader:
    """Loads LLM prompts from YAML configuration."""
    
    def __init__(self, prompts_path: str = "config/prompts.yaml"):
        self.prompts_path = Path(prompts_path)
        self.prompts = self._load_prompts()
    
    def _load_prompts(self) -> Dict[str, str]:
        """Load prompts from YAML file."""
        try:
            with open(self.prompts_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file) or {}
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompts file not found: {self.prompts_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML prompts configuration: {e}")
    
    def get_prompt(self, prompt_name: str) -> str:
        """Get a specific prompt by name."""
        prompt = self.prompts.get(prompt_name)
        if not prompt:
            raise ValueError(f"Prompt not found: {prompt_name}")
        return prompt
    
    def reload(self) -> None:
        """Reload prompts from file."""
        self.prompts = self._load_prompts()
