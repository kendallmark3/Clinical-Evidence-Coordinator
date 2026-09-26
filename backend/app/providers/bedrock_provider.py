from .base import Provider

DEFAULT_MODEL_ID = "anthropic.claude-opus-5"

class BedrockProvider(Provider):
    """Claude on Amazon Bedrock via the Anthropic SDK's Mantle client.

    Credentials come from the standard AWS chain (AWS_PROFILE, env vars, or the
    AgentCore execution role). Any API failure or refusal raises, and the
    calling agent fails closed.
    """

    name = "bedrock"

    def __init__(self, region: str, model_id: str = ""):
        from anthropic import AnthropicBedrockMantle

        self.region = region
        self.model_id = model_id or DEFAULT_MODEL_ID
        self.client = AnthropicBedrockMantle(aws_region=region)

    def generate(self, prompt: str, system: str = "") -> str:
        response = self.client.messages.create(
            model=self.model_id,
            max_tokens=16000,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        if response.stop_reason == "refusal":
            raise RuntimeError("Model declined the request.")
        return "".join(b.text for b in response.content if b.type == "text")
