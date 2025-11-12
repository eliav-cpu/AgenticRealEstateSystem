"""
Configuration Manager
Centralized configuration management with environment variable support
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from pathlib import Path
import json


@dataclass
class LLMConfig:
    """LLM configuration"""
    provider: str = "groq"
    api_key: str = ""
    default_model: str = "moonshotai/kimi-k2-instruct-0905"
    temperature: float = 0.1
    max_tokens: int = 2000
    timeout: float = 30.0

    # Agent-specific models
    search_model: Optional[str] = None
    property_model: Optional[str] = None
    scheduling_model: Optional[str] = None


@dataclass
class DataConfig:
    """Data layer configuration"""
    mode: str = "mock"  # mock or real
    mock_data_path: str = "data/fixtures"
    duckdb_path: str = "data/properties.duckdb"

    # External APIs (for real mode)
    rentcast_api_key: str = ""
    rentcast_base_url: str = "https://api.rentcast.io/v1"


@dataclass
class DatabaseConfig:
    """Database configuration"""
    # PostgreSQL
    db_url: str = "postgresql://user:password@localhost:5432/real_estate"
    db_echo: bool = False
    db_pool_size: int = 5
    db_max_overflow: int = 10

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_password: str = ""
    redis_max_connections: int = 10


@dataclass
class ObservabilityConfig:
    """Observability configuration"""
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Metrics
    metrics_enabled: bool = True
    metrics_port: int = 8090

    # Tracing
    tracing_enabled: bool = True
    jaeger_endpoint: str = ""

    # Langfuse
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"
    langfuse_enabled: bool = False

    # Logfire
    logfire_token: str = ""
    logfire_enabled: bool = False

    # LangSmith
    langsmith_api_key: str = ""
    langsmith_project: str = "agentic-real-estate"
    langsmith_endpoint: str = "https://api.smith.langchain.com"


@dataclass
class ResilienceConfig:
    """Resilience configuration"""
    # Circuit Breaker
    circuit_enabled: bool = True
    failure_threshold: int = 5
    recovery_timeout: int = 60

    # Retry
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_backoff: float = 2.0

    # Timeout
    default_timeout: float = 30.0


@dataclass
class SwarmConfig:
    """Swarm configuration"""
    # Handoff
    handoff_timeout: float = 5.0
    max_handoffs: int = 10

    # Context
    context_window: int = 4000
    context_overlap: int = 200


@dataclass
class SecurityConfig:
    """Security configuration"""
    secret_key: str = "dev-secret-key-change-in-production"
    token_expire_minutes: int = 30
    rate_limit_requests: int = 100
    rate_limit_window: int = 60


@dataclass
class AppConfig:
    """Complete application configuration"""
    app_name: str = "Agentic Real Estate"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True

    llm: LLMConfig = field(default_factory=LLMConfig)
    data: DataConfig = field(default_factory=DataConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    observability: ObservabilityConfig = field(default_factory=ObservabilityConfig)
    resilience: ResilienceConfig = field(default_factory=ResilienceConfig)
    swarm: SwarmConfig = field(default_factory=SwarmConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)


class ConfigManager:
    """Manage application configuration"""

    def __init__(self, env_file: Optional[str] = None):
        """Initialize configuration manager"""
        self.env_file = env_file or ".env"
        self._load_env_file()
        self.config = self._build_config()

    def _load_env_file(self):
        """Load environment variables from .env file"""
        env_path = Path(self.env_file)
        if not env_path.exists():
            return

        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    if key and value and key not in os.environ:
                        os.environ[key] = value

    def _get_env(self, key: str, default: Any = "") -> Any:
        """Get environment variable with type conversion"""
        value = os.getenv(key, default)

        # Type conversion
        if isinstance(default, bool):
            return value.lower() in ("true", "1", "yes") if isinstance(value, str) else bool(value)
        elif isinstance(default, int):
            return int(value) if value else default
        elif isinstance(default, float):
            return float(value) if value else default

        return value

    def _build_config(self) -> AppConfig:
        """Build configuration from environment"""
        return AppConfig(
            app_name=self._get_env("APP_NAME", "Agentic Real Estate"),
            app_version=self._get_env("APP_VERSION", "1.0.0"),
            environment=self._get_env("ENVIRONMENT", "development"),
            debug=self._get_env("DEBUG", True),

            llm=LLMConfig(
                provider=self._get_env("LLM_PROVIDER", "groq"),
                api_key=self._get_env("GROQ_API_KEY", ""),
                default_model=self._get_env("LLM_DEFAULT_MODEL", "moonshotai/kimi-k2-instruct-0905"),
                temperature=self._get_env("LLM_TEMPERATURE", 0.1),
                max_tokens=self._get_env("LLM_MAX_TOKENS", 2000),
                timeout=self._get_env("LLM_TIMEOUT", 30.0),
                search_model=self._get_env("LLM_SEARCH_MODEL"),
                property_model=self._get_env("LLM_PROPERTY_MODEL"),
                scheduling_model=self._get_env("LLM_SCHEDULING_MODEL")
            ),

            data=DataConfig(
                mode=self._get_env("DATA_MODE", "mock"),
                mock_data_path=self._get_env("DATA_MOCK_DATA_PATH", "data/fixtures"),
                duckdb_path=self._get_env("DUCKDB_DB_PATH", "data/properties.duckdb"),
                rentcast_api_key=self._get_env("RENTCAST_API_KEY", ""),
                rentcast_base_url=self._get_env("RENTCAST_BASE_URL", "https://api.rentcast.io/v1")
            ),

            database=DatabaseConfig(
                db_url=self._get_env("DB_URL", "postgresql://user:password@localhost:5432/real_estate"),
                db_echo=self._get_env("DB_ECHO", False),
                db_pool_size=self._get_env("DB_POOL_SIZE", 5),
                db_max_overflow=self._get_env("DB_MAX_OVERFLOW", 10),
                redis_url=self._get_env("REDIS_URL", "redis://localhost:6379/0"),
                redis_password=self._get_env("REDIS_PASSWORD", ""),
                redis_max_connections=self._get_env("REDIS_MAX_CONNECTIONS", 10)
            ),

            observability=ObservabilityConfig(
                log_level=self._get_env("OBS_LOG_LEVEL", "INFO"),
                log_format=self._get_env("OBS_LOG_FORMAT", "json"),
                metrics_enabled=self._get_env("OBS_METRICS_ENABLED", True),
                metrics_port=self._get_env("OBS_METRICS_PORT", 8090),
                tracing_enabled=self._get_env("OBS_TRACING_ENABLED", True),
                jaeger_endpoint=self._get_env("OBS_JAEGER_ENDPOINT", ""),
                langfuse_public_key=self._get_env("LANGFUSE_PUBLIC_KEY", ""),
                langfuse_secret_key=self._get_env("LANGFUSE_SECRET_KEY", ""),
                langfuse_host=self._get_env("LANGFUSE_HOST", "https://cloud.langfuse.com"),
                langfuse_enabled=bool(self._get_env("LANGFUSE_PUBLIC_KEY", "")),
                logfire_token=self._get_env("LOGFIRE_TOKEN", ""),
                logfire_enabled=bool(self._get_env("LOGFIRE_TOKEN", "")),
                langsmith_api_key=self._get_env("LANGSMITH_API_KEY", ""),
                langsmith_project=self._get_env("LANGSMITH_PROJECT", "agentic-real-estate"),
                langsmith_endpoint=self._get_env("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
            ),

            resilience=ResilienceConfig(
                circuit_enabled=self._get_env("RESILIENCE_CIRCUIT_ENABLED", True),
                failure_threshold=self._get_env("RESILIENCE_FAILURE_THRESHOLD", 5),
                recovery_timeout=self._get_env("RESILIENCE_RECOVERY_TIMEOUT", 60),
                max_retries=self._get_env("RESILIENCE_MAX_RETRIES", 3),
                retry_delay=self._get_env("RESILIENCE_RETRY_DELAY", 1.0),
                retry_backoff=self._get_env("RESILIENCE_RETRY_BACKOFF", 2.0),
                default_timeout=self._get_env("RESILIENCE_DEFAULT_TIMEOUT", 30.0)
            ),

            swarm=SwarmConfig(
                handoff_timeout=self._get_env("SWARM_HANDOFF_TIMEOUT", 5.0),
                max_handoffs=self._get_env("SWARM_MAX_HANDOFFS", 10),
                context_window=self._get_env("SWARM_CONTEXT_WINDOW", 4000),
                context_overlap=self._get_env("SWARM_CONTEXT_OVERLAP", 200)
            ),

            security=SecurityConfig(
                secret_key=self._get_env("SECRET_KEY", "dev-secret-key-change-in-production"),
                token_expire_minutes=self._get_env("TOKEN_EXPIRE_MINUTES", 30),
                rate_limit_requests=self._get_env("RATE_LIMIT_REQUESTS", 100),
                rate_limit_window=self._get_env("RATE_LIMIT_WINDOW", 60)
            )
        )

    def get_config(self) -> AppConfig:
        """Get complete configuration"""
        return self.config

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        def dataclass_to_dict(obj):
            if hasattr(obj, "__dataclass_fields__"):
                return {
                    key: dataclass_to_dict(getattr(obj, key))
                    for key in obj.__dataclass_fields__
                }
            return obj

        return dataclass_to_dict(self.config)

    def validate(self) -> bool:
        """Validate configuration"""
        errors = []

        # Check required API keys in production
        if self.config.environment == "production":
            if not self.config.llm.api_key:
                errors.append("GROQ_API_KEY is required in production")

            if self.config.data.mode == "real":
                if not self.config.data.rentcast_api_key:
                    errors.append("RENTCAST_API_KEY is required for real data mode")

        # Check security settings in production
        if self.config.environment == "production":
            if self.config.security.secret_key == "dev-secret-key-change-in-production":
                errors.append("SECRET_KEY must be changed in production")

            if self.config.debug:
                errors.append("DEBUG should be False in production")

        if errors:
            for error in errors:
                print(f"Configuration Error: {error}")
            return False

        return True


# Global configuration instance
_config_manager: Optional[ConfigManager] = None


def get_config() -> AppConfig:
    """Get global configuration instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager.get_config()


def reload_config():
    """Reload configuration from environment"""
    global _config_manager
    _config_manager = ConfigManager()
    return _config_manager.get_config()


# Example usage
if __name__ == "__main__":
    config = get_config()

    print("=== Application Configuration ===")
    print(f"App: {config.app_name} v{config.app_version}")
    print(f"Environment: {config.environment}")
    print(f"Debug: {config.debug}")
    print(f"\nLLM Provider: {config.llm.provider}")
    print(f"LLM Model: {config.llm.default_model}")
    print(f"Data Mode: {config.data.mode}")
    print(f"\nObservability:")
    print(f"  - Langfuse: {config.observability.langfuse_enabled}")
    print(f"  - Logfire: {config.observability.logfire_enabled}")

    # Validate
    is_valid = ConfigManager().validate()
    print(f"\nConfiguration Valid: {is_valid}")
