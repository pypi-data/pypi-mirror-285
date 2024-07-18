from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

CASTOR_ENV_PREFIX = "CASTOR_SIGMA_"


class SigmaCredentials(BaseSettings):
    """Class to handle Sigma rest API permissions"""

    model_config = SettingsConfigDict(
        env_prefix=CASTOR_ENV_PREFIX,
        extra="ignore",
        populate_by_name=True,
    )

    api_token: str = Field(repr=False)
    client_id: str
    host: str
    grant_type: str = "client_credentials"
