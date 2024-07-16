from enum import StrEnum


class CaseInsensitiveEnum(StrEnum):
    @classmethod
    def _missing_(cls, value):
        value_str = str(value)  # Ensure the value is a string
        for member in cls:
            if member.value.lower() == value_str.lower():
                return member
        raise ValueError(f"{value} is not a valid {cls.__name__}")


class APIType(CaseInsensitiveEnum):
    OTHER = "Other"
    ANTHROPIC = "Anthropic"
    OPENAI = "OpenAI"


class APIModel(CaseInsensitiveEnum): ...


class AnthropicModel(APIModel):
    CLAUDE_3_OPUS_20240229 = "claude-3-opus-20240229"
    CLAUDE_3_HAIKU_20240307 = "claude-3-haiku-20240307"
    CLAUDE_3_5_SONNET_20240620 = "claude-3-5-sonnet-20240620"
    CLAUDE_3_SONNET_20240229 = "claude-3-sonnet-20240229"


class OpenAIModel(APIModel):
    GPT_3_5_TURBO_0125 = "gpt-3.5-turbo-0125"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_3_5_TURBO_INSTRUCT = "gpt-3.5-turbo-instruct"
    GPT_4 = "gpt-4"
    GPT_4O = "gpt-4o"
    GPT_4O_2024_05_13 = "gpt-4o-2024-05-13"
    DAVINCI = "davinci"
    CURIE = "curie"
