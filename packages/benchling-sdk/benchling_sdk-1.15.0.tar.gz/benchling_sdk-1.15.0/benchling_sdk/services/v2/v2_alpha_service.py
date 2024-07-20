from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from benchling_api_client.v2.stable.client import Client

from benchling_sdk.helpers.client_helpers import v2_alpha_client
from benchling_sdk.helpers.retry_helpers import RetryStrategy

if TYPE_CHECKING:
    from benchling_sdk.services.v2.alpha.v2_alpha_app_service import V2AlphaAppService

from benchling_sdk.services.v2.base_service import BaseService


class V2AlphaService(BaseService):
    """
    V2-alpha.

    Alpha endpoints have different stability guidelines than other stable endpoints.

    See https://benchling.com/api/v2-alpha/reference
    """

    _alpha_client: Client

    def __init__(self, client: Client, retry_strategy: RetryStrategy = RetryStrategy()):
        """
        Initialize a v2-alpha service.

        :param client: Underlying generated Client.
        :param retry_strategy: Retry strategy for failed HTTP calls
        """
        super().__init__(client, retry_strategy)
        self._alpha_client = v2_alpha_client(self.client)

    @cached_property
    def apps(self) -> V2AlphaAppService:
        """
        V2-Alpha Apps.

        Create and manage Apps on your tenant.

        https://benchling.com/api/v2-alpha/reference?stability=not-available#/Apps
        """
        from .alpha.v2_alpha_app_service import V2AlphaAppService

        return self._create_service(V2AlphaAppService)

    def _create_service(self, cls):
        """Instantiate a service using the alpha client."""
        return cls(self._alpha_client, self._retry_strategy)
