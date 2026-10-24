import json
import re
from typing import Dict, List

import openai
from config import Config


class LLMError(Exception):
    """
    Raised when the LLM provider fails or returns an unusable response.
    The message is meant for the server log, not for the UI.
    """


def parse_json_response(text: str) -> Dict:
    """
    Parses a JSON object from a model response, ignoring ``` fences and any text around it.
    """
    content = text.strip()
    if content.startswith('```json'):
        content = content[7:]
    if content.startswith('```'):
        content = content[3:]
    if content.endswith('```'):
        content = content[:-3]
    content = content.strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # Smaller models often add text before or after the JSON
    match = re.search(r'\{.*\}', content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    raise LLMError(f'Model response is not valid JSON: {text[:200]}')


class LLMClient:
    """
    Chat client for any OpenAI-compatible API, configured per task in .env (see Config.llm_settings).
    """

    def __init__(self, task: str):
        settings = Config.llm_settings(task)
        self.task = task
        self.model = settings['model']
        self.base_url = settings['base_url']
        self.client = openai.OpenAI(
            base_url=self.base_url,
            # Local servers such as Ollama do not need a key, but the SDK requires one
            api_key=settings['api_key'] or 'not-needed',
            timeout=settings['timeout'],
            max_retries=0
        )

    def chat(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = None) -> str:
        options = {'max_tokens': max_tokens} if max_tokens else {}
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                **options
            )
        except openai.OpenAIError as e:
            raise LLMError(f'{self.task} LLM call failed ({self.model} at {self.base_url}): {e}') from e

        content = response.choices[0].message.content if response.choices else None
        if not content:
            raise LLMError(f'{self.task} LLM returned an empty response ({self.model} at {self.base_url})')
        return content

    def chat_json(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = None) -> Dict:
        return parse_json_response(self.chat(messages, temperature, max_tokens))
