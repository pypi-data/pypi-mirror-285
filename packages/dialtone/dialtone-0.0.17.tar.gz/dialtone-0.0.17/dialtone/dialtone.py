from typing import Any, Optional
from pydantic import ValidationError, BaseModel
from dialtone.types import (
    FallbackConfig,
    ProviderConfig,
    RouterModelConfig,
    ChatCompletion,
    Choice,
    ChatMessage,
    Tool,
    DialtoneClient,
    Dials,
    RouteDecision,
    TokenUsage,
    LLM,
    ToolsConfig,
)
from dialtone.utils import dialtone_post_request, prepare_chat_message
from dialtone.config import DEFAULT_BASE_URL


class Completions(BaseModel):
    client: DialtoneClient

    def create(
        self, messages: list[ChatMessage] | list[dict[str, Any]], tools: list[Tool] = []
    ):
        headers = {"Authorization": f"Bearer {self.client.api_key}"}
        params = {
            "messages": [prepare_chat_message(message) for message in messages],
            "dials": self.client.dials.model_dump(),
            "provider_config": self.client.provider_config.model_dump(),
        }
        if self.client.router_model_config:
            params["router_model_config"] = self.client.router_model_config.model_dump()
        if self.client.fallback_config:
            params["fallback_config"] = self.client.fallback_config.model_dump()
        if self.client.tools_config:
            params["tools_config"] = self.client.tools_config.model_dump()
        if tools:
            params["tools"] = [tool.model_dump() for tool in tools]

        response_json = dialtone_post_request(
            url=f"{self.client.base_url}/chat/completions",
            data=params,
            headers=headers,
        )

        return ChatCompletion(
            choices=[
                Choice(
                    model=response_json["model"],
                    provider=response_json["provider"],
                    message=response_json["message"],
                )
            ],
            usage=TokenUsage(**response_json["usage"]),
        )


class Chat(BaseModel):
    client: DialtoneClient
    completions: Completions

    def __init__(self, client: DialtoneClient):
        completions = Completions(client=client)
        super().__init__(client=client, completions=completions)

    def route(
        self, messages: list[ChatMessage] | list[dict[str, Any]], tools: list[Tool] = []
    ):
        headers = {"Authorization": f"Bearer {self.client.api_key}"}
        params = {
            "messages": [prepare_chat_message(message) for message in messages],
            "dials": self.client.dials.model_dump(),
            "provider_config": self.client.provider_config.model_dump(),
        }
        if self.client.router_model_config:
            params["router_model_config"] = self.client.router_model_config.model_dump()
        if self.client.fallback_config:
            params["fallback_config"] = self.client.fallback_config.model_dump()
        if self.client.tools_config:
            params["tools_config"] = self.client.tools_config.model_dump()
        if tools:
            params["tools"] = [tool.model_dump() for tool in tools]

        response_json = dialtone_post_request(
            url=f"{self.client.base_url}/chat/route",
            data=params,
            headers=headers,
            timeout=15,
        )

        return RouteDecision(
            model=response_json["model"],
            providers=response_json["providers"],
            quality_predictions=response_json["quality_predictions"],
            routing_strategy=response_json["routing_strategy"],
        )


class Dialtone:
    chat: Chat
    client: DialtoneClient

    def __init__(
        self,
        api_key: str,
        provider_config: ProviderConfig | dict[str, Any],
        dials: Dials | dict[str, Any] = Dials(quality=0.5, cost=0.5, speed=0),
        router_model_config: Optional[RouterModelConfig | dict[str, Any]] = None,
        fallback_config: Optional[FallbackConfig | dict[str, Any]] = None,
        tools_config: Optional[ToolsConfig | dict[str, Any]] = None,
        base_url: str = DEFAULT_BASE_URL,
    ):
        try:
            if isinstance(provider_config, dict):
                provider_config = ProviderConfig(**provider_config)
        except ValidationError as e:
            raise ValidationError(f"Invalid provider_config: {e}")

        try:
            if not isinstance(dials, Dials):
                dials = Dials(**dials)
        except ValidationError as e:
            raise ValidationError(f"Invalid dials: {e}")

        try:
            if router_model_config:
                if isinstance(router_model_config, dict):
                    router_model_config = RouterModelConfig(**router_model_config)
            else:
                router_model_config = None
        except ValidationError as e:
            raise ValidationError(f"Invalid router_model_config: {e}")

        if router_model_config:
            try:
                if router_model_config.include_models:
                    router_model_config.include_models = [
                        LLM(model) if isinstance(model, str) else model
                        for model in router_model_config.include_models
                    ]
            except ValueError as e:
                raise ValidationError(f"Invalid include_models: {e}")

            try:
                if router_model_config.exclude_models:
                    router_model_config.exclude_models = [
                        LLM(model) if isinstance(model, str) else model
                        for model in router_model_config.exclude_models
                    ]
            except ValueError as e:
                raise ValidationError(f"Invalid exclude_models: {e}")

        try:
            if isinstance(fallback_config, dict):
                fallback_config = FallbackConfig(**fallback_config)
            else:
                fallback_config = None
        except ValidationError as e:
            raise ValidationError(f"Invalid fallback_config: {e}")

        try:
            if isinstance(tools_config, dict):
                tools_config = ToolsConfig(**tools_config)
            else:
                tools_config = None
        except ValidationError as e:
            raise ValidationError(f"Invalid tools_config: {e}")

        self.client = DialtoneClient(
            api_key=api_key,
            provider_config=provider_config,
            router_model_config=router_model_config,
            fallback_config=fallback_config,
            tools_config=tools_config,
            base_url=base_url,
            dials=dials,
        )
        self.chat = Chat(client=self.client)
