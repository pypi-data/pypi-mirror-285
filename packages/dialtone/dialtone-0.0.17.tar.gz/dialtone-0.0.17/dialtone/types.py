import sys
from enum import StrEnum
from pydantic import BaseModel
from typing import Literal, Any, Optional


class Tool(BaseModel):
    type: Literal["function"]
    function: dict[str, Any]


class ToolCallFunction(BaseModel):
    name: str
    arguments: str


class ToolCall(BaseModel):
    id: str
    type: Literal["function"]
    function: ToolCallFunction


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    tool_calls: list[ToolCall] = []
    tool_call_id: Optional[str] = None
    name: Optional[str] = None


class Provider(StrEnum):
    OpenAI = "openai"
    Groq = "groq"
    DeepInfra = "deepinfra"
    Fireworks = "fireworks"
    Together = "together"
    Replicate = "replicate"
    Anthropic = "anthropic"
    Google = "google"
    Cohere = "cohere"

    def __str__(self):
        return self.value


class LLM(StrEnum):
    claude_3_opus = "claude-3-opus-20240229"
    claude_3_5_sonnet = "claude-3-5-sonnet-20240620"
    claude_3_haiku = "claude-3-haiku-20240307"
    gpt_4o = "gpt-4o-2024-05-13"
    gpt_3_5_turbo = "gpt-3.5-turbo-0125"
    gemini_1_5_pro = "gemini-1.5-pro"
    gemini_1_5_flash = "gemini-1.5-flash"
    command_r_plus = "command-r-plus"
    command_r = "command-r"
    llama_3_70b = "llama3-70b-8192"

    def __str__(self):
        return self.value


class Choice(BaseModel):
    model: LLM
    provider: Provider
    message: ChatMessage


class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatCompletion(BaseModel):
    choices: list[Choice]
    usage: TokenUsage


class OpenAIConfig(BaseModel):
    api_key: str


class AnthropicConfig(BaseModel):
    api_key: str


class GoogleConfig(BaseModel):
    api_key: str


class CohereConfig(BaseModel):
    api_key: str


class GroqConfig(BaseModel):
    api_key: str


class ReplicateConfig(BaseModel):
    api_key: str


class FireworksConfig(BaseModel):
    api_key: str


class TogetherConfig(BaseModel):
    api_key: str


class DeepInfraConfig(BaseModel):
    api_key: str


class OpenAIModelConfig(BaseModel):
    providers: list[Provider] = []


class AnthropicModelConfig(BaseModel):
    providers: list[Provider] = []


class GoogleModelConfig(BaseModel):
    providers: list[Provider] = []


class CohereModelConfig(BaseModel):
    providers: list[Provider] = []


class Llama370BModelConfig(BaseModel):
    tools_providers: list[Provider] = []
    no_tools_providers: list[Provider] = []


class ProviderConfig(BaseModel):
    openai: Optional[OpenAIConfig] = None
    anthropic: Optional[AnthropicConfig] = None
    google: Optional[GoogleConfig] = None
    cohere: Optional[CohereConfig] = None
    groq: Optional[GroqConfig] = None
    replicate: Optional[ReplicateConfig] = None
    fireworks: Optional[FireworksConfig] = None
    together: Optional[TogetherConfig] = None
    deepinfra: Optional[DeepInfraConfig] = None

    @classmethod
    def OpenAI(cls, api_key: str) -> OpenAIConfig:
        return OpenAIConfig(api_key=api_key)

    @classmethod
    def Anthropic(cls, api_key: str) -> AnthropicConfig:
        return AnthropicConfig(api_key=api_key)

    @classmethod
    def Google(cls, api_key: str) -> GoogleConfig:
        return GoogleConfig(api_key=api_key)

    @classmethod
    def Cohere(cls, api_key: str) -> CohereConfig:
        return CohereConfig(api_key=api_key)

    @classmethod
    def Groq(cls, api_key: str) -> GroqConfig:
        return GroqConfig(api_key=api_key)

    @classmethod
    def Replicate(cls, api_key: str) -> ReplicateConfig:
        return ReplicateConfig(api_key=api_key)

    @classmethod
    def Fireworks(cls, api_key: str) -> FireworksConfig:
        return FireworksConfig(api_key=api_key)

    @classmethod
    def Together(cls, api_key: str) -> TogetherConfig:
        return TogetherConfig(api_key=api_key)

    @classmethod
    def DeepInfra(cls, api_key: str) -> DeepInfraConfig:
        return DeepInfraConfig(api_key=api_key)


