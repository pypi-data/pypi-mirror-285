#############################################################################
#                                                                           #
# Copyright © 2023 Faceware Technologies, Inc.                              #
#                                                                           #
# All rights reserved.  No part of this software including any part         #
# of the coding or data forming any part thereof may be used or reproduced  #
# in any form or by any means otherwise than in accordance with any         #
# written license granted by Faceware Technologies, Inc.                    #
#                                                                           #
# Requests for permissions for use of copyright material forming            #
# part of this software (including the grant of licenses) shall be made     #
# to Faceware Technologies, Inc.                                            #
#                                                                           #
#############################################################################
"""pyportal is a python library for submitting new jobs & downloading results of the processed jobs from FACEWARE PORTAL."""

import logging
import os
import asyncio
import base64
import mimetypes
from . import constant, exceptions, utils
from .project import Project
from .base_component import BaseComponent
from typing import Optional, List


class PortalClient(BaseComponent):
    """Class responsible for getting data and creating new projects in FacewareTech Cloud Portal."""

    def __init__(self,
                 access_token: Optional[str] = None,
                 organization_id: Optional[str] = None,
                 parent_logger: Optional[logging.Logger] = None):
        """Initialize the PortalClient.

        Args:
            access_token: The access token to use for authentication.
                                        Leave as None to use env var `FACEWARE_PORTAL_API_ACCESS_TOKEN`

            organization_id: Your organization id on Portal
                                        Leave as None to use env var `FACEWARE_PORTAL_ORGANIZATION_ID`

        Raises:
            AccessTokenNotFoundError: If no valid access_token is found
            OrganizationIdNotFoundError: If no valid organization_id is found
        """
        BaseComponent.init_log(parent_logger)
        if access_token is None and os.environ.get(
                constant.ENV_VAR_FACEWARE_PORTAL_ACCESS_TOKEN, None) is None:
            raise exceptions.AccessTokenNotFoundError(
                f'Please provide access token as part of client initialization or set env var {constant.ENV_VAR_FACEWARE_PORTAL_ACCESS_TOKEN}'
            )

        if organization_id is None and os.environ.get(
                constant.ENV_VAR_FACEWARE_PORTAL_ORG_ID, None) is None:
            raise exceptions.OrganizationIdNotFoundError(
                f'Please provide organization id as part of client initialization or set env var {constant.ENV_VAR_FACEWARE_PORTAL_ORG_ID}'
            )

        self.access_token = access_token if access_token is not None else os.environ.get(
            constant.ENV_VAR_FACEWARE_PORTAL_ACCESS_TOKEN)
        self.organization_id = organization_id if organization_id is not None else os.environ.get(
            constant.ENV_VAR_FACEWARE_PORTAL_ORG_ID)
        BaseComponent.init_api(self.access_token, self.organization_id)

    async def create_project(
            self,
            project_name: str,
            project_description: Optional[str] = None) -> Project:
        """Create new project in the Cloud Portal.

        Args:
            project_name: Your Cloud Portal project name
            project_description: Short description of the project

        Returns:
            Returns the created project

        Raises:
            exceptions.PortalHTTPException: If there was an error while communicating with FacewareTech Portal.
            TypeError: If the project is failed to validate.
        """
        project = Project(id='',
                          name=project_name,
                          description=project_description)
        project.validate_project()
        body = {'name': project.name}
        if project.description is not None:
            body['description'] = project.description
        url = constant.get_project_post_api_url()
        _, response_json = await self.api.post(url=url, body=body)
        project.id = response_json['projectId']
        return project

    async def get_projects(self,
                           enabled: Optional[bool] = None) -> List[Project]:
        """Get list of projects.

        Args:
            enabled: A boolean for filterting projects by enabled status. None will return all projects.

        Returns:
            List of projects.

        Raises:
            exceptions.PortalHTTPException: If there was an error while communicating with FacewareTech Portal.
        """
        url = constant.get_projects_api_url()
        params = {}
        params['enabled'] = 'true' if enabled else 'false'
        _, response_json = await self.api.get(url, params)
        projects = []
        for item in response_json:
            project = Project(item['id'], item['name'], item.get('description'),
                              item.get('logo'), item['enabled'],
                              item['jobCount'], item['processedSeconds'])
            projects.append(project)
        return projects

    async def get_project(self, project_id: str) -> Project:
        """Get a specfic project.

        Args:
            project_id: Your unique project ID

        Returns:
            project

        Raises:
            exceptions.PortalHTTPException: If there was an error while communicating with FacewareTech Portal.
        """
        url = constant.get_project_by_id_url(project_id)
        _, response_json = await self.api.get(url)
        project = Project(response_json['id'], response_json['name'],
                          response_json.get('description'),
                          response_json.get('logo'), response_json['enabled'],
                          response_json['jobCount'],
                          response_json['processedSeconds'])
        return project
