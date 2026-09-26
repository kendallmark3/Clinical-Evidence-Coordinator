from backend.app.config import Settings

from .base import Provider
from .mock_provider import MockProvider

def get_provider(settings: Settings) -> Provider:
    if settings.provider_mode == "bedrock":
        from .bedrock_provider import BedrockProvider
        return BedrockProvider(settings.aws_region, settings.bedrock_model_id)
    if settings.provider_mode == "mock":
        return MockProvider()
    raise ValueError(f"Unknown PROVIDER_MODE: {settings.provider_mode!r}")
