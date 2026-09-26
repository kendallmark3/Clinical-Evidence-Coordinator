import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    provider_mode: str = os.getenv("PROVIDER_MODE", "mock")
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    bedrock_model_id: str = os.getenv("BEDROCK_MODEL_ID", "")
    artifact_dir: str = os.getenv("ARTIFACT_DIR", "artifacts")

settings = Settings()
