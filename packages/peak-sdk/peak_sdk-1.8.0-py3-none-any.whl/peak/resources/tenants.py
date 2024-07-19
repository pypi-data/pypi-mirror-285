#
# # Copyright © 2024 Peak AI Limited. or its affiliates. All Rights Reserved.
# #
# # Licensed under the Apache License, Version 2.0 (the "License"). You
# # may not use this file except in compliance with the License. A copy of
# # the License is located at:
# #
# # https://github.com/PeakBI/peak-sdk/blob/main/LICENSE
# #
# # or in the "license" file accompanying this file. This file is
# # distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# # ANY KIND, either express or implied. See the License for the specific
# # language governing permissions and limitations under the License.
# #
# # This file is part of the peak-sdk.
# # see (https://github.com/PeakBI/peak-sdk)
# #
# # You should have received a copy of the APACHE LICENSE, VERSION 2.0
# # along with this program. If not, see <https://apache.org/licenses/LICENSE-2.0>
#
"""Tenants client module."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from peak.base_client import BaseClient
from peak.constants import ContentType, HttpMethods
from peak.session import Session


class Tenant(BaseClient):
    """Tenant client class."""

    BASE_ENDPOINT = "quota/api/v1"

    def list_instance_options(
        self,
        entity_type: str,
    ) -> Dict[str, Any]:
        """Retrieve details of allowed instance options for a tenant.

        REFERENCE:
            🔗 `API Documentation <https://service.peak.ai/quota/api-docs/index.htm#/settings/get_api_v1_settings_tenant_instance_options>`__

        Args:
            entity_type (str): The type of the entity.
                Allowed values are - api-deployment, data-bridge, webapp, workflow, workspace.

        Returns:
            Dict[str, Any]: a dictionary containing the details of the allowed instance options of a tenant.

        Raises:
            BadRequestException: The given request parameters are invalid.
            UnauthorizedException: The credentials are invalid.
            ForbiddenException: The user does not have permission to perform the operation.
            NotFoundException: The given image does not exist.
            InternalServerErrorException: The server failed to process the request.
        """
        method, endpoint = HttpMethods.GET, f"{self.BASE_ENDPOINT}/settings/tenant-instance-options"
        params = {"entityType": entity_type}

        return self.session.create_request(  # type: ignore[no-any-return]
            endpoint,
            method,
            content_type=ContentType.APPLICATION_JSON,
            params=params,
        )


def get_client(session: Optional[Session] = None) -> Tenant:
    """Returns a Tenant client, If no session is provided, a default session is used.

    Args:
        session (Optional[Session]): A Session Object. Default is None.

    Returns:
        Tenant: the tenant client object
    """
    return Tenant(session)


__all__: List[str] = ["get_client"]
