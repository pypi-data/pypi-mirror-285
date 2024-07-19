import loguru
from pinjected import instances, providers

__meta_design__ = instances(
    default_design_path="pinjected_openai.default_design"
)

from pinjected_openai.clients import async_openai_client, openai_api_key

default_design = instances(
) + providers(
    logger=lambda: loguru.logger,
    async_openai_client=async_openai_client,
    openai_api_key=openai_api_key
)
