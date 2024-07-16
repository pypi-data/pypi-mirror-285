# QRev Instructor

QRev Instructor is a Python wrapper around the [`instructor`](https://github.com/jxnl/instructor) module, providing a unified interface for working with different language models from OpenAI and Anthropic.

## Features

- Supports both OpenAI and Anthropic models
- Easy-to-use client initialization
- Automatic model type detection
- Case-insensitive enum handling
- Extensible for other API types

## Installation

To install QRev Instructor, use pip:

```pip install qrev-instructor```

For Anthropic (Claude models)

```pip install qrev-instructor[anthropic]```

## Usage

Here's a basic example of how to use QRev Instructor:

```python
from qrev_instructor import get_client
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

model_name="gpt-3.5-turbo" # for OpenAI
# model_name="claude-3-haiku-20240307" # uncomment for Anthropic

# Initialize the client
client = get_client(model=model_name)

# Use the client to create a response
response = client.messages.create(
    model=model_name,
    messages=[
        {
            "role": "user",
            "content": "Jason is 25 years old.",
        }
    ],
    response_model=User
)

print(f"Name: {response.name}, Age: {response.age}")
# prints "Name: Jason, Age: 25"
```

## Supported Models

### Anthropic Models:
- CLAUDE_3_OPUS_20240229 = "claude-3-opus-20240229"
- CLAUDE_3_HAIKU_20240307 = "claude-3-haiku-20240307"
- CLAUDE_3_5_SONNET_20240620 = "claude-3-5-sonnet-20240620"
- CLAUDE_3_SONNET_20240229 = "claude-3-sonnet-20240229"

### OpenAI Models:
- GPT_3_5_TURBO_0125 = "gpt-3.5-turbo-0125"
- GPT_3_5_TURBO = "gpt-3.5-turbo"
- GPT_3_5_TURBO_INSTRUCT = "gpt-3.5-turbo-instruct"
- GPT_4 = "gpt-4"
- GPT_4O = "gpt-4o"
- GPT_4O_2024_05_13 = "gpt-4o-2024-05-13"
- DAVINCI = "davinci"
- CURIE = "curie"

## Testing

The package includes pytest-based tests for both OpenAI and Anthropic clients. To run the tests:

```make test```

## Dependencies

- `instructor`
- `anthropic` (optional, for Anthropic models)
- `pydantic`
