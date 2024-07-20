from typing import Dict, Optional

from pydantic import SecretStr

from promptquality.constants.integrations import IntegrationName
from promptquality.set_config import set_config
from promptquality.types.config import Config
from promptquality.types.run import CreateIntegrationRequest


def add_openai_integration(
    api_key: str, organization_id: Optional[str] = None, config: Optional[Config] = None
) -> None:
    """
    Add an OpenAI integration to your Galileo account.

    If you add an integration while one already exists, the new integration will
    overwrite the old one.

    Parameters
    ----------
    api_key : str
        Your OpenAI API key.
    organization_id : Optional[str], optional
        Organization ID, if you want to include it in OpenAI requests, by default None
    config : Optional[Config], optional
        Config to use, by default None which translates to the config being set
        automatically.
    """
    config = config or set_config()
    config.api_client.put_integration(
        integration_request=CreateIntegrationRequest(
            api_key=SecretStr(api_key), name=IntegrationName.openai, organization_id=organization_id
        ),
    )


def add_azure_integration(
    api_key: str,
    endpoint: str,
    headers: Optional[Dict[str, str]] = None,
    proxy: Optional[bool] = None,
    config: Optional[Config] = None,
) -> None:
    """
    Add an Azure integration to your Galileo account.

    If you add an integration while one already exists, the new integration will
    overwrite the old one.

    Parameters
    ----------
    api_key : str
        Your Azure API key.
    endpoint : str
        The endpoint to use for the Azure API.
    headers : Optional[Dict[str, str]], optional
        Headers to use for making requests to Azure, by default None
    config : Optional[Config], optional
        Config to use, by default None which translates to the config being set
        automatically.
    """
    config = config or set_config()
    config.api_client.put_integration(
        integration_request=CreateIntegrationRequest(
            api_key=SecretStr(api_key),
            name=IntegrationName.azure,
            endpoint=endpoint,
            headers=headers,
            proxy=proxy,
        ),
    )
