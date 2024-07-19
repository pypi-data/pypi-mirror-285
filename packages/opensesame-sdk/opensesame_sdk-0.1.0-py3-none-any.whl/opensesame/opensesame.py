import openai
import requests
import json
from typing import Dict, Any, List, Union

class OpenSesame(openai.OpenAI):
    def __init__(self, config: Dict[str, Any]):
        openai_config = {k: v for k, v in config.items() if k in ['api_key', 'organization']}
        super().__init__(**openai_config)
        
        self._api_key = config['api_key']
        self._open_sesame_key = config['open_sesame_key']
        self._project_name = config['project_name']
        self._ground_truth = config.get('ground_truth', '')
        self._context = config.get('context', '')

        print("OpenSesame constructor called")
        self._monkey_patch_methods()

    def _monkey_patch_methods(self):
        print("monkey_patch_methods called")
        original_create = self.chat.completions.create
        
        def new_create(messages: List[Dict[str, str]], **kwargs):
            print("chat.completions.create called")
            self._log_chat_completion_query(messages, **kwargs)

            result = original_create(messages=messages, **kwargs)
            
            if isinstance(result, openai.types.chat.ChatCompletion):
                self._log_chat_completion_answer(result)
                prompt = next((msg['content'] for msg in messages if msg['role'] == 'user'), None)
                answer = result.choices[0].message.content

                print('Prompt:', prompt)
                print('Answer:', answer)

                try:
                    print('Sending request to:', 'https://app.opensesame.dev/api/newEvaluate')
                    print('Request body:', json.dumps({
                        'openSesameKey': self._open_sesame_key,
                        'prompt': prompt,
                        'answer': answer,
                        'projectName': self._project_name,
                        'groundTruth': self._ground_truth,
                        'context': self._context
                        
                    }))

                    response = requests.post(
                        'https://app.opensesame.dev/api/newEvaluate',
                        headers={
                            'Content-Type': 'application/json',
                            'Authorization': self._open_sesame_key
                        },
                        json={
                            'prompt': prompt,
                            'answer': answer,
                            'projectName': self._project_name,
                            'groundTruth': self._ground_truth,
                            'context': self._context
                        }
                    )

                    response.raise_for_status()
                    data = response.json()
                    print('Evaluation:', data)
                except requests.RequestException as error:
                    print('Error in API call:', error)
                    if error.response:
                        print('Error response:', error.response.text)

            return result

        self.chat.completions.create = new_create

    def _log_chat_completion_query(self, messages: List[Dict[str, str]], **kwargs):
        print('OpenAI Query:')
        print('Model:', kwargs.get('model', 'Not specified'))
        print('Messages:')
        last_user_message = next((msg for msg in reversed(messages) if msg['role'] == 'user'), None)

        if last_user_message:
            print('Last User Query:')
            print(f"  {last_user_message['content']}")
        else:
            print('No user query found in the messages.')

        if 'temperature' in kwargs:
            print('Temperature:', kwargs['temperature'])
        if 'max_tokens' in kwargs:
            print('Max Tokens:', kwargs['max_tokens'])
        print('---')

    def _log_chat_completion_answer(self, result: openai.types.chat.ChatCompletion):
        print('LLM Answer:')
        for i, choice in enumerate(result.choices, 1):
            print(f"Choice {i}:")
            print(f"  Role: {choice.message.role}")
            print(f"  Content: {choice.message.content}")
        print('---')