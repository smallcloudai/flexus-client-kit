import base64
import json
import logging
import os
from typing import Any, Dict, Optional
from urllib.parse import quote

import httpx


logger = logging.getLogger("apify")

PROVIDER_NAME = "apify"
_BASE_URL = "https://api.apify.com"
_TIMEOUT = 60.0
_TEXT_RESPONSE_PREFIXES = (
    "text/",
    "application/json",
    "application/xml",
    "application/javascript",
    "application/x-www-form-urlencoded",
    "application/csv",
    "application/xhtml+xml",
)

METHOD_SPECS = [
    {
        'method_id': 'apify.PostChargeRun.v1',
        'operation_id': 'PostChargeRun',
        'http_method': 'POST',
        'path': '/v2/actor-runs/{runId}/charge',
        'summary': 'Charge events in run',
        'path_params': ['runId'],
        'query_params': [],
        'has_request_body': True,
        'request_content_types': ['application/json'],
        'response_content_types': [],
    },
    {
        'method_id': 'apify.PostResurrectRun.v1',
        'operation_id': 'PostResurrectRun',
        'http_method': 'POST',
        'path': '/v2/actor-runs/{runId}/resurrect',
        'summary': 'Resurrect run',
        'path_params': ['runId'],
        'query_params': ['build', 'memory', 'restartOnError', 'timeout'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.act_build_abort_post.v1',
        'operation_id': 'act_build_abort_post',
        'http_method': 'POST',
        'path': '/v2/acts/{actorId}/builds/{buildId}/abort',
        'summary': 'Abort build',
        'path_params': ['actorId', 'buildId'],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.act_build_default_get.v1',
        'operation_id': 'act_build_default_get',
        'http_method': 'GET',
        'path': '/v2/acts/{actorId}/builds/default',
        'summary': 'Get default build',
        'path_params': ['actorId'],
        'query_params': ['waitForFinish'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.act_build_get.v1',
        'operation_id': 'act_build_get',
        'http_method': 'GET',
        'path': '/v2/acts/{actorId}/builds/{buildId}',
        'summary': 'Get build',
        'path_params': ['actorId', 'buildId'],
        'query_params': ['waitForFinish'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.act_builds_get.v1',
        'operation_id': 'act_builds_get',
        'http_method': 'GET',
        'path': '/v2/acts/{actorId}/builds',
        'summary': 'Get list of builds',
        'path_params': ['actorId'],
        'query_params': ['desc', 'limit', 'offset'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.act_builds_post.v1',
        'operation_id': 'act_builds_post',
        'http_method': 'POST',
        'path': '/v2/acts/{actorId}/builds',
        'summary': 'Build Actor',
        'path_params': ['actorId'],
        'query_params': ['betaPackages', 'tag', 'useCache', 'version', 'waitForFinish'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.act_delete.v1',
        'operation_id': 'act_delete',
        'http_method': 'DELETE',
        'path': '/v2/acts/{actorId}',
        'summary': 'Delete Actor',
        'path_params': ['actorId'],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.act_get.v1',
        'operation_id': 'act_get',
        'http_method': 'GET',
        'path': '/v2/acts/{actorId}',
        'summary': 'Get Actor',
        'path_params': ['actorId'],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.act_openapi_json_get.v1',
        'operation_id': 'act_openapi_json_get',
        'http_method': 'GET',
        'path': '/v2/acts/{actorId}/builds/{buildId}/openapi.json',
        'summary': 'Get OpenAPI definition',
        'path_params': ['actorId', 'buildId'],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.act_put.v1',
        'operation_id': 'act_put',
        'http_method': 'PUT',
        'path': '/v2/acts/{actorId}',
        'summary': 'Update Actor',
        'path_params': ['actorId'],
        'query_params': [],
        'has_request_body': True,
        'request_content_types': ['application/json'],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.act_runSyncGetDatasetItems_get.v1',
        'operation_id': 'act_runSyncGetDatasetItems_get',
        'http_method': 'GET',
        'path': '/v2/acts/{actorId}/run-sync-get-dataset-items',
        'summary': 'Run Actor synchronously without input and get dataset items',
        'path_params': ['actorId'],
        'query_params': ['attachment', 'bom', 'build', 'clean', 'delimiter', 'desc', 'fields', 'flatten', 'format', 'limit', 'memory', 'offset', 'omit', 'restartOnError', 'simplified', 'skipEmpty', 'skipFailedPages', 'skipHeaderRow', 'skipHidden', 'timeout', 'unwind', 'webhooks', 'xmlRoot', 'xmlRow'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.act_runSyncGetDatasetItems_post.v1',
        'operation_id': 'act_runSyncGetDatasetItems_post',
        'http_method': 'POST',
        'path': '/v2/acts/{actorId}/run-sync-get-dataset-items',
        'summary': 'Run Actor synchronously with input and get dataset items',
        'path_params': ['actorId'],
        'query_params': ['attachment', 'bom', 'build', 'clean', 'delimiter', 'desc', 'fields', 'flatten', 'format', 'limit', 'memory', 'offset', 'omit', 'restartOnError', 'simplified', 'skipEmpty', 'skipFailedPages', 'skipHeaderRow', 'skipHidden', 'timeout', 'unwind', 'webhooks', 'xmlRoot', 'xmlRow'],
        'has_request_body': True,
        'request_content_types': ['application/json'],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.act_runSync_get.v1',
        'operation_id': 'act_runSync_get',
        'http_method': 'GET',
        'path': '/v2/acts/{actorId}/run-sync',
        'summary': 'Without input',
        'path_params': ['actorId'],
        'query_params': ['build', 'memory', 'outputRecordKey', 'restartOnError', 'timeout', 'webhooks'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.act_runSync_post.v1',
        'operation_id': 'act_runSync_post',
        'http_method': 'POST',
        'path': '/v2/acts/{actorId}/run-sync',
        'summary': 'Run Actor synchronously with input and return output',
        'path_params': ['actorId'],
        'query_params': ['build', 'memory', 'outputRecordKey', 'restartOnError', 'timeout', 'webhooks'],
        'has_request_body': True,
        'request_content_types': ['application/json'],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.act_run_abort_post.v1',
        'operation_id': 'act_run_abort_post',
        'http_method': 'POST',
        'path': '/v2/acts/{actorId}/runs/{runId}/abort',
        'summary': 'Abort run',
        'path_params': ['actorId', 'runId'],
        'query_params': ['gracefully'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.act_run_get.v1',
        'operation_id': 'act_run_get',
        'http_method': 'GET',
        'path': '/v2/acts/{actorId}/runs/{runId}',
        'summary': 'Get run',
        'path_params': ['actorId', 'runId'],
        'query_params': ['waitForFinish'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.act_run_metamorph_post.v1',
        'operation_id': 'act_run_metamorph_post',
        'http_method': 'POST',
        'path': '/v2/acts/{actorId}/runs/{runId}/metamorph',
        'summary': 'Metamorph run',
        'path_params': ['actorId', 'runId'],
        'query_params': ['build', 'targetActorId'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.act_run_resurrect_post.v1',
        'operation_id': 'act_run_resurrect_post',
        'http_method': 'POST',
        'path': '/v2/acts/{actorId}/runs/{runId}/resurrect',
        'summary': 'Resurrect run',
        'path_params': ['actorId', 'runId'],
        'query_params': ['build', 'memory', 'restartOnError', 'timeout'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.act_runs_get.v1',
        'operation_id': 'act_runs_get',
        'http_method': 'GET',
        'path': '/v2/acts/{actorId}/runs',
        'summary': 'Get list of runs',
        'path_params': ['actorId'],
        'query_params': ['desc', 'limit', 'offset', 'startedAfter', 'startedBefore', 'status'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.act_runs_last_get.v1',
        'operation_id': 'act_runs_last_get',
        'http_method': 'GET',
        'path': '/v2/acts/{actorId}/runs/last',
        'summary': 'Get last run',
        'path_params': ['actorId'],
        'query_params': ['status'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.act_runs_post.v1',
        'operation_id': 'act_runs_post',
        'http_method': 'POST',
        'path': '/v2/acts/{actorId}/runs',
        'summary': 'Run Actor',
        'path_params': ['actorId'],
        'query_params': ['build', 'forcePermissionLevel', 'memory', 'restartOnError', 'timeout', 'waitForFinish', 'webhooks'],
        'has_request_body': True,
        'request_content_types': ['application/json'],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.act_version_delete.v1',
        'operation_id': 'act_version_delete',
        'http_method': 'DELETE',
        'path': '/v2/acts/{actorId}/versions/{versionNumber}',
        'summary': 'Delete version',
        'path_params': ['actorId', 'versionNumber'],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.act_version_envVar_delete.v1',
        'operation_id': 'act_version_envVar_delete',
        'http_method': 'DELETE',
        'path': '/v2/acts/{actorId}/versions/{versionNumber}/env-vars/{envVarName}',
        'summary': 'Delete environment variable',
        'path_params': ['actorId', 'envVarName', 'versionNumber'],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.act_version_envVar_get.v1',
        'operation_id': 'act_version_envVar_get',
        'http_method': 'GET',
        'path': '/v2/acts/{actorId}/versions/{versionNumber}/env-vars/{envVarName}',
        'summary': 'Get environment variable',
        'path_params': ['actorId', 'envVarName', 'versionNumber'],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.act_version_envVar_put.v1',
        'operation_id': 'act_version_envVar_put',
        'http_method': 'PUT',
        'path': '/v2/acts/{actorId}/versions/{versionNumber}/env-vars/{envVarName}',
        'summary': 'Update environment variable',
        'path_params': ['actorId', 'envVarName', 'versionNumber'],
        'query_params': [],
        'has_request_body': True,
        'request_content_types': ['application/json'],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.act_version_envVars_get.v1',
        'operation_id': 'act_version_envVars_get',
        'http_method': 'GET',
        'path': '/v2/acts/{actorId}/versions/{versionNumber}/env-vars',
        'summary': 'Get list of environment variables',
        'path_params': ['actorId', 'versionNumber'],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.act_version_envVars_post.v1',
        'operation_id': 'act_version_envVars_post',
        'http_method': 'POST',
        'path': '/v2/acts/{actorId}/versions/{versionNumber}/env-vars',
        'summary': 'Create environment variable',
        'path_params': ['actorId', 'versionNumber'],
        'query_params': [],
        'has_request_body': True,
        'request_content_types': ['application/json'],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.act_version_get.v1',
        'operation_id': 'act_version_get',
        'http_method': 'GET',
        'path': '/v2/acts/{actorId}/versions/{versionNumber}',
        'summary': 'Get version',
        'path_params': ['actorId', 'versionNumber'],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.act_version_put.v1',
        'operation_id': 'act_version_put',
        'http_method': 'PUT',
        'path': '/v2/acts/{actorId}/versions/{versionNumber}',
        'summary': 'Update version',
        'path_params': ['actorId', 'versionNumber'],
        'query_params': [],
        'has_request_body': True,
        'request_content_types': ['application/json'],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.act_versions_get.v1',
        'operation_id': 'act_versions_get',
        'http_method': 'GET',
        'path': '/v2/acts/{actorId}/versions',
        'summary': 'Get list of versions',
        'path_params': ['actorId'],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.act_versions_post.v1',
        'operation_id': 'act_versions_post',
        'http_method': 'POST',
        'path': '/v2/acts/{actorId}/versions',
        'summary': 'Create version',
        'path_params': ['actorId'],
        'query_params': [],
        'has_request_body': True,
        'request_content_types': ['application/json'],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.act_webhooks_get.v1',
        'operation_id': 'act_webhooks_get',
        'http_method': 'GET',
        'path': '/v2/acts/{actorId}/webhooks',
        'summary': 'Get list of webhooks',
        'path_params': ['actorId'],
        'query_params': ['desc', 'limit', 'offset'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.actorBuild_abort_post.v1',
        'operation_id': 'actorBuild_abort_post',
        'http_method': 'POST',
        'path': '/v2/actor-builds/{buildId}/abort',
        'summary': 'Abort build',
        'path_params': ['buildId'],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.actorBuild_delete.v1',
        'operation_id': 'actorBuild_delete',
        'http_method': 'DELETE',
        'path': '/v2/actor-builds/{buildId}',
        'summary': 'Delete build',
        'path_params': ['buildId'],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': [],
    },
    {
        'method_id': 'apify.actorBuild_get.v1',
        'operation_id': 'actorBuild_get',
        'http_method': 'GET',
        'path': '/v2/actor-builds/{buildId}',
        'summary': 'Get build',
        'path_params': ['buildId'],
        'query_params': ['waitForFinish'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.actorBuild_log_get.v1',
        'operation_id': 'actorBuild_log_get',
        'http_method': 'GET',
        'path': '/v2/actor-builds/{buildId}/log',
        'summary': 'Get log',
        'path_params': ['buildId'],
        'query_params': ['download', 'stream'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['text/plain'],
    },
    {
        'method_id': 'apify.actorBuild_openapi_json_get.v1',
        'operation_id': 'actorBuild_openapi_json_get',
        'http_method': 'GET',
        'path': '/v2/actor-builds/{buildId}/openapi.json',
        'summary': 'Get OpenAPI definition',
        'path_params': ['buildId'],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.actorBuilds_get.v1',
        'operation_id': 'actorBuilds_get',
        'http_method': 'GET',
        'path': '/v2/actor-builds',
        'summary': 'Get user builds list',
        'path_params': [],
        'query_params': ['desc', 'limit', 'offset'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.actorRun_abort_post.v1',
        'operation_id': 'actorRun_abort_post',
        'http_method': 'POST',
        'path': '/v2/actor-runs/{runId}/abort',
        'summary': 'Abort run',
        'path_params': ['runId'],
        'query_params': ['gracefully'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.actorRun_delete.v1',
        'operation_id': 'actorRun_delete',
        'http_method': 'DELETE',
        'path': '/v2/actor-runs/{runId}',
        'summary': 'Delete run',
        'path_params': ['runId'],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': [],
    },
    {
        'method_id': 'apify.actorRun_get.v1',
        'operation_id': 'actorRun_get',
        'http_method': 'GET',
        'path': '/v2/actor-runs/{runId}',
        'summary': 'Get run',
        'path_params': ['runId'],
        'query_params': ['waitForFinish'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.actorRun_metamorph_post.v1',
        'operation_id': 'actorRun_metamorph_post',
        'http_method': 'POST',
        'path': '/v2/actor-runs/{runId}/metamorph',
        'summary': 'Metamorph run',
        'path_params': ['runId'],
        'query_params': ['build', 'targetActorId'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.actorRun_put.v1',
        'operation_id': 'actorRun_put',
        'http_method': 'PUT',
        'path': '/v2/actor-runs/{runId}',
        'summary': 'Update run',
        'path_params': ['runId'],
        'query_params': [],
        'has_request_body': True,
        'request_content_types': ['application/json'],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.actorRun_reboot_post.v1',
        'operation_id': 'actorRun_reboot_post',
        'http_method': 'POST',
        'path': '/v2/actor-runs/{runId}/reboot',
        'summary': 'Reboot run',
        'path_params': ['runId'],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.actorRuns_get.v1',
        'operation_id': 'actorRuns_get',
        'http_method': 'GET',
        'path': '/v2/actor-runs',
        'summary': 'Get user runs list',
        'path_params': [],
        'query_params': ['desc', 'limit', 'offset', 'startedAfter', 'startedBefore', 'status'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.actorTask_delete.v1',
        'operation_id': 'actorTask_delete',
        'http_method': 'DELETE',
        'path': '/v2/actor-tasks/{actorTaskId}',
        'summary': 'Delete task',
        'path_params': ['actorTaskId'],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.actorTask_get.v1',
        'operation_id': 'actorTask_get',
        'http_method': 'GET',
        'path': '/v2/actor-tasks/{actorTaskId}',
        'summary': 'Get task',
        'path_params': ['actorTaskId'],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.actorTask_input_get.v1',
        'operation_id': 'actorTask_input_get',
        'http_method': 'GET',
        'path': '/v2/actor-tasks/{actorTaskId}/input',
        'summary': 'Get task input',
        'path_params': ['actorTaskId'],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.actorTask_input_put.v1',
        'operation_id': 'actorTask_input_put',
        'http_method': 'PUT',
        'path': '/v2/actor-tasks/{actorTaskId}/input',
        'summary': 'Update task input',
        'path_params': ['actorTaskId'],
        'query_params': [],
        'has_request_body': True,
        'request_content_types': ['application/json'],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.actorTask_put.v1',
        'operation_id': 'actorTask_put',
        'http_method': 'PUT',
        'path': '/v2/actor-tasks/{actorTaskId}',
        'summary': 'Update task',
        'path_params': ['actorTaskId'],
        'query_params': [],
        'has_request_body': True,
        'request_content_types': ['application/json'],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.actorTask_runSyncGetDatasetItems_get.v1',
        'operation_id': 'actorTask_runSyncGetDatasetItems_get',
        'http_method': 'GET',
        'path': '/v2/actor-tasks/{actorTaskId}/run-sync-get-dataset-items',
        'summary': 'Run task synchronously and get dataset items',
        'path_params': ['actorTaskId'],
        'query_params': ['attachment', 'bom', 'build', 'clean', 'delimiter', 'desc', 'fields', 'flatten', 'format', 'limit', 'memory', 'offset', 'omit', 'simplified', 'skipEmpty', 'skipFailedPages', 'skipHeaderRow', 'skipHidden', 'timeout', 'unwind', 'webhooks', 'xmlRoot', 'xmlRow'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.actorTask_runSyncGetDatasetItems_post.v1',
        'operation_id': 'actorTask_runSyncGetDatasetItems_post',
        'http_method': 'POST',
        'path': '/v2/actor-tasks/{actorTaskId}/run-sync-get-dataset-items',
        'summary': 'Run task synchronously and get dataset items',
        'path_params': ['actorTaskId'],
        'query_params': ['attachment', 'bom', 'build', 'clean', 'delimiter', 'desc', 'fields', 'flatten', 'format', 'limit', 'memory', 'offset', 'omit', 'restartOnError', 'simplified', 'skipEmpty', 'skipFailedPages', 'skipHeaderRow', 'skipHidden', 'timeout', 'unwind', 'webhooks', 'xmlRoot', 'xmlRow'],
        'has_request_body': True,
        'request_content_types': ['application/json'],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.actorTask_runSync_get.v1',
        'operation_id': 'actorTask_runSync_get',
        'http_method': 'GET',
        'path': '/v2/actor-tasks/{actorTaskId}/run-sync',
        'summary': 'Run task synchronously',
        'path_params': ['actorTaskId'],
        'query_params': ['build', 'memory', 'outputRecordKey', 'timeout', 'webhooks'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.actorTask_runSync_post.v1',
        'operation_id': 'actorTask_runSync_post',
        'http_method': 'POST',
        'path': '/v2/actor-tasks/{actorTaskId}/run-sync',
        'summary': 'Run task synchronously',
        'path_params': ['actorTaskId'],
        'query_params': ['build', 'memory', 'outputRecordKey', 'restartOnError', 'timeout', 'webhooks'],
        'has_request_body': True,
        'request_content_types': ['application/json'],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.actorTask_runs_get.v1',
        'operation_id': 'actorTask_runs_get',
        'http_method': 'GET',
        'path': '/v2/actor-tasks/{actorTaskId}/runs',
        'summary': 'Get list of task runs',
        'path_params': ['actorTaskId'],
        'query_params': ['desc', 'limit', 'offset', 'status'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.actorTask_runs_last_get.v1',
        'operation_id': 'actorTask_runs_last_get',
        'http_method': 'GET',
        'path': '/v2/actor-tasks/{actorTaskId}/runs/last',
        'summary': 'Get last run',
        'path_params': ['actorTaskId'],
        'query_params': ['status'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.actorTask_runs_post.v1',
        'operation_id': 'actorTask_runs_post',
        'http_method': 'POST',
        'path': '/v2/actor-tasks/{actorTaskId}/runs',
        'summary': 'Run task',
        'path_params': ['actorTaskId'],
        'query_params': ['build', 'memory', 'restartOnError', 'timeout', 'waitForFinish', 'webhooks'],
        'has_request_body': True,
        'request_content_types': ['application/json'],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.actorTask_webhooks_get.v1',
        'operation_id': 'actorTask_webhooks_get',
        'http_method': 'GET',
        'path': '/v2/actor-tasks/{actorTaskId}/webhooks',
        'summary': 'Get list of webhooks',
        'path_params': ['actorTaskId'],
        'query_params': ['desc', 'limit', 'offset'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.actorTasks_get.v1',
        'operation_id': 'actorTasks_get',
        'http_method': 'GET',
        'path': '/v2/actor-tasks',
        'summary': 'Get list of tasks',
        'path_params': [],
        'query_params': ['desc', 'limit', 'offset'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.actorTasks_post.v1',
        'operation_id': 'actorTasks_post',
        'http_method': 'POST',
        'path': '/v2/actor-tasks',
        'summary': 'Create task',
        'path_params': [],
        'query_params': [],
        'has_request_body': True,
        'request_content_types': ['application/json'],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.acts_get.v1',
        'operation_id': 'acts_get',
        'http_method': 'GET',
        'path': '/v2/acts',
        'summary': 'Get list of Actors',
        'path_params': [],
        'query_params': ['desc', 'limit', 'my', 'offset', 'sortBy'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.acts_post.v1',
        'operation_id': 'acts_post',
        'http_method': 'POST',
        'path': '/v2/acts',
        'summary': 'Create Actor',
        'path_params': [],
        'query_params': [],
        'has_request_body': True,
        'request_content_types': ['application/json'],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.dataset_delete.v1',
        'operation_id': 'dataset_delete',
        'http_method': 'DELETE',
        'path': '/v2/datasets/{datasetId}',
        'summary': 'Delete dataset',
        'path_params': [],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': [],
    },
    {
        'method_id': 'apify.dataset_get.v1',
        'operation_id': 'dataset_get',
        'http_method': 'GET',
        'path': '/v2/datasets/{datasetId}',
        'summary': 'Get dataset',
        'path_params': [],
        'query_params': ['token'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.dataset_items_get.v1',
        'operation_id': 'dataset_items_get',
        'http_method': 'GET',
        'path': '/v2/datasets/{datasetId}/items',
        'summary': 'Get dataset items',
        'path_params': [],
        'query_params': ['attachment', 'bom', 'clean', 'delimiter', 'fields', 'flatten', 'format', 'limit', 'omit', 'simplified', 'skipEmpty', 'skipFailedPages', 'skipHeaderRow', 'skipHidden', 'unwind', 'view', 'xmlRoot', 'xmlRow'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json', 'application/jsonl', 'application/rss+xml', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/xml', 'text/csv', 'text/html'],
    },
    {
        'method_id': 'apify.dataset_items_post.v1',
        'operation_id': 'dataset_items_post',
        'http_method': 'POST',
        'path': '/v2/datasets/{datasetId}/items',
        'summary': 'Store items',
        'path_params': [],
        'query_params': [],
        'has_request_body': True,
        'request_content_types': ['application/json'],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.dataset_put.v1',
        'operation_id': 'dataset_put',
        'http_method': 'PUT',
        'path': '/v2/datasets/{datasetId}',
        'summary': 'Update dataset',
        'path_params': [],
        'query_params': [],
        'has_request_body': True,
        'request_content_types': ['application/json'],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.dataset_statistics_get.v1',
        'operation_id': 'dataset_statistics_get',
        'http_method': 'GET',
        'path': '/v2/datasets/{datasetId}/statistics',
        'summary': 'Get dataset statistics',
        'path_params': [],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.datasets_get.v1',
        'operation_id': 'datasets_get',
        'http_method': 'GET',
        'path': '/v2/datasets',
        'summary': 'Get list of datasets',
        'path_params': [],
        'query_params': ['ownership'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.datasets_post.v1',
        'operation_id': 'datasets_post',
        'http_method': 'POST',
        'path': '/v2/datasets',
        'summary': 'Create dataset',
        'path_params': [],
        'query_params': ['name'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.keyValueStore_delete.v1',
        'operation_id': 'keyValueStore_delete',
        'http_method': 'DELETE',
        'path': '/v2/key-value-stores/{storeId}',
        'summary': 'Delete store',
        'path_params': [],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': [],
    },
    {
        'method_id': 'apify.keyValueStore_get.v1',
        'operation_id': 'keyValueStore_get',
        'http_method': 'GET',
        'path': '/v2/key-value-stores/{storeId}',
        'summary': 'Get store',
        'path_params': [],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.keyValueStore_keys_get.v1',
        'operation_id': 'keyValueStore_keys_get',
        'http_method': 'GET',
        'path': '/v2/key-value-stores/{storeId}/keys',
        'summary': 'Get list of keys',
        'path_params': [],
        'query_params': ['collection', 'exclusiveStartKey', 'limit', 'prefix'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.keyValueStore_put.v1',
        'operation_id': 'keyValueStore_put',
        'http_method': 'PUT',
        'path': '/v2/key-value-stores/{storeId}',
        'summary': 'Update store',
        'path_params': [],
        'query_params': [],
        'has_request_body': True,
        'request_content_types': ['application/json'],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.keyValueStore_record_delete.v1',
        'operation_id': 'keyValueStore_record_delete',
        'http_method': 'DELETE',
        'path': '/v2/key-value-stores/{storeId}/records/{recordKey}',
        'summary': 'Delete record',
        'path_params': [],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': [],
    },
    {
        'method_id': 'apify.keyValueStore_record_get.v1',
        'operation_id': 'keyValueStore_record_get',
        'http_method': 'GET',
        'path': '/v2/key-value-stores/{storeId}/records/{recordKey}',
        'summary': 'Get record',
        'path_params': [],
        'query_params': ['attachment'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.keyValueStore_record_head.v1',
        'operation_id': 'keyValueStore_record_head',
        'http_method': 'HEAD',
        'path': '/v2/key-value-stores/{storeId}/records/{recordKey}',
        'summary': 'Check if a record exists',
        'path_params': [],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': [],
    },
    {
        'method_id': 'apify.keyValueStore_record_put.v1',
        'operation_id': 'keyValueStore_record_put',
        'http_method': 'PUT',
        'path': '/v2/key-value-stores/{storeId}/records/{recordKey}',
        'summary': 'Store record',
        'path_params': [],
        'query_params': [],
        'has_request_body': True,
        'request_content_types': ['application/json'],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.keyValueStores_get.v1',
        'operation_id': 'keyValueStores_get',
        'http_method': 'GET',
        'path': '/v2/key-value-stores',
        'summary': 'Get list of key-value stores',
        'path_params': [],
        'query_params': ['ownership'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.keyValueStores_post.v1',
        'operation_id': 'keyValueStores_post',
        'http_method': 'POST',
        'path': '/v2/key-value-stores',
        'summary': 'Create key-value store',
        'path_params': [],
        'query_params': ['name'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.log_get.v1',
        'operation_id': 'log_get',
        'http_method': 'GET',
        'path': '/v2/logs/{buildOrRunId}',
        'summary': 'Get log',
        'path_params': ['buildOrRunId'],
        'query_params': ['download', 'raw', 'stream'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['text/plain'],
    },
    {
        'method_id': 'apify.requestQueue_delete.v1',
        'operation_id': 'requestQueue_delete',
        'http_method': 'DELETE',
        'path': '/v2/request-queues/{queueId}',
        'summary': 'Delete request queue',
        'path_params': [],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': [],
    },
    {
        'method_id': 'apify.requestQueue_get.v1',
        'operation_id': 'requestQueue_get',
        'http_method': 'GET',
        'path': '/v2/request-queues/{queueId}',
        'summary': 'Get request queue',
        'path_params': [],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.requestQueue_head_get.v1',
        'operation_id': 'requestQueue_head_get',
        'http_method': 'GET',
        'path': '/v2/request-queues/{queueId}/head',
        'summary': 'Get head',
        'path_params': [],
        'query_params': ['limit'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.requestQueue_head_lock_post.v1',
        'operation_id': 'requestQueue_head_lock_post',
        'http_method': 'POST',
        'path': '/v2/request-queues/{queueId}/head/lock',
        'summary': 'Get head and lock',
        'path_params': [],
        'query_params': ['limit'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.requestQueue_put.v1',
        'operation_id': 'requestQueue_put',
        'http_method': 'PUT',
        'path': '/v2/request-queues/{queueId}',
        'summary': 'Update request queue',
        'path_params': [],
        'query_params': [],
        'has_request_body': True,
        'request_content_types': ['application/json'],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.requestQueue_request_delete.v1',
        'operation_id': 'requestQueue_request_delete',
        'http_method': 'DELETE',
        'path': '/v2/request-queues/{queueId}/requests/{requestId}',
        'summary': 'Delete request',
        'path_params': [],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': [],
    },
    {
        'method_id': 'apify.requestQueue_request_get.v1',
        'operation_id': 'requestQueue_request_get',
        'http_method': 'GET',
        'path': '/v2/request-queues/{queueId}/requests/{requestId}',
        'summary': 'Get request',
        'path_params': [],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.requestQueue_request_lock_delete.v1',
        'operation_id': 'requestQueue_request_lock_delete',
        'http_method': 'DELETE',
        'path': '/v2/request-queues/{queueId}/requests/{requestId}/lock',
        'summary': 'Delete request lock',
        'path_params': [],
        'query_params': ['forefront'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': [],
    },
    {
        'method_id': 'apify.requestQueue_request_lock_put.v1',
        'operation_id': 'requestQueue_request_lock_put',
        'http_method': 'PUT',
        'path': '/v2/request-queues/{queueId}/requests/{requestId}/lock',
        'summary': 'Prolong request lock',
        'path_params': [],
        'query_params': ['forefront'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.requestQueue_request_put.v1',
        'operation_id': 'requestQueue_request_put',
        'http_method': 'PUT',
        'path': '/v2/request-queues/{queueId}/requests/{requestId}',
        'summary': 'Update request',
        'path_params': [],
        'query_params': [],
        'has_request_body': True,
        'request_content_types': ['application/json'],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.requestQueue_requests_batch_delete.v1',
        'operation_id': 'requestQueue_requests_batch_delete',
        'http_method': 'DELETE',
        'path': '/v2/request-queues/{queueId}/requests/batch',
        'summary': 'Delete requests',
        'path_params': [],
        'query_params': [],
        'has_request_body': True,
        'request_content_types': ['application/json'],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.requestQueue_requests_batch_post.v1',
        'operation_id': 'requestQueue_requests_batch_post',
        'http_method': 'POST',
        'path': '/v2/request-queues/{queueId}/requests/batch',
        'summary': 'Add requests',
        'path_params': [],
        'query_params': [],
        'has_request_body': True,
        'request_content_types': ['application/json'],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.requestQueue_requests_get.v1',
        'operation_id': 'requestQueue_requests_get',
        'http_method': 'GET',
        'path': '/v2/request-queues/{queueId}/requests',
        'summary': 'List requests',
        'path_params': [],
        'query_params': ['exclusiveStartId', 'limit'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.requestQueue_requests_post.v1',
        'operation_id': 'requestQueue_requests_post',
        'http_method': 'POST',
        'path': '/v2/request-queues/{queueId}/requests',
        'summary': 'Add request',
        'path_params': [],
        'query_params': [],
        'has_request_body': True,
        'request_content_types': ['application/json'],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.requestQueue_requests_unlock_post.v1',
        'operation_id': 'requestQueue_requests_unlock_post',
        'http_method': 'POST',
        'path': '/v2/request-queues/{queueId}/requests/unlock',
        'summary': 'Unlock requests',
        'path_params': [],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.requestQueues_get.v1',
        'operation_id': 'requestQueues_get',
        'http_method': 'GET',
        'path': '/v2/request-queues',
        'summary': 'Get list of request queues',
        'path_params': [],
        'query_params': ['ownership'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.requestQueues_post.v1',
        'operation_id': 'requestQueues_post',
        'http_method': 'POST',
        'path': '/v2/request-queues',
        'summary': 'Create request queue',
        'path_params': [],
        'query_params': ['name'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.schedule_delete.v1',
        'operation_id': 'schedule_delete',
        'http_method': 'DELETE',
        'path': '/v2/schedules/{scheduleId}',
        'summary': 'Delete schedule',
        'path_params': ['scheduleId'],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.schedule_get.v1',
        'operation_id': 'schedule_get',
        'http_method': 'GET',
        'path': '/v2/schedules/{scheduleId}',
        'summary': 'Get schedule',
        'path_params': ['scheduleId'],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.schedule_log_get.v1',
        'operation_id': 'schedule_log_get',
        'http_method': 'GET',
        'path': '/v2/schedules/{scheduleId}/log',
        'summary': 'Get schedule log',
        'path_params': ['scheduleId'],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.schedule_put.v1',
        'operation_id': 'schedule_put',
        'http_method': 'PUT',
        'path': '/v2/schedules/{scheduleId}',
        'summary': 'Update schedule',
        'path_params': ['scheduleId'],
        'query_params': [],
        'has_request_body': True,
        'request_content_types': ['application/json'],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.schedules_get.v1',
        'operation_id': 'schedules_get',
        'http_method': 'GET',
        'path': '/v2/schedules',
        'summary': 'Get list of schedules',
        'path_params': [],
        'query_params': ['desc', 'limit', 'offset'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.schedules_post.v1',
        'operation_id': 'schedules_post',
        'http_method': 'POST',
        'path': '/v2/schedules',
        'summary': 'Create schedule',
        'path_params': [],
        'query_params': [],
        'has_request_body': True,
        'request_content_types': ['application/json'],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.store_get.v1',
        'operation_id': 'store_get',
        'http_method': 'GET',
        'path': '/v2/store',
        'summary': 'Get list of Actors in store',
        'path_params': [],
        'query_params': ['allowsAgenticUsers', 'category', 'limit', 'offset', 'pricingModel', 'search', 'sortBy', 'username'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.user_get.v1',
        'operation_id': 'user_get',
        'http_method': 'GET',
        'path': '/v2/users/{userId}',
        'summary': 'Get public user data',
        'path_params': ['userId'],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.users_me_get.v1',
        'operation_id': 'users_me_get',
        'http_method': 'GET',
        'path': '/v2/users/me',
        'summary': 'Get private user data',
        'path_params': [],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.users_me_limits_get.v1',
        'operation_id': 'users_me_limits_get',
        'http_method': 'GET',
        'path': '/v2/users/me/limits',
        'summary': 'Get limits',
        'path_params': [],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.users_me_limits_put.v1',
        'operation_id': 'users_me_limits_put',
        'http_method': 'PUT',
        'path': '/v2/users/me/limits',
        'summary': 'Update limits',
        'path_params': [],
        'query_params': [],
        'has_request_body': True,
        'request_content_types': ['application/json'],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.users_me_usage_monthly_get.v1',
        'operation_id': 'users_me_usage_monthly_get',
        'http_method': 'GET',
        'path': '/v2/users/me/usage/monthly',
        'summary': 'Get monthly usage',
        'path_params': [],
        'query_params': ['date'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.webhookDispatch_get.v1',
        'operation_id': 'webhookDispatch_get',
        'http_method': 'GET',
        'path': '/v2/webhook-dispatches/{dispatchId}',
        'summary': 'Get webhook dispatch',
        'path_params': ['dispatchId'],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.webhookDispatches_get.v1',
        'operation_id': 'webhookDispatches_get',
        'http_method': 'GET',
        'path': '/v2/webhook-dispatches',
        'summary': 'Get list of webhook dispatches',
        'path_params': [],
        'query_params': ['desc', 'limit', 'offset'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.webhook_delete.v1',
        'operation_id': 'webhook_delete',
        'http_method': 'DELETE',
        'path': '/v2/webhooks/{webhookId}',
        'summary': 'Delete webhook',
        'path_params': ['webhookId'],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.webhook_get.v1',
        'operation_id': 'webhook_get',
        'http_method': 'GET',
        'path': '/v2/webhooks/{webhookId}',
        'summary': 'Get webhook',
        'path_params': ['webhookId'],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.webhook_put.v1',
        'operation_id': 'webhook_put',
        'http_method': 'PUT',
        'path': '/v2/webhooks/{webhookId}',
        'summary': 'Update webhook',
        'path_params': ['webhookId'],
        'query_params': [],
        'has_request_body': True,
        'request_content_types': ['application/json'],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.webhook_test_post.v1',
        'operation_id': 'webhook_test_post',
        'http_method': 'POST',
        'path': '/v2/webhooks/{webhookId}/test',
        'summary': 'Test webhook',
        'path_params': ['webhookId'],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.webhook_webhookDispatches_get.v1',
        'operation_id': 'webhook_webhookDispatches_get',
        'http_method': 'GET',
        'path': '/v2/webhooks/{webhookId}/dispatches',
        'summary': 'Get collection',
        'path_params': ['webhookId'],
        'query_params': [],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.webhooks_get.v1',
        'operation_id': 'webhooks_get',
        'http_method': 'GET',
        'path': '/v2/webhooks',
        'summary': 'Get list of webhooks',
        'path_params': [],
        'query_params': ['desc', 'limit', 'offset'],
        'has_request_body': False,
        'request_content_types': [],
        'response_content_types': ['application/json'],
    },
    {
        'method_id': 'apify.webhooks_post.v1',
        'operation_id': 'webhooks_post',
        'http_method': 'POST',
        'path': '/v2/webhooks',
        'summary': 'Create webhook',
        'path_params': [],
        'query_params': ['desc', 'limit', 'offset'],
        'has_request_body': True,
        'request_content_types': ['application/json'],
        'response_content_types': ['application/json'],
    },
]
METHOD_IDS = [spec["method_id"] for spec in METHOD_SPECS]
METHOD_SPECS_BY_ID = {spec["method_id"]: spec for spec in METHOD_SPECS}


class IntegrationApify:
    def __init__(self, rcx=None):
        self.rcx = rcx

    def _auth(self) -> Dict[str, Any]:
        if self.rcx is not None:
            return (self.rcx.external_auth.get(PROVIDER_NAME) or {})
        return {}

    def _token(self) -> str:
        auth = self._auth()
        return str(
            auth.get("api_key", "")
            or auth.get("token", "")
            or auth.get("oauth_token", "")
            or os.environ.get("APIFY_API_TOKEN", "")
        ).strip()

    def _help(self) -> str:
        return (
            f"provider={PROVIDER_NAME}\n"
            "op=help | status | list_methods | call\n"
            "call args: method_id plus explicit endpoint args as documented in list_methods; optional body, body_base64, content_type, headers, accept, timeout_seconds, follow_redirects\n"
            f"methods={len(METHOD_IDS)}"
        )

    def _status(self) -> str:
        token = self._token()
        return json.dumps({
            "ok": True,
            "provider": PROVIDER_NAME,
            "status": "ready" if token else "missing_credentials",
            "has_api_token": bool(token),
            "method_count": len(METHOD_IDS),
        }, indent=2, ensure_ascii=False)

    async def called_by_model(self, toolcall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        args = model_produced_args or {}
        op = str(args.get("op", "help")).strip()
        if op == "help":
            return self._help()
        if op == "status":
            return self._status()
        if op == "list_methods":
            return json.dumps({"ok": True, "provider": PROVIDER_NAME, "method_ids": METHOD_IDS, "methods": METHOD_SPECS}, indent=2, ensure_ascii=False)
        if op != "call":
            return "Error: unknown op. Use help/status/list_methods/call."
        call_args = args.get("args") or {}
        method_id = str(call_args.get("method_id", "")).strip()
        if not method_id:
            return "Error: args.method_id required for op=call."
        return await self._dispatch(method_id, call_args)

    async def _dispatch(self, method_id: str, args: Dict[str, Any]) -> str:
        if method_id == 'apify.PostChargeRun.v1':
            return await self._PostChargeRun(args)
        if method_id == 'apify.PostResurrectRun.v1':
            return await self._PostResurrectRun(args)
        if method_id == 'apify.act_build_abort_post.v1':
            return await self._act_build_abort_post(args)
        if method_id == 'apify.act_build_default_get.v1':
            return await self._act_build_default_get(args)
        if method_id == 'apify.act_build_get.v1':
            return await self._act_build_get(args)
        if method_id == 'apify.act_builds_get.v1':
            return await self._act_builds_get(args)
        if method_id == 'apify.act_builds_post.v1':
            return await self._act_builds_post(args)
        if method_id == 'apify.act_delete.v1':
            return await self._act_delete(args)
        if method_id == 'apify.act_get.v1':
            return await self._act_get(args)
        if method_id == 'apify.act_openapi_json_get.v1':
            return await self._act_openapi_json_get(args)
        if method_id == 'apify.act_put.v1':
            return await self._act_put(args)
        if method_id == 'apify.act_runSyncGetDatasetItems_get.v1':
            return await self._act_runSyncGetDatasetItems_get(args)
        if method_id == 'apify.act_runSyncGetDatasetItems_post.v1':
            return await self._act_runSyncGetDatasetItems_post(args)
        if method_id == 'apify.act_runSync_get.v1':
            return await self._act_runSync_get(args)
        if method_id == 'apify.act_runSync_post.v1':
            return await self._act_runSync_post(args)
        if method_id == 'apify.act_run_abort_post.v1':
            return await self._act_run_abort_post(args)
        if method_id == 'apify.act_run_get.v1':
            return await self._act_run_get(args)
        if method_id == 'apify.act_run_metamorph_post.v1':
            return await self._act_run_metamorph_post(args)
        if method_id == 'apify.act_run_resurrect_post.v1':
            return await self._act_run_resurrect_post(args)
        if method_id == 'apify.act_runs_get.v1':
            return await self._act_runs_get(args)
        if method_id == 'apify.act_runs_last_get.v1':
            return await self._act_runs_last_get(args)
        if method_id == 'apify.act_runs_post.v1':
            return await self._act_runs_post(args)
        if method_id == 'apify.act_version_delete.v1':
            return await self._act_version_delete(args)
        if method_id == 'apify.act_version_envVar_delete.v1':
            return await self._act_version_envVar_delete(args)
        if method_id == 'apify.act_version_envVar_get.v1':
            return await self._act_version_envVar_get(args)
        if method_id == 'apify.act_version_envVar_put.v1':
            return await self._act_version_envVar_put(args)
        if method_id == 'apify.act_version_envVars_get.v1':
            return await self._act_version_envVars_get(args)
        if method_id == 'apify.act_version_envVars_post.v1':
            return await self._act_version_envVars_post(args)
        if method_id == 'apify.act_version_get.v1':
            return await self._act_version_get(args)
        if method_id == 'apify.act_version_put.v1':
            return await self._act_version_put(args)
        if method_id == 'apify.act_versions_get.v1':
            return await self._act_versions_get(args)
        if method_id == 'apify.act_versions_post.v1':
            return await self._act_versions_post(args)
        if method_id == 'apify.act_webhooks_get.v1':
            return await self._act_webhooks_get(args)
        if method_id == 'apify.actorBuild_abort_post.v1':
            return await self._actorBuild_abort_post(args)
        if method_id == 'apify.actorBuild_delete.v1':
            return await self._actorBuild_delete(args)
        if method_id == 'apify.actorBuild_get.v1':
            return await self._actorBuild_get(args)
        if method_id == 'apify.actorBuild_log_get.v1':
            return await self._actorBuild_log_get(args)
        if method_id == 'apify.actorBuild_openapi_json_get.v1':
            return await self._actorBuild_openapi_json_get(args)
        if method_id == 'apify.actorBuilds_get.v1':
            return await self._actorBuilds_get(args)
        if method_id == 'apify.actorRun_abort_post.v1':
            return await self._actorRun_abort_post(args)
        if method_id == 'apify.actorRun_delete.v1':
            return await self._actorRun_delete(args)
        if method_id == 'apify.actorRun_get.v1':
            return await self._actorRun_get(args)
        if method_id == 'apify.actorRun_metamorph_post.v1':
            return await self._actorRun_metamorph_post(args)
        if method_id == 'apify.actorRun_put.v1':
            return await self._actorRun_put(args)
        if method_id == 'apify.actorRun_reboot_post.v1':
            return await self._actorRun_reboot_post(args)
        if method_id == 'apify.actorRuns_get.v1':
            return await self._actorRuns_get(args)
        if method_id == 'apify.actorTask_delete.v1':
            return await self._actorTask_delete(args)
        if method_id == 'apify.actorTask_get.v1':
            return await self._actorTask_get(args)
        if method_id == 'apify.actorTask_input_get.v1':
            return await self._actorTask_input_get(args)
        if method_id == 'apify.actorTask_input_put.v1':
            return await self._actorTask_input_put(args)
        if method_id == 'apify.actorTask_put.v1':
            return await self._actorTask_put(args)
        if method_id == 'apify.actorTask_runSyncGetDatasetItems_get.v1':
            return await self._actorTask_runSyncGetDatasetItems_get(args)
        if method_id == 'apify.actorTask_runSyncGetDatasetItems_post.v1':
            return await self._actorTask_runSyncGetDatasetItems_post(args)
        if method_id == 'apify.actorTask_runSync_get.v1':
            return await self._actorTask_runSync_get(args)
        if method_id == 'apify.actorTask_runSync_post.v1':
            return await self._actorTask_runSync_post(args)
        if method_id == 'apify.actorTask_runs_get.v1':
            return await self._actorTask_runs_get(args)
        if method_id == 'apify.actorTask_runs_last_get.v1':
            return await self._actorTask_runs_last_get(args)
        if method_id == 'apify.actorTask_runs_post.v1':
            return await self._actorTask_runs_post(args)
        if method_id == 'apify.actorTask_webhooks_get.v1':
            return await self._actorTask_webhooks_get(args)
        if method_id == 'apify.actorTasks_get.v1':
            return await self._actorTasks_get(args)
        if method_id == 'apify.actorTasks_post.v1':
            return await self._actorTasks_post(args)
        if method_id == 'apify.acts_get.v1':
            return await self._acts_get(args)
        if method_id == 'apify.acts_post.v1':
            return await self._acts_post(args)
        if method_id == 'apify.dataset_delete.v1':
            return await self._dataset_delete(args)
        if method_id == 'apify.dataset_get.v1':
            return await self._dataset_get(args)
        if method_id == 'apify.dataset_items_get.v1':
            return await self._dataset_items_get(args)
        if method_id == 'apify.dataset_items_post.v1':
            return await self._dataset_items_post(args)
        if method_id == 'apify.dataset_put.v1':
            return await self._dataset_put(args)
        if method_id == 'apify.dataset_statistics_get.v1':
            return await self._dataset_statistics_get(args)
        if method_id == 'apify.datasets_get.v1':
            return await self._datasets_get(args)
        if method_id == 'apify.datasets_post.v1':
            return await self._datasets_post(args)
        if method_id == 'apify.keyValueStore_delete.v1':
            return await self._keyValueStore_delete(args)
        if method_id == 'apify.keyValueStore_get.v1':
            return await self._keyValueStore_get(args)
        if method_id == 'apify.keyValueStore_keys_get.v1':
            return await self._keyValueStore_keys_get(args)
        if method_id == 'apify.keyValueStore_put.v1':
            return await self._keyValueStore_put(args)
        if method_id == 'apify.keyValueStore_record_delete.v1':
            return await self._keyValueStore_record_delete(args)
        if method_id == 'apify.keyValueStore_record_get.v1':
            return await self._keyValueStore_record_get(args)
        if method_id == 'apify.keyValueStore_record_head.v1':
            return await self._keyValueStore_record_head(args)
        if method_id == 'apify.keyValueStore_record_put.v1':
            return await self._keyValueStore_record_put(args)
        if method_id == 'apify.keyValueStores_get.v1':
            return await self._keyValueStores_get(args)
        if method_id == 'apify.keyValueStores_post.v1':
            return await self._keyValueStores_post(args)
        if method_id == 'apify.log_get.v1':
            return await self._log_get(args)
        if method_id == 'apify.requestQueue_delete.v1':
            return await self._requestQueue_delete(args)
        if method_id == 'apify.requestQueue_get.v1':
            return await self._requestQueue_get(args)
        if method_id == 'apify.requestQueue_head_get.v1':
            return await self._requestQueue_head_get(args)
        if method_id == 'apify.requestQueue_head_lock_post.v1':
            return await self._requestQueue_head_lock_post(args)
        if method_id == 'apify.requestQueue_put.v1':
            return await self._requestQueue_put(args)
        if method_id == 'apify.requestQueue_request_delete.v1':
            return await self._requestQueue_request_delete(args)
        if method_id == 'apify.requestQueue_request_get.v1':
            return await self._requestQueue_request_get(args)
        if method_id == 'apify.requestQueue_request_lock_delete.v1':
            return await self._requestQueue_request_lock_delete(args)
        if method_id == 'apify.requestQueue_request_lock_put.v1':
            return await self._requestQueue_request_lock_put(args)
        if method_id == 'apify.requestQueue_request_put.v1':
            return await self._requestQueue_request_put(args)
        if method_id == 'apify.requestQueue_requests_batch_delete.v1':
            return await self._requestQueue_requests_batch_delete(args)
        if method_id == 'apify.requestQueue_requests_batch_post.v1':
            return await self._requestQueue_requests_batch_post(args)
        if method_id == 'apify.requestQueue_requests_get.v1':
            return await self._requestQueue_requests_get(args)
        if method_id == 'apify.requestQueue_requests_post.v1':
            return await self._requestQueue_requests_post(args)
        if method_id == 'apify.requestQueue_requests_unlock_post.v1':
            return await self._requestQueue_requests_unlock_post(args)
        if method_id == 'apify.requestQueues_get.v1':
            return await self._requestQueues_get(args)
        if method_id == 'apify.requestQueues_post.v1':
            return await self._requestQueues_post(args)
        if method_id == 'apify.schedule_delete.v1':
            return await self._schedule_delete(args)
        if method_id == 'apify.schedule_get.v1':
            return await self._schedule_get(args)
        if method_id == 'apify.schedule_log_get.v1':
            return await self._schedule_log_get(args)
        if method_id == 'apify.schedule_put.v1':
            return await self._schedule_put(args)
        if method_id == 'apify.schedules_get.v1':
            return await self._schedules_get(args)
        if method_id == 'apify.schedules_post.v1':
            return await self._schedules_post(args)
        if method_id == 'apify.store_get.v1':
            return await self._store_get(args)
        if method_id == 'apify.user_get.v1':
            return await self._user_get(args)
        if method_id == 'apify.users_me_get.v1':
            return await self._users_me_get(args)
        if method_id == 'apify.users_me_limits_get.v1':
            return await self._users_me_limits_get(args)
        if method_id == 'apify.users_me_limits_put.v1':
            return await self._users_me_limits_put(args)
        if method_id == 'apify.users_me_usage_monthly_get.v1':
            return await self._users_me_usage_monthly_get(args)
        if method_id == 'apify.webhookDispatch_get.v1':
            return await self._webhookDispatch_get(args)
        if method_id == 'apify.webhookDispatches_get.v1':
            return await self._webhookDispatches_get(args)
        if method_id == 'apify.webhook_delete.v1':
            return await self._webhook_delete(args)
        if method_id == 'apify.webhook_get.v1':
            return await self._webhook_get(args)
        if method_id == 'apify.webhook_put.v1':
            return await self._webhook_put(args)
        if method_id == 'apify.webhook_test_post.v1':
            return await self._webhook_test_post(args)
        if method_id == 'apify.webhook_webhookDispatches_get.v1':
            return await self._webhook_webhookDispatches_get(args)
        if method_id == 'apify.webhooks_get.v1':
            return await self._webhooks_get(args)
        if method_id == 'apify.webhooks_post.v1':
            return await self._webhooks_post(args)
        return json.dumps({"ok": False, "provider": PROVIDER_NAME, "error_code": "METHOD_UNKNOWN", "method_id": method_id}, indent=2, ensure_ascii=False)

    def _path_params(self, args: Dict[str, Any], names: list[str]) -> Dict[str, str]:
        result = {}
        missing = []
        for name in names:
            value = args.get(name)
            if value is None or value == "":
                missing.append(name)
                continue
            result[name] = quote(str(value), safe="~")
        if missing:
            raise ValueError(f"Missing required path params: {', '.join(missing)}")
        return result

    def _query_params(self, args: Dict[str, Any], names: list[str]) -> Dict[str, Any]:
        return {name: args[name] for name in names if args.get(name) is not None}

    def _content_type(self, default_content_types: list[str], args: Dict[str, Any]) -> str:
        explicit = str(args.get("content_type", "")).strip()
        if explicit:
            return explicit
        if "application/json" in default_content_types:
            return "application/json"
        if default_content_types:
            return str(default_content_types[0])
        return "application/json"

    async def _request(
        self,
        *,
        method_id: str,
        http_method: str,
        path: str,
        path_params: Dict[str, str],
        query: Dict[str, Any],
        has_request_body: bool,
        request_content_types: list[str],
        args: Dict[str, Any],
    ) -> str:
        token = self._token()
        headers_obj = args.get("headers") or {}
        if not isinstance(headers_obj, dict):
            return self._invalid_args(method_id, "headers must be an object when provided.")
        headers = {k: str(v) for k, v in headers_obj.items()}
        if token and "Authorization" not in headers:
            headers["Authorization"] = f"Bearer {token}"
        accept = str(args.get("accept", "")).strip()
        if accept and "Accept" not in headers:
            headers["Accept"] = accept
        try:
            timeout_seconds = float(args.get("timeout_seconds", _TIMEOUT))
        except (TypeError, ValueError) as e:
            return self._invalid_args(method_id, f"Invalid timeout_seconds: {type(e).__name__}: {e}")
        if timeout_seconds <= 0:
            return self._invalid_args(method_id, "timeout_seconds must be > 0.")
        url = _BASE_URL + path.format(**path_params)
        request_kwargs: Dict[str, Any] = {"params": query, "headers": headers}
        has_body = "body" in args
        has_body_base64 = "body_base64" in args
        if has_body and has_body_base64:
            return self._invalid_args(method_id, "Provide either body or body_base64, not both.")
        if not has_request_body and (has_body or has_body_base64):
            return self._invalid_args(method_id, "This method does not accept a request body.")
        if has_request_body:
            content_type = self._content_type(request_content_types, args)
            if "Content-Type" not in headers:
                headers["Content-Type"] = content_type
            if has_body_base64:
                try:
                    request_kwargs["content"] = base64.b64decode(str(args.get("body_base64", "")))
                except (ValueError, TypeError) as e:
                    return self._invalid_args(method_id, f"Invalid body_base64: {type(e).__name__}: {e}")
            else:
                body = args.get("body")
                if content_type.startswith("application/json"):
                    request_kwargs["json"] = body
                elif isinstance(body, str):
                    request_kwargs["content"] = body.encode("utf-8")
                elif body is not None:
                    request_kwargs["content"] = json.dumps(body, ensure_ascii=False).encode("utf-8")
        try:
            async with httpx.AsyncClient(timeout=timeout_seconds, follow_redirects=bool(args.get("follow_redirects", False))) as client:
                response = await client.request(http_method, url, **request_kwargs)
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "provider": PROVIDER_NAME, "method_id": method_id, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError) as e:
            logger.error("apify request failed method=%s", method_id, exc_info=e)
            return json.dumps({"ok": False, "provider": PROVIDER_NAME, "method_id": method_id, "error_code": "HTTP_ERROR", "message": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)
        return self._format_response(method_id, response)

    def _format_response(self, method_id: str, response: httpx.Response) -> str:
        if response.status_code >= 400:
            return self._provider_error(method_id, response)
        content_type = response.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        result: Dict[str, Any] = {
            "status_code": response.status_code,
            "content_type": content_type or None,
            "url": str(response.request.url),
            "headers": dict(response.headers),
        }
        if response.request.method == "HEAD":
            result["body"] = None
        elif content_type.startswith("application/json"):
            try:
                result["body"] = response.json()
            except json.JSONDecodeError:
                result["body"] = response.text
        elif self._is_text_content_type(content_type):
            result["body"] = response.text
        elif not response.content:
            result["body"] = ""
        else:
            result["body_base64"] = base64.b64encode(response.content).decode("ascii")
            result["body_size"] = len(response.content)
        return json.dumps({"ok": True, "provider": PROVIDER_NAME, "method_id": method_id, "result": result}, indent=2, ensure_ascii=False)

    def _provider_error(self, method_id: str, response: httpx.Response) -> str:
        try:
            detail: Any = response.json()
        except json.JSONDecodeError:
            detail = response.text[:1000]
        logger.info("apify api error method=%s status=%s body=%s", method_id, response.status_code, response.text[:300])
        return json.dumps({"ok": False, "provider": PROVIDER_NAME, "method_id": method_id, "error_code": "PROVIDER_ERROR", "http_status": response.status_code, "detail": detail}, indent=2, ensure_ascii=False)

    def _invalid_args(self, method_id: str, message: str) -> str:
        return json.dumps({"ok": False, "provider": PROVIDER_NAME, "method_id": method_id, "error_code": "INVALID_ARGS", "message": message}, indent=2, ensure_ascii=False)

    def _is_text_content_type(self, content_type: str) -> bool:
        if not content_type:
            return True
        return content_type.startswith(_TEXT_RESPONSE_PREFIXES)

    async def _PostChargeRun(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['runId'])
        except ValueError as e:
            return self._invalid_args('apify.PostChargeRun.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.PostChargeRun.v1',
            http_method='POST',
            path='/v2/actor-runs/{runId}/charge',
            path_params=path_params,
            query=query,
            has_request_body=True,
            request_content_types=['application/json'],
            args=args,
        )

    async def _PostResurrectRun(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['runId'])
        except ValueError as e:
            return self._invalid_args('apify.PostResurrectRun.v1', str(e))
        query = self._query_params(args, ['build', 'memory', 'restartOnError', 'timeout'])
        return await self._request(
            method_id='apify.PostResurrectRun.v1',
            http_method='POST',
            path='/v2/actor-runs/{runId}/resurrect',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _act_build_abort_post(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorId', 'buildId'])
        except ValueError as e:
            return self._invalid_args('apify.act_build_abort_post.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.act_build_abort_post.v1',
            http_method='POST',
            path='/v2/acts/{actorId}/builds/{buildId}/abort',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _act_build_default_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorId'])
        except ValueError as e:
            return self._invalid_args('apify.act_build_default_get.v1', str(e))
        query = self._query_params(args, ['waitForFinish'])
        return await self._request(
            method_id='apify.act_build_default_get.v1',
            http_method='GET',
            path='/v2/acts/{actorId}/builds/default',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _act_build_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorId', 'buildId'])
        except ValueError as e:
            return self._invalid_args('apify.act_build_get.v1', str(e))
        query = self._query_params(args, ['waitForFinish'])
        return await self._request(
            method_id='apify.act_build_get.v1',
            http_method='GET',
            path='/v2/acts/{actorId}/builds/{buildId}',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _act_builds_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorId'])
        except ValueError as e:
            return self._invalid_args('apify.act_builds_get.v1', str(e))
        query = self._query_params(args, ['desc', 'limit', 'offset'])
        return await self._request(
            method_id='apify.act_builds_get.v1',
            http_method='GET',
            path='/v2/acts/{actorId}/builds',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _act_builds_post(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorId'])
        except ValueError as e:
            return self._invalid_args('apify.act_builds_post.v1', str(e))
        query = self._query_params(args, ['betaPackages', 'tag', 'useCache', 'version', 'waitForFinish'])
        return await self._request(
            method_id='apify.act_builds_post.v1',
            http_method='POST',
            path='/v2/acts/{actorId}/builds',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _act_delete(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorId'])
        except ValueError as e:
            return self._invalid_args('apify.act_delete.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.act_delete.v1',
            http_method='DELETE',
            path='/v2/acts/{actorId}',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _act_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorId'])
        except ValueError as e:
            return self._invalid_args('apify.act_get.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.act_get.v1',
            http_method='GET',
            path='/v2/acts/{actorId}',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _act_openapi_json_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorId', 'buildId'])
        except ValueError as e:
            return self._invalid_args('apify.act_openapi_json_get.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.act_openapi_json_get.v1',
            http_method='GET',
            path='/v2/acts/{actorId}/builds/{buildId}/openapi.json',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _act_put(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorId'])
        except ValueError as e:
            return self._invalid_args('apify.act_put.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.act_put.v1',
            http_method='PUT',
            path='/v2/acts/{actorId}',
            path_params=path_params,
            query=query,
            has_request_body=True,
            request_content_types=['application/json'],
            args=args,
        )

    async def _act_runSyncGetDatasetItems_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorId'])
        except ValueError as e:
            return self._invalid_args('apify.act_runSyncGetDatasetItems_get.v1', str(e))
        query = self._query_params(args, ['attachment', 'bom', 'build', 'clean', 'delimiter', 'desc', 'fields', 'flatten', 'format', 'limit', 'memory', 'offset', 'omit', 'restartOnError', 'simplified', 'skipEmpty', 'skipFailedPages', 'skipHeaderRow', 'skipHidden', 'timeout', 'unwind', 'webhooks', 'xmlRoot', 'xmlRow'])
        return await self._request(
            method_id='apify.act_runSyncGetDatasetItems_get.v1',
            http_method='GET',
            path='/v2/acts/{actorId}/run-sync-get-dataset-items',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _act_runSyncGetDatasetItems_post(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorId'])
        except ValueError as e:
            return self._invalid_args('apify.act_runSyncGetDatasetItems_post.v1', str(e))
        query = self._query_params(args, ['attachment', 'bom', 'build', 'clean', 'delimiter', 'desc', 'fields', 'flatten', 'format', 'limit', 'memory', 'offset', 'omit', 'restartOnError', 'simplified', 'skipEmpty', 'skipFailedPages', 'skipHeaderRow', 'skipHidden', 'timeout', 'unwind', 'webhooks', 'xmlRoot', 'xmlRow'])
        return await self._request(
            method_id='apify.act_runSyncGetDatasetItems_post.v1',
            http_method='POST',
            path='/v2/acts/{actorId}/run-sync-get-dataset-items',
            path_params=path_params,
            query=query,
            has_request_body=True,
            request_content_types=['application/json'],
            args=args,
        )

    async def _act_runSync_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorId'])
        except ValueError as e:
            return self._invalid_args('apify.act_runSync_get.v1', str(e))
        query = self._query_params(args, ['build', 'memory', 'outputRecordKey', 'restartOnError', 'timeout', 'webhooks'])
        return await self._request(
            method_id='apify.act_runSync_get.v1',
            http_method='GET',
            path='/v2/acts/{actorId}/run-sync',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _act_runSync_post(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorId'])
        except ValueError as e:
            return self._invalid_args('apify.act_runSync_post.v1', str(e))
        query = self._query_params(args, ['build', 'memory', 'outputRecordKey', 'restartOnError', 'timeout', 'webhooks'])
        return await self._request(
            method_id='apify.act_runSync_post.v1',
            http_method='POST',
            path='/v2/acts/{actorId}/run-sync',
            path_params=path_params,
            query=query,
            has_request_body=True,
            request_content_types=['application/json'],
            args=args,
        )

    async def _act_run_abort_post(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorId', 'runId'])
        except ValueError as e:
            return self._invalid_args('apify.act_run_abort_post.v1', str(e))
        query = self._query_params(args, ['gracefully'])
        return await self._request(
            method_id='apify.act_run_abort_post.v1',
            http_method='POST',
            path='/v2/acts/{actorId}/runs/{runId}/abort',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _act_run_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorId', 'runId'])
        except ValueError as e:
            return self._invalid_args('apify.act_run_get.v1', str(e))
        query = self._query_params(args, ['waitForFinish'])
        return await self._request(
            method_id='apify.act_run_get.v1',
            http_method='GET',
            path='/v2/acts/{actorId}/runs/{runId}',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _act_run_metamorph_post(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorId', 'runId'])
        except ValueError as e:
            return self._invalid_args('apify.act_run_metamorph_post.v1', str(e))
        query = self._query_params(args, ['build', 'targetActorId'])
        return await self._request(
            method_id='apify.act_run_metamorph_post.v1',
            http_method='POST',
            path='/v2/acts/{actorId}/runs/{runId}/metamorph',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _act_run_resurrect_post(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorId', 'runId'])
        except ValueError as e:
            return self._invalid_args('apify.act_run_resurrect_post.v1', str(e))
        query = self._query_params(args, ['build', 'memory', 'restartOnError', 'timeout'])
        return await self._request(
            method_id='apify.act_run_resurrect_post.v1',
            http_method='POST',
            path='/v2/acts/{actorId}/runs/{runId}/resurrect',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _act_runs_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorId'])
        except ValueError as e:
            return self._invalid_args('apify.act_runs_get.v1', str(e))
        query = self._query_params(args, ['desc', 'limit', 'offset', 'startedAfter', 'startedBefore', 'status'])
        return await self._request(
            method_id='apify.act_runs_get.v1',
            http_method='GET',
            path='/v2/acts/{actorId}/runs',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _act_runs_last_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorId'])
        except ValueError as e:
            return self._invalid_args('apify.act_runs_last_get.v1', str(e))
        query = self._query_params(args, ['status'])
        return await self._request(
            method_id='apify.act_runs_last_get.v1',
            http_method='GET',
            path='/v2/acts/{actorId}/runs/last',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _act_runs_post(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorId'])
        except ValueError as e:
            return self._invalid_args('apify.act_runs_post.v1', str(e))
        query = self._query_params(args, ['build', 'forcePermissionLevel', 'memory', 'restartOnError', 'timeout', 'waitForFinish', 'webhooks'])
        return await self._request(
            method_id='apify.act_runs_post.v1',
            http_method='POST',
            path='/v2/acts/{actorId}/runs',
            path_params=path_params,
            query=query,
            has_request_body=True,
            request_content_types=['application/json'],
            args=args,
        )

    async def _act_version_delete(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorId', 'versionNumber'])
        except ValueError as e:
            return self._invalid_args('apify.act_version_delete.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.act_version_delete.v1',
            http_method='DELETE',
            path='/v2/acts/{actorId}/versions/{versionNumber}',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _act_version_envVar_delete(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorId', 'envVarName', 'versionNumber'])
        except ValueError as e:
            return self._invalid_args('apify.act_version_envVar_delete.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.act_version_envVar_delete.v1',
            http_method='DELETE',
            path='/v2/acts/{actorId}/versions/{versionNumber}/env-vars/{envVarName}',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _act_version_envVar_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorId', 'envVarName', 'versionNumber'])
        except ValueError as e:
            return self._invalid_args('apify.act_version_envVar_get.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.act_version_envVar_get.v1',
            http_method='GET',
            path='/v2/acts/{actorId}/versions/{versionNumber}/env-vars/{envVarName}',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _act_version_envVar_put(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorId', 'envVarName', 'versionNumber'])
        except ValueError as e:
            return self._invalid_args('apify.act_version_envVar_put.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.act_version_envVar_put.v1',
            http_method='PUT',
            path='/v2/acts/{actorId}/versions/{versionNumber}/env-vars/{envVarName}',
            path_params=path_params,
            query=query,
            has_request_body=True,
            request_content_types=['application/json'],
            args=args,
        )

    async def _act_version_envVars_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorId', 'versionNumber'])
        except ValueError as e:
            return self._invalid_args('apify.act_version_envVars_get.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.act_version_envVars_get.v1',
            http_method='GET',
            path='/v2/acts/{actorId}/versions/{versionNumber}/env-vars',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _act_version_envVars_post(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorId', 'versionNumber'])
        except ValueError as e:
            return self._invalid_args('apify.act_version_envVars_post.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.act_version_envVars_post.v1',
            http_method='POST',
            path='/v2/acts/{actorId}/versions/{versionNumber}/env-vars',
            path_params=path_params,
            query=query,
            has_request_body=True,
            request_content_types=['application/json'],
            args=args,
        )

    async def _act_version_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorId', 'versionNumber'])
        except ValueError as e:
            return self._invalid_args('apify.act_version_get.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.act_version_get.v1',
            http_method='GET',
            path='/v2/acts/{actorId}/versions/{versionNumber}',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _act_version_put(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorId', 'versionNumber'])
        except ValueError as e:
            return self._invalid_args('apify.act_version_put.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.act_version_put.v1',
            http_method='PUT',
            path='/v2/acts/{actorId}/versions/{versionNumber}',
            path_params=path_params,
            query=query,
            has_request_body=True,
            request_content_types=['application/json'],
            args=args,
        )

    async def _act_versions_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorId'])
        except ValueError as e:
            return self._invalid_args('apify.act_versions_get.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.act_versions_get.v1',
            http_method='GET',
            path='/v2/acts/{actorId}/versions',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _act_versions_post(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorId'])
        except ValueError as e:
            return self._invalid_args('apify.act_versions_post.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.act_versions_post.v1',
            http_method='POST',
            path='/v2/acts/{actorId}/versions',
            path_params=path_params,
            query=query,
            has_request_body=True,
            request_content_types=['application/json'],
            args=args,
        )

    async def _act_webhooks_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorId'])
        except ValueError as e:
            return self._invalid_args('apify.act_webhooks_get.v1', str(e))
        query = self._query_params(args, ['desc', 'limit', 'offset'])
        return await self._request(
            method_id='apify.act_webhooks_get.v1',
            http_method='GET',
            path='/v2/acts/{actorId}/webhooks',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _actorBuild_abort_post(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['buildId'])
        except ValueError as e:
            return self._invalid_args('apify.actorBuild_abort_post.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.actorBuild_abort_post.v1',
            http_method='POST',
            path='/v2/actor-builds/{buildId}/abort',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _actorBuild_delete(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['buildId'])
        except ValueError as e:
            return self._invalid_args('apify.actorBuild_delete.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.actorBuild_delete.v1',
            http_method='DELETE',
            path='/v2/actor-builds/{buildId}',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _actorBuild_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['buildId'])
        except ValueError as e:
            return self._invalid_args('apify.actorBuild_get.v1', str(e))
        query = self._query_params(args, ['waitForFinish'])
        return await self._request(
            method_id='apify.actorBuild_get.v1',
            http_method='GET',
            path='/v2/actor-builds/{buildId}',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _actorBuild_log_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['buildId'])
        except ValueError as e:
            return self._invalid_args('apify.actorBuild_log_get.v1', str(e))
        query = self._query_params(args, ['download', 'stream'])
        return await self._request(
            method_id='apify.actorBuild_log_get.v1',
            http_method='GET',
            path='/v2/actor-builds/{buildId}/log',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _actorBuild_openapi_json_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['buildId'])
        except ValueError as e:
            return self._invalid_args('apify.actorBuild_openapi_json_get.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.actorBuild_openapi_json_get.v1',
            http_method='GET',
            path='/v2/actor-builds/{buildId}/openapi.json',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _actorBuilds_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.actorBuilds_get.v1', str(e))
        query = self._query_params(args, ['desc', 'limit', 'offset'])
        return await self._request(
            method_id='apify.actorBuilds_get.v1',
            http_method='GET',
            path='/v2/actor-builds',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _actorRun_abort_post(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['runId'])
        except ValueError as e:
            return self._invalid_args('apify.actorRun_abort_post.v1', str(e))
        query = self._query_params(args, ['gracefully'])
        return await self._request(
            method_id='apify.actorRun_abort_post.v1',
            http_method='POST',
            path='/v2/actor-runs/{runId}/abort',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _actorRun_delete(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['runId'])
        except ValueError as e:
            return self._invalid_args('apify.actorRun_delete.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.actorRun_delete.v1',
            http_method='DELETE',
            path='/v2/actor-runs/{runId}',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _actorRun_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['runId'])
        except ValueError as e:
            return self._invalid_args('apify.actorRun_get.v1', str(e))
        query = self._query_params(args, ['waitForFinish'])
        return await self._request(
            method_id='apify.actorRun_get.v1',
            http_method='GET',
            path='/v2/actor-runs/{runId}',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _actorRun_metamorph_post(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['runId'])
        except ValueError as e:
            return self._invalid_args('apify.actorRun_metamorph_post.v1', str(e))
        query = self._query_params(args, ['build', 'targetActorId'])
        return await self._request(
            method_id='apify.actorRun_metamorph_post.v1',
            http_method='POST',
            path='/v2/actor-runs/{runId}/metamorph',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _actorRun_put(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['runId'])
        except ValueError as e:
            return self._invalid_args('apify.actorRun_put.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.actorRun_put.v1',
            http_method='PUT',
            path='/v2/actor-runs/{runId}',
            path_params=path_params,
            query=query,
            has_request_body=True,
            request_content_types=['application/json'],
            args=args,
        )

    async def _actorRun_reboot_post(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['runId'])
        except ValueError as e:
            return self._invalid_args('apify.actorRun_reboot_post.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.actorRun_reboot_post.v1',
            http_method='POST',
            path='/v2/actor-runs/{runId}/reboot',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _actorRuns_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.actorRuns_get.v1', str(e))
        query = self._query_params(args, ['desc', 'limit', 'offset', 'startedAfter', 'startedBefore', 'status'])
        return await self._request(
            method_id='apify.actorRuns_get.v1',
            http_method='GET',
            path='/v2/actor-runs',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _actorTask_delete(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorTaskId'])
        except ValueError as e:
            return self._invalid_args('apify.actorTask_delete.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.actorTask_delete.v1',
            http_method='DELETE',
            path='/v2/actor-tasks/{actorTaskId}',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _actorTask_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorTaskId'])
        except ValueError as e:
            return self._invalid_args('apify.actorTask_get.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.actorTask_get.v1',
            http_method='GET',
            path='/v2/actor-tasks/{actorTaskId}',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _actorTask_input_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorTaskId'])
        except ValueError as e:
            return self._invalid_args('apify.actorTask_input_get.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.actorTask_input_get.v1',
            http_method='GET',
            path='/v2/actor-tasks/{actorTaskId}/input',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _actorTask_input_put(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorTaskId'])
        except ValueError as e:
            return self._invalid_args('apify.actorTask_input_put.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.actorTask_input_put.v1',
            http_method='PUT',
            path='/v2/actor-tasks/{actorTaskId}/input',
            path_params=path_params,
            query=query,
            has_request_body=True,
            request_content_types=['application/json'],
            args=args,
        )

    async def _actorTask_put(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorTaskId'])
        except ValueError as e:
            return self._invalid_args('apify.actorTask_put.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.actorTask_put.v1',
            http_method='PUT',
            path='/v2/actor-tasks/{actorTaskId}',
            path_params=path_params,
            query=query,
            has_request_body=True,
            request_content_types=['application/json'],
            args=args,
        )

    async def _actorTask_runSyncGetDatasetItems_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorTaskId'])
        except ValueError as e:
            return self._invalid_args('apify.actorTask_runSyncGetDatasetItems_get.v1', str(e))
        query = self._query_params(args, ['attachment', 'bom', 'build', 'clean', 'delimiter', 'desc', 'fields', 'flatten', 'format', 'limit', 'memory', 'offset', 'omit', 'simplified', 'skipEmpty', 'skipFailedPages', 'skipHeaderRow', 'skipHidden', 'timeout', 'unwind', 'webhooks', 'xmlRoot', 'xmlRow'])
        return await self._request(
            method_id='apify.actorTask_runSyncGetDatasetItems_get.v1',
            http_method='GET',
            path='/v2/actor-tasks/{actorTaskId}/run-sync-get-dataset-items',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _actorTask_runSyncGetDatasetItems_post(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorTaskId'])
        except ValueError as e:
            return self._invalid_args('apify.actorTask_runSyncGetDatasetItems_post.v1', str(e))
        query = self._query_params(args, ['attachment', 'bom', 'build', 'clean', 'delimiter', 'desc', 'fields', 'flatten', 'format', 'limit', 'memory', 'offset', 'omit', 'restartOnError', 'simplified', 'skipEmpty', 'skipFailedPages', 'skipHeaderRow', 'skipHidden', 'timeout', 'unwind', 'webhooks', 'xmlRoot', 'xmlRow'])
        return await self._request(
            method_id='apify.actorTask_runSyncGetDatasetItems_post.v1',
            http_method='POST',
            path='/v2/actor-tasks/{actorTaskId}/run-sync-get-dataset-items',
            path_params=path_params,
            query=query,
            has_request_body=True,
            request_content_types=['application/json'],
            args=args,
        )

    async def _actorTask_runSync_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorTaskId'])
        except ValueError as e:
            return self._invalid_args('apify.actorTask_runSync_get.v1', str(e))
        query = self._query_params(args, ['build', 'memory', 'outputRecordKey', 'timeout', 'webhooks'])
        return await self._request(
            method_id='apify.actorTask_runSync_get.v1',
            http_method='GET',
            path='/v2/actor-tasks/{actorTaskId}/run-sync',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _actorTask_runSync_post(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorTaskId'])
        except ValueError as e:
            return self._invalid_args('apify.actorTask_runSync_post.v1', str(e))
        query = self._query_params(args, ['build', 'memory', 'outputRecordKey', 'restartOnError', 'timeout', 'webhooks'])
        return await self._request(
            method_id='apify.actorTask_runSync_post.v1',
            http_method='POST',
            path='/v2/actor-tasks/{actorTaskId}/run-sync',
            path_params=path_params,
            query=query,
            has_request_body=True,
            request_content_types=['application/json'],
            args=args,
        )

    async def _actorTask_runs_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorTaskId'])
        except ValueError as e:
            return self._invalid_args('apify.actorTask_runs_get.v1', str(e))
        query = self._query_params(args, ['desc', 'limit', 'offset', 'status'])
        return await self._request(
            method_id='apify.actorTask_runs_get.v1',
            http_method='GET',
            path='/v2/actor-tasks/{actorTaskId}/runs',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _actorTask_runs_last_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorTaskId'])
        except ValueError as e:
            return self._invalid_args('apify.actorTask_runs_last_get.v1', str(e))
        query = self._query_params(args, ['status'])
        return await self._request(
            method_id='apify.actorTask_runs_last_get.v1',
            http_method='GET',
            path='/v2/actor-tasks/{actorTaskId}/runs/last',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _actorTask_runs_post(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorTaskId'])
        except ValueError as e:
            return self._invalid_args('apify.actorTask_runs_post.v1', str(e))
        query = self._query_params(args, ['build', 'memory', 'restartOnError', 'timeout', 'waitForFinish', 'webhooks'])
        return await self._request(
            method_id='apify.actorTask_runs_post.v1',
            http_method='POST',
            path='/v2/actor-tasks/{actorTaskId}/runs',
            path_params=path_params,
            query=query,
            has_request_body=True,
            request_content_types=['application/json'],
            args=args,
        )

    async def _actorTask_webhooks_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['actorTaskId'])
        except ValueError as e:
            return self._invalid_args('apify.actorTask_webhooks_get.v1', str(e))
        query = self._query_params(args, ['desc', 'limit', 'offset'])
        return await self._request(
            method_id='apify.actorTask_webhooks_get.v1',
            http_method='GET',
            path='/v2/actor-tasks/{actorTaskId}/webhooks',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _actorTasks_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.actorTasks_get.v1', str(e))
        query = self._query_params(args, ['desc', 'limit', 'offset'])
        return await self._request(
            method_id='apify.actorTasks_get.v1',
            http_method='GET',
            path='/v2/actor-tasks',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _actorTasks_post(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.actorTasks_post.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.actorTasks_post.v1',
            http_method='POST',
            path='/v2/actor-tasks',
            path_params=path_params,
            query=query,
            has_request_body=True,
            request_content_types=['application/json'],
            args=args,
        )

    async def _acts_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.acts_get.v1', str(e))
        query = self._query_params(args, ['desc', 'limit', 'my', 'offset', 'sortBy'])
        return await self._request(
            method_id='apify.acts_get.v1',
            http_method='GET',
            path='/v2/acts',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _acts_post(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.acts_post.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.acts_post.v1',
            http_method='POST',
            path='/v2/acts',
            path_params=path_params,
            query=query,
            has_request_body=True,
            request_content_types=['application/json'],
            args=args,
        )

    async def _dataset_delete(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.dataset_delete.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.dataset_delete.v1',
            http_method='DELETE',
            path='/v2/datasets/{datasetId}',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _dataset_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.dataset_get.v1', str(e))
        query = self._query_params(args, ['token'])
        return await self._request(
            method_id='apify.dataset_get.v1',
            http_method='GET',
            path='/v2/datasets/{datasetId}',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _dataset_items_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.dataset_items_get.v1', str(e))
        query = self._query_params(args, ['attachment', 'bom', 'clean', 'delimiter', 'fields', 'flatten', 'format', 'limit', 'omit', 'simplified', 'skipEmpty', 'skipFailedPages', 'skipHeaderRow', 'skipHidden', 'unwind', 'view', 'xmlRoot', 'xmlRow'])
        return await self._request(
            method_id='apify.dataset_items_get.v1',
            http_method='GET',
            path='/v2/datasets/{datasetId}/items',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _dataset_items_post(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.dataset_items_post.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.dataset_items_post.v1',
            http_method='POST',
            path='/v2/datasets/{datasetId}/items',
            path_params=path_params,
            query=query,
            has_request_body=True,
            request_content_types=['application/json'],
            args=args,
        )

    async def _dataset_put(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.dataset_put.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.dataset_put.v1',
            http_method='PUT',
            path='/v2/datasets/{datasetId}',
            path_params=path_params,
            query=query,
            has_request_body=True,
            request_content_types=['application/json'],
            args=args,
        )

    async def _dataset_statistics_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.dataset_statistics_get.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.dataset_statistics_get.v1',
            http_method='GET',
            path='/v2/datasets/{datasetId}/statistics',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _datasets_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.datasets_get.v1', str(e))
        query = self._query_params(args, ['ownership'])
        return await self._request(
            method_id='apify.datasets_get.v1',
            http_method='GET',
            path='/v2/datasets',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _datasets_post(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.datasets_post.v1', str(e))
        query = self._query_params(args, ['name'])
        return await self._request(
            method_id='apify.datasets_post.v1',
            http_method='POST',
            path='/v2/datasets',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _keyValueStore_delete(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.keyValueStore_delete.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.keyValueStore_delete.v1',
            http_method='DELETE',
            path='/v2/key-value-stores/{storeId}',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _keyValueStore_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.keyValueStore_get.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.keyValueStore_get.v1',
            http_method='GET',
            path='/v2/key-value-stores/{storeId}',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _keyValueStore_keys_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.keyValueStore_keys_get.v1', str(e))
        query = self._query_params(args, ['collection', 'exclusiveStartKey', 'limit', 'prefix'])
        return await self._request(
            method_id='apify.keyValueStore_keys_get.v1',
            http_method='GET',
            path='/v2/key-value-stores/{storeId}/keys',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _keyValueStore_put(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.keyValueStore_put.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.keyValueStore_put.v1',
            http_method='PUT',
            path='/v2/key-value-stores/{storeId}',
            path_params=path_params,
            query=query,
            has_request_body=True,
            request_content_types=['application/json'],
            args=args,
        )

    async def _keyValueStore_record_delete(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.keyValueStore_record_delete.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.keyValueStore_record_delete.v1',
            http_method='DELETE',
            path='/v2/key-value-stores/{storeId}/records/{recordKey}',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _keyValueStore_record_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.keyValueStore_record_get.v1', str(e))
        query = self._query_params(args, ['attachment'])
        return await self._request(
            method_id='apify.keyValueStore_record_get.v1',
            http_method='GET',
            path='/v2/key-value-stores/{storeId}/records/{recordKey}',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _keyValueStore_record_head(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.keyValueStore_record_head.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.keyValueStore_record_head.v1',
            http_method='HEAD',
            path='/v2/key-value-stores/{storeId}/records/{recordKey}',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _keyValueStore_record_put(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.keyValueStore_record_put.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.keyValueStore_record_put.v1',
            http_method='PUT',
            path='/v2/key-value-stores/{storeId}/records/{recordKey}',
            path_params=path_params,
            query=query,
            has_request_body=True,
            request_content_types=['application/json'],
            args=args,
        )

    async def _keyValueStores_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.keyValueStores_get.v1', str(e))
        query = self._query_params(args, ['ownership'])
        return await self._request(
            method_id='apify.keyValueStores_get.v1',
            http_method='GET',
            path='/v2/key-value-stores',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _keyValueStores_post(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.keyValueStores_post.v1', str(e))
        query = self._query_params(args, ['name'])
        return await self._request(
            method_id='apify.keyValueStores_post.v1',
            http_method='POST',
            path='/v2/key-value-stores',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _log_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['buildOrRunId'])
        except ValueError as e:
            return self._invalid_args('apify.log_get.v1', str(e))
        query = self._query_params(args, ['download', 'raw', 'stream'])
        return await self._request(
            method_id='apify.log_get.v1',
            http_method='GET',
            path='/v2/logs/{buildOrRunId}',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _requestQueue_delete(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.requestQueue_delete.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.requestQueue_delete.v1',
            http_method='DELETE',
            path='/v2/request-queues/{queueId}',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _requestQueue_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.requestQueue_get.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.requestQueue_get.v1',
            http_method='GET',
            path='/v2/request-queues/{queueId}',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _requestQueue_head_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.requestQueue_head_get.v1', str(e))
        query = self._query_params(args, ['limit'])
        return await self._request(
            method_id='apify.requestQueue_head_get.v1',
            http_method='GET',
            path='/v2/request-queues/{queueId}/head',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _requestQueue_head_lock_post(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.requestQueue_head_lock_post.v1', str(e))
        query = self._query_params(args, ['limit'])
        return await self._request(
            method_id='apify.requestQueue_head_lock_post.v1',
            http_method='POST',
            path='/v2/request-queues/{queueId}/head/lock',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _requestQueue_put(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.requestQueue_put.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.requestQueue_put.v1',
            http_method='PUT',
            path='/v2/request-queues/{queueId}',
            path_params=path_params,
            query=query,
            has_request_body=True,
            request_content_types=['application/json'],
            args=args,
        )

    async def _requestQueue_request_delete(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.requestQueue_request_delete.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.requestQueue_request_delete.v1',
            http_method='DELETE',
            path='/v2/request-queues/{queueId}/requests/{requestId}',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _requestQueue_request_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.requestQueue_request_get.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.requestQueue_request_get.v1',
            http_method='GET',
            path='/v2/request-queues/{queueId}/requests/{requestId}',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _requestQueue_request_lock_delete(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.requestQueue_request_lock_delete.v1', str(e))
        query = self._query_params(args, ['forefront'])
        return await self._request(
            method_id='apify.requestQueue_request_lock_delete.v1',
            http_method='DELETE',
            path='/v2/request-queues/{queueId}/requests/{requestId}/lock',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _requestQueue_request_lock_put(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.requestQueue_request_lock_put.v1', str(e))
        query = self._query_params(args, ['forefront'])
        return await self._request(
            method_id='apify.requestQueue_request_lock_put.v1',
            http_method='PUT',
            path='/v2/request-queues/{queueId}/requests/{requestId}/lock',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _requestQueue_request_put(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.requestQueue_request_put.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.requestQueue_request_put.v1',
            http_method='PUT',
            path='/v2/request-queues/{queueId}/requests/{requestId}',
            path_params=path_params,
            query=query,
            has_request_body=True,
            request_content_types=['application/json'],
            args=args,
        )

    async def _requestQueue_requests_batch_delete(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.requestQueue_requests_batch_delete.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.requestQueue_requests_batch_delete.v1',
            http_method='DELETE',
            path='/v2/request-queues/{queueId}/requests/batch',
            path_params=path_params,
            query=query,
            has_request_body=True,
            request_content_types=['application/json'],
            args=args,
        )

    async def _requestQueue_requests_batch_post(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.requestQueue_requests_batch_post.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.requestQueue_requests_batch_post.v1',
            http_method='POST',
            path='/v2/request-queues/{queueId}/requests/batch',
            path_params=path_params,
            query=query,
            has_request_body=True,
            request_content_types=['application/json'],
            args=args,
        )

    async def _requestQueue_requests_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.requestQueue_requests_get.v1', str(e))
        query = self._query_params(args, ['exclusiveStartId', 'limit'])
        return await self._request(
            method_id='apify.requestQueue_requests_get.v1',
            http_method='GET',
            path='/v2/request-queues/{queueId}/requests',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _requestQueue_requests_post(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.requestQueue_requests_post.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.requestQueue_requests_post.v1',
            http_method='POST',
            path='/v2/request-queues/{queueId}/requests',
            path_params=path_params,
            query=query,
            has_request_body=True,
            request_content_types=['application/json'],
            args=args,
        )

    async def _requestQueue_requests_unlock_post(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.requestQueue_requests_unlock_post.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.requestQueue_requests_unlock_post.v1',
            http_method='POST',
            path='/v2/request-queues/{queueId}/requests/unlock',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _requestQueues_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.requestQueues_get.v1', str(e))
        query = self._query_params(args, ['ownership'])
        return await self._request(
            method_id='apify.requestQueues_get.v1',
            http_method='GET',
            path='/v2/request-queues',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _requestQueues_post(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.requestQueues_post.v1', str(e))
        query = self._query_params(args, ['name'])
        return await self._request(
            method_id='apify.requestQueues_post.v1',
            http_method='POST',
            path='/v2/request-queues',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _schedule_delete(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['scheduleId'])
        except ValueError as e:
            return self._invalid_args('apify.schedule_delete.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.schedule_delete.v1',
            http_method='DELETE',
            path='/v2/schedules/{scheduleId}',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _schedule_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['scheduleId'])
        except ValueError as e:
            return self._invalid_args('apify.schedule_get.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.schedule_get.v1',
            http_method='GET',
            path='/v2/schedules/{scheduleId}',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _schedule_log_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['scheduleId'])
        except ValueError as e:
            return self._invalid_args('apify.schedule_log_get.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.schedule_log_get.v1',
            http_method='GET',
            path='/v2/schedules/{scheduleId}/log',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _schedule_put(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['scheduleId'])
        except ValueError as e:
            return self._invalid_args('apify.schedule_put.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.schedule_put.v1',
            http_method='PUT',
            path='/v2/schedules/{scheduleId}',
            path_params=path_params,
            query=query,
            has_request_body=True,
            request_content_types=['application/json'],
            args=args,
        )

    async def _schedules_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.schedules_get.v1', str(e))
        query = self._query_params(args, ['desc', 'limit', 'offset'])
        return await self._request(
            method_id='apify.schedules_get.v1',
            http_method='GET',
            path='/v2/schedules',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _schedules_post(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.schedules_post.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.schedules_post.v1',
            http_method='POST',
            path='/v2/schedules',
            path_params=path_params,
            query=query,
            has_request_body=True,
            request_content_types=['application/json'],
            args=args,
        )

    async def _store_get(self, args: Dict[str, Any]) -> str:
        try:
            allowed_args = {
                'method_id',
                'allowsAgenticUsers',
                'category',
                'limit',
                'offset',
                'pricingModel',
                'search',
                'sortBy',
                'username',
            }
            unknown_args = sorted(k for k in args.keys() if k not in allowed_args)
            if unknown_args:
                return self._invalid_args(
                    'apify.store_get.v1',
                    f"Unknown args: {', '.join(unknown_args)}. Allowed args: allowsAgenticUsers, category, limit, offset, pricingModel, search, sortBy, username.",
                )
            path_params = self._path_params(args, [])
            if not any(args.get(name) is not None for name in ['allowsAgenticUsers', 'category', 'pricingModel', 'search', 'username']):
                return self._invalid_args(
                    'apify.store_get.v1',
                    "At least one narrowing filter is required: allowsAgenticUsers, category, pricingModel, search, or username.",
                )
        except ValueError as e:
            return self._invalid_args('apify.store_get.v1', str(e))
        query = self._query_params(args, ['allowsAgenticUsers', 'category', 'limit', 'offset', 'pricingModel', 'search', 'sortBy', 'username'])
        if query.get('limit') is None:
            query['limit'] = 20
        return await self._request(
            method_id='apify.store_get.v1',
            http_method='GET',
            path='/v2/store',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _user_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['userId'])
        except ValueError as e:
            return self._invalid_args('apify.user_get.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.user_get.v1',
            http_method='GET',
            path='/v2/users/{userId}',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _users_me_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.users_me_get.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.users_me_get.v1',
            http_method='GET',
            path='/v2/users/me',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _users_me_limits_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.users_me_limits_get.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.users_me_limits_get.v1',
            http_method='GET',
            path='/v2/users/me/limits',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _users_me_limits_put(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.users_me_limits_put.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.users_me_limits_put.v1',
            http_method='PUT',
            path='/v2/users/me/limits',
            path_params=path_params,
            query=query,
            has_request_body=True,
            request_content_types=['application/json'],
            args=args,
        )

    async def _users_me_usage_monthly_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.users_me_usage_monthly_get.v1', str(e))
        query = self._query_params(args, ['date'])
        return await self._request(
            method_id='apify.users_me_usage_monthly_get.v1',
            http_method='GET',
            path='/v2/users/me/usage/monthly',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _webhookDispatch_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['dispatchId'])
        except ValueError as e:
            return self._invalid_args('apify.webhookDispatch_get.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.webhookDispatch_get.v1',
            http_method='GET',
            path='/v2/webhook-dispatches/{dispatchId}',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _webhookDispatches_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.webhookDispatches_get.v1', str(e))
        query = self._query_params(args, ['desc', 'limit', 'offset'])
        return await self._request(
            method_id='apify.webhookDispatches_get.v1',
            http_method='GET',
            path='/v2/webhook-dispatches',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _webhook_delete(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['webhookId'])
        except ValueError as e:
            return self._invalid_args('apify.webhook_delete.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.webhook_delete.v1',
            http_method='DELETE',
            path='/v2/webhooks/{webhookId}',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _webhook_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['webhookId'])
        except ValueError as e:
            return self._invalid_args('apify.webhook_get.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.webhook_get.v1',
            http_method='GET',
            path='/v2/webhooks/{webhookId}',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _webhook_put(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['webhookId'])
        except ValueError as e:
            return self._invalid_args('apify.webhook_put.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.webhook_put.v1',
            http_method='PUT',
            path='/v2/webhooks/{webhookId}',
            path_params=path_params,
            query=query,
            has_request_body=True,
            request_content_types=['application/json'],
            args=args,
        )

    async def _webhook_test_post(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['webhookId'])
        except ValueError as e:
            return self._invalid_args('apify.webhook_test_post.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.webhook_test_post.v1',
            http_method='POST',
            path='/v2/webhooks/{webhookId}/test',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _webhook_webhookDispatches_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, ['webhookId'])
        except ValueError as e:
            return self._invalid_args('apify.webhook_webhookDispatches_get.v1', str(e))
        query = self._query_params(args, [])
        return await self._request(
            method_id='apify.webhook_webhookDispatches_get.v1',
            http_method='GET',
            path='/v2/webhooks/{webhookId}/dispatches',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _webhooks_get(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.webhooks_get.v1', str(e))
        query = self._query_params(args, ['desc', 'limit', 'offset'])
        return await self._request(
            method_id='apify.webhooks_get.v1',
            http_method='GET',
            path='/v2/webhooks',
            path_params=path_params,
            query=query,
            has_request_body=False,
            request_content_types=[],
            args=args,
        )

    async def _webhooks_post(self, args: Dict[str, Any]) -> str:
        try:
            path_params = self._path_params(args, [])
        except ValueError as e:
            return self._invalid_args('apify.webhooks_post.v1', str(e))
        query = self._query_params(args, ['desc', 'limit', 'offset'])
        return await self._request(
            method_id='apify.webhooks_post.v1',
            http_method='POST',
            path='/v2/webhooks',
            path_params=path_params,
            query=query,
            has_request_body=True,
            request_content_types=['application/json'],
            args=args,
        )
