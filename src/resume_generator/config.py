import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration settings for the resume generator."""

    # OpenAI Configuration
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.1"))

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Validation
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present."""
        if not cls.OPENAI_API_KEY:
            return False
        return True

    @classmethod
    def get_missing_configs(cls) -> list[str]:
        """Get list of missing required configurations."""
        missing = []
        if not cls.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
        return missing


# Global config instance
config = Config()