class RouterModelConfig(BaseModel):
    include_models: Optional[list[LLM | str]] = None
    exclude_models: Optional[list[LLM | str]] = None

    gpt_4o: Optional[OpenAIModelConfig] = OpenAIModelConfig(providers=[Provider.OpenAI])
    gpt_3_5_turbo: Optional[OpenAIModelConfig] = OpenAIModelConfig(
        providers=[Provider.OpenAI]
    )
    llama_3_70b: Optional[Llama370BModelConfig] = Llama370BModelConfig(
        tools_providers=[Provider.Groq, Provider.DeepInfra],
        no_tools_providers=[
            Provider.Groq,
            Provider.Fireworks,
            Provider.Together,
            Provider.DeepInfra,
            Provider.Replicate,
        ],
    )
    claude_3_opus: Optional[AnthropicModelConfig] = AnthropicModelConfig(
        providers=[Provider.Anthropic]
    )
    claude_3_haiku: Optional[AnthropicModelConfig] = AnthropicModelConfig(
        providers=[Provider.Anthropic]
    )
    gemini_1_5_pro: Optional[GoogleModelConfig] = GoogleModelConfig(
        providers=[Provider.Google]
    )
    gemini_1_5_flash: Optional[GoogleModelConfig] = GoogleModelConfig(
        providers=[Provider.Google]
    )
    command_r_plus: Optional[CohereModelConfig] = CohereModelConfig(
        providers=[Provider.Cohere]
    )
    command_r: Optional[CohereModelConfig] = CohereModelConfig(
        providers=[Provider.Cohere]
    )

    @classmethod
    def OpenAI(cls, providers: list[Provider] = []) -> OpenAIModelConfig:
        return OpenAIModelConfig(providers=providers)

    @classmethod
    def Anthropic(cls, providers: list[Provider] = []) -> AnthropicModelConfig:
        return AnthropicModelConfig(providers=providers)

    @classmethod
    def Google(cls, providers: list[Provider] = []) -> GoogleModelConfig:
        return GoogleModelConfig(providers=providers)

    @classmethod
    def Cohere(cls, providers: list[Provider] = []) -> CohereModelConfig:
        return CohereModelConfig(providers=providers)

    @classmethod
    def Llama370B(
        cls,
        tools_providers: list[Provider] = [],
        no_tools_providers: list[Provider] = [],
    ) -> Llama370BModelConfig:
        return Llama370BModelConfig(
            tools_providers=tools_providers, no_tools_providers=no_tools_providers
        )


class FallbackConfig(BaseModel):
    # By default just fall back through models recommended by the router from best to worst.
    fallback_model: Optional[LLM] = None

    # By default don't fall back at all and only try the top model recommended by the router.
    max_model_fallback_attempts: int = 0

    # By default use all available providers until a successful response is received.
    max_provider_fallback_attempts: int = sys.maxsize


class ToolsConfig(BaseModel):
    # By default assume no parallel tool use
    parallel_tool_use: bool = False


class Dials(BaseModel):
    quality: float = 0.5
    cost: float = 0.5
    speed: Optional[float] = None

    def sum_to_one(self) -> bool:
        return (self.quality + self.cost + (self.speed if self.speed else 0)) == 1


class DialtoneClient(BaseModel):
    api_key: str
    provider_config: ProviderConfig
    dials: Dials = Dials()
    router_model_config: Optional[RouterModelConfig] = None
    fallback_config: Optional[FallbackConfig] = None
    tools_config: Optional[ToolsConfig] = None
    base_url: Optional[str] = None


class RouteDecision(BaseModel):
    model: LLM
    providers: list[Provider]
    quality_predictions: dict[str, float]
    routing_strategy: str
