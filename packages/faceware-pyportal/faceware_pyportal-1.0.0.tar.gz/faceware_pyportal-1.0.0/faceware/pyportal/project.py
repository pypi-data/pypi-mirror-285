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
"""Module for Cloud Portal projects."""

from aiolimiter import AsyncLimiter
import asyncio
import os
import math
from stat import S_ISDIR, S_ISREG
from . import constant
from typing import Optional, List
from .job import TrackingModel, VideoRotation, Job
from .job_result import JobStatus, JobResult
from .base_component import BaseComponent
from dataclasses import dataclass

VALID_FILTERING_STATUSES = [
    JobStatus.IN_PROGRESS, JobStatus.COMPLETED, JobStatus.QUEUED,
    JobStatus.FAILED, JobStatus.CANCELED
]

JOB_SUBMISSION_RATE_LIMIT = AsyncLimiter(1, 2)
"""
Allow maximum of 1 job submission in 2 seconds
"""


@dataclass
class JobResults:
    """Data class used for .get_jobs() response."""
    jobs: List[Job]
    next: Optional[str] = None
    limit: Optional[int] = None


class Project(BaseComponent):
    """A class encapsulating Cloud Portal Project.

    Intended to be initilized via the client, not directly.

    Has the following accessible properties:
    - name
    - description
    - logo
    - id
    - enabled
    - job_count
    - processed_seconds

    !!! warning The 'job_count', 'enabled, and 'processed_seconds' properties are not updated in real-time and added only for filtering purposes when the projects are loaded via project `get_project` and `get_projects` methods.
    For the latest updates run these methods again.
    """
    name: str
    description: Optional[str]
    logo: Optional[str]
    id: str
    enabled: Optional[bool]
    job_count: Optional[int]
    processed_seconds: Optional[float]

    def __init__(self,
                 id: str,
                 name: str,
                 description: Optional[str],
                 logo: Optional[str] = None,
                 enabled: Optional[bool] = None,
                 job_count: Optional[int] = None,
                 processed_seconds: Optional[float] = None) -> None:
        """Initialize Project.

        Args:
            id: Unique project ID.
            name: Name of the project.
            description: Description of the project.
            logo: Base 64 encoded project logo.
            enabled: Enabled status of the project.
            job_count: Number of jobs in the project.
            processed_seconds: Total number of processed seconds.
        """
        self.id = id
        self.name = name
        self.description = description
        self.logo = logo
        self.enabled = enabled
        self.job_count = job_count
        self.processed_seconds = processed_seconds

    async def submit_job(
            self,
            actor_name: str,
            tracking_model: TrackingModel,
            video_file_path: str,
            calibration_image_file_path: Optional[str] = None,
            video_rotation: Optional[VideoRotation] = VideoRotation.NONE,
            tracking_version: Optional[str] = None) -> Job:
        """Will create new job and submit it for processing.

        Args:
            actor_name: The name of the actor for this job
            tracking_model: Select if the video was recorded on Head cam or static cam
            video_file_path: Absolute local file system filepath to the video file. File size limit is 5TiB.
            calibration_image_file_path: Absolute local file system filepath to the calibration image file
            video_rotation: The orientation of the camera when video was recorded
            tracking_version: Tracking version for Job.
        
        Raises:
            exceptions.PortalHTTPException: If there was an error while communicating with FacewareTech Portal.

        Returns:
            Job object.
        """
        async with JOB_SUBMISSION_RATE_LIMIT:
            if self.enabled is False:
                raise TypeError("Can't submit a job for a disabled project.")
            job = Job(self.id, actor_name, tracking_model, video_file_path,
                      calibration_image_file_path, video_rotation,
                      tracking_version)
            job.validate_job()
            # calibration file upload
            if job.calibration_image_file_path is not None:
                self.log.debug('Uploading the calibration image')
                job._uploaded_image_s3_key = await self.api.upload_file(
                    job.calibration_image_file_path, job.project_id)
            # video file upload
            self.log.debug('Uploading the video')
            job._uploaded_video_s3_key = await self.api.upload_file(
                job.video_file_path, job.project_id)
            # post the job
            job_id = await self.__post_job(job)
            job._job_result = JobResult(job.project_id, job_id)
            job._job_result.status = JobStatus.IN_PROGRESS
            return job

    async def __post_job(self, job: Job) -> str:
        self.log.info('Job: Posting job for processing')
        body = {
            'actorName': job.actor_name,
            'trackingModel': job.tracking_model.value,
            'rotation': job.video_rotation.value,
            'videoKey': job._uploaded_video_s3_key,
        }
        if job.tracking_version is not None:
            body['trackingVersion'] = job.tracking_version

        if job._uploaded_image_s3_key is not None:
            body['calibrationImageKey'] = job._uploaded_image_s3_key

        _, response_json = await self.api.post(
            url=constant.get_job_post_api_url(job.project_id), body=body)
        job_id = response_json['jobId']
        self.log.info('Job: Posted job for processing. Job id: %s', job_id)
        return job_id

    async def get_jobs(self,
                       next: Optional[str] = None,
                       limit: Optional[int] = None,
                       status: Optional[List[JobStatus]] = None) -> List[Job]:
        """Get the list of all jobs in the project.

        Args:
            next: the token use for pagination, will be returned with a previous get_jobs() request if the limit was set. Used to load next sequence of the jobs
            limit: how many jobs to load
            status: filter jobs based on the JobStatus

        Valid filtering statuses:
            JobStatus.IN_PROGRESS
            JobStatus.QUEUED
            JobStatus.COMPLETED
            JobStatus.FAILED

        Raises:
            exceptions.PortalHTTPException: If there was an error while communicating with FacewareTech Portal.
            ValueError: If the invalid filterting status provided.
        
        Returns:
            The JobResults object.
        """
        params = {}
        if next is not None:
            params['next'] = next
        if limit is not None:
            params['limit'] = limit
        if status is not None:
            invalid_statuses = [
                s for s in status if s not in VALID_FILTERING_STATUSES
            ]
            if invalid_statuses:
                raise ValueError(
                    f"Invalid filtering statuses: {', '.join(str(s) for s in invalid_statuses)}"
                )
            params['status'] = [s.value for s in status]
        _, response_json = await self.api.get(
            constant.get_all_jobs_for_project_api_url(self.id), params)
        jobs = []
        for item in response_json['results']:
            rotation_value = int(item['input']['rotation'])
            job = Job(project_id=self.id,
                      actor_name=item['actorName'],
                      tracking_model=TrackingModel(
                          item['input']['trackingModel']),
                      video_rotation=VideoRotation(rotation_value),
                      tracking_version=item['input']['trackingVersion'])
            job._job_result = JobResult(
                project_id=self.id,
                id=item['jobId'],
                status=JobStatus.from_str(item['status']),
                extended_status=item.get('extendedStatus'),
                progress=item['progress'],
                processing_seconds=item['processingSeconds'])
            jobs.append(job)
        return JobResults(jobs, response_json.get('next'),
                          response_json.get('limit'))

    async def get_job(self, job_id: str) -> Job:
        """Get a specific job by id.

        Args:
            job_id: Unique ID to load the job.
        
        Returns:
            Job object.

        Raises:
            exceptions.PortalHTTPException: If there was an error while communicating with FacewareTech Portal.
        """
        _, response_json = await self.api.get(
            constant.get_job_by_id_api_url(self.id, job_id))
        rotation_value = int(response_json['input']['rotation'])
        job = Job(self.id, response_json['actorName'],
                  TrackingModel(response_json['input']['trackingModel']),
                  response_json['input'].get('trackingVersion', None), None,
                  VideoRotation(rotation_value),
                  response_json['input'].get('trackingVersion', None))
        job._job_result = JobResult(self.id, response_json['jobId'],
                                    JobStatus.from_str(response_json['status']),
                                    response_json.get('progress'),
                                    response_json.get('processingSeconds'))
        return job

    def validate_project(self):
        """Validates project before uploading."""
        self.log.info('Validating project')
        # Validates name
        if not isinstance(self.name, str):
            raise TypeError('Invalid Name')
        # Validates description
        if self.description is not None:
            if not isinstance(self.description, str):
                raise TypeError('Invalid description')
        self.log.info('Project validation finished')
