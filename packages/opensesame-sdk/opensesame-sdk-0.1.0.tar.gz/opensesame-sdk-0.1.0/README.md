# OpenSesame OpenAI

OpenSesame OpenAI is a custom OpenAI client that integrates with the OpenSesame service for evaluating AI responses.

## Installation

You can install the OpenSesame OpenAI package using pip:

```
pip install opensesame-openai
```

## Usage

Here's a quick example of how to use the OpenSesame OpenAI client:

```python
from opensesame_openai import OpenSesame

client = OpenSesame(
    api_key="your-openai-api-key",
    open_sesame_key="your-opensesame-key",
    project_name="your-project-name",
    ground_truth="",
    context=""
)

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "Hello, how are you?"}
    ]
)

print(response.choices[0].message.content)
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.