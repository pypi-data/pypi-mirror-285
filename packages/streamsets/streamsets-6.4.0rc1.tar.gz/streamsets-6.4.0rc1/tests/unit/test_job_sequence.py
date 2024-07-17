# Copyright 2024 StreamSets Inc.

# fmt: off
import pytest

from streamsets.sdk.sch import ControlHub
from streamsets.sdk.sch_models import Job, JobSequence, JobSequenceBuilder, Step
from streamsets.sdk.utils import SeekableList

from .conftest import JOB_SEQUENCE_BUILDER_JSON, JOB_SEQUENCE_EMPTY_JSON

# fmt: on
START_TIME_2099 = 4200268800
END_TIME_2099 = 4200268800
START_TIME_2100 = 4237401600
END_TIME_2100 = 4237996800
UTC_TIME_Z0NE = ' UTC'
BASIC_CRON_TAB_MASK = '0/1 * 1/1 * ? *'
NUM_OF_STEPS = 4
NUM_OF_JOBS = 3

JOB_SEQUENCE_HISTORY_LOG_JSON = {
    'offset': 0,
    'len': -1,
    'data': [
        {
            'id': '1293093b-6347-4faa-b337-6b4628a5efcf:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
            'timestamp': 1710290150713,
            'logMessage': "Could not update steps of sequence 'a9ce0818-0521-41aa-9057-bcd313ce7ada:a2df1e64-dd65-11ed-bee6-3bf718d3c508'. There were validation errors: 'null'",
            'logType': 'SEQUENCE_UPDATE_STEPS_VALIDATION_ERROR',
            'logLevel': 'ERROR',
            'sequenceId': 'a9ce0818-0521-41aa-9057-bcd313ce7ada:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
        },
        {
            'id': 'b68ecaa5-74a1-44ce-8058-8dcc2c290a90:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
            'timestamp': 1710290150386,
            'logMessage': "Successfully started sequence 'a9ce0818-0521-41aa-9057-bcd313ce7ada:a2df1e64-dd65-11ed-bee6-3bf718d3c508' with initial steps 'b25ed93a-d494-4604-8ffc-75075b5d957c:a2df1e64-dd65-11ed-bee6-3bf718d3c508'",
            'logType': 'SEQUENCE_START',
            'logLevel': 'INFO',
            'sequenceId': 'a9ce0818-0521-41aa-9057-bcd313ce7ada:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
        },
        {
            'id': '51c07107-09bf-4840-bfb2-c815609373ac:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
            'timestamp': 1710290149130,
            'logMessage': "Created sequence 'a9ce0818-0521-41aa-9057-bcd313ce7ada:a2df1e64-dd65-11ed-bee6-3bf718d3c508'",
            'logType': 'SEQUENCE_CREATE',
            'logLevel': 'INFO',
            'sequenceId': 'a9ce0818-0521-41aa-9057-bcd313ce7ada:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
        },
    ],
}


class MockControlHub:
    def __init__(self):
        self.api_client = MockApiClient()
        self.organization = 'DUMMY ORG'

    @property
    def _sequencing_api(self):
        return {'definitions': {'USequence': JOB_SEQUENCE_BUILDER_JSON}}


class MockApiClient:
    def __init__(self):
        self.value = 'value'

    def mark_job_as_finished(self, value):
        return MockReturn(value)

    def get_job_sequence_log_history(
        self, sequence_id, offset, len, log_type, log_level, last_run_only, run_id, from_date, to_date
    ):
        json_copy = dict(JOB_SEQUENCE_HISTORY_LOG_JSON)
        json_copy['offset'] = offset
        json_copy['len'] = -1

        for json in json_copy['data']:
            json['sequenceId'] = sequence_id
            json['logType'] = log_type
            json['logLevel'] = log_level
        return MockReturn(json_copy)

    def add_step_jobs_to_job_sequence(self, value1, value2):
        return MockReturn([value1, value2])

    def update_steps_of_job_sequence(self, value1, value2):
        return MockReturn([value1, value2])


class MockReturn:
    def __init__(self, value):
        self.response = MockResponse(value)


class MockResponse:
    def __init__(self, value):
        self.value = value

    def json(self):
        return self.value


@pytest.fixture(scope="function")
def job_sequence():
    json = {
        'id': '9fc8db2c-2465-497a-a7f8-3fcacbdb4c5e:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
        'name': 'test 1',
        'description': '',
        'organization': 'a2df1e64-dd65-11ed-bee6-3bf718d3c508',
        'createdBy': '2ad74630-dd65-11ed-bee6-9ff0bb10e1af@a2df1e64-dd65-11ed-bee6-3bf718d3c508',
        'createTime': 1709744412022,
        'lastModifiedBy': '2ad74630-dd65-11ed-bee6-9ff0bb10e1af@a2df1e64-dd65-11ed-bee6-3bf718d3c508',
        'lastModifiedTime': 1709745247332,
        'startTime': 0,
        'endTime': None,
        'timezone': 'UTC',
        'crontabMask': '0 0 1/1 * ? *',
        'steps': [
            {
                'id': '1',
                'organization': 'a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                'createdBy': '2ad74630-dd65-11ed-bee6-9ff0bb10e1af@a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                'createTime': 1709745245073,
                'lastModifiedBy': '2ad74630-dd65-11ed-bee6-9ff0bb10e1af@a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                'lastModifiedTime': 1709745245073,
                'stepNumber': 1,
                'sequenceId': '9fc8db2c-2465-497a-a7f8-3fcacbdb4c5e:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                'ignoreError': True,
                'status': 'INACTIVE',
                'type': 'JOB_STEP',
                'jobs': [
                    {
                        'id': '4993be7f-89c0-4dc7-92ef-537be78f7474:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                        'jobId': '032c6fd8-73f4-4e7a-b9f3-728e722c5658:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                        'sequenceId': '9fc8db2c-2465-497a-a7f8-3fcacbdb4c5e:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                        'stepId': 'cb817030-c625-432c-ab6b-0918f27f5a16:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                        'organization': 'a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                        'status': 'INACTIVE',
                    }
                ],
            },
            {
                'id': '2',
                'organization': 'a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                'createdBy': '2ad74630-dd65-11ed-bee6-9ff0bb10e1af@a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                'createTime': 1709745245074,
                'lastModifiedBy': '2ad74630-dd65-11ed-bee6-9ff0bb10e1af@a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                'lastModifiedTime': 1709745245074,
                'stepNumber': 2,
                'sequenceId': '9fc8db2c-2465-497a-a7f8-3fcacbdb4c5e:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                'ignoreError': True,
                'status': 'INACTIVE',
                'type': 'JOB_STEP',
                'jobs': [
                    {
                        'id': '73a06e5d-010f-49bf-9056-9562965b6784:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                        'jobId': 'ca06408d-8c88-4364-977b-00906ff0e673:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                        'sequenceId': '9fc8db2c-2465-497a-a7f8-3fcacbdb4c5e:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                        'stepId': '2c4e67ca-ef55-42fb-83ae-82a3a6d0fc2c:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                        'organization': 'a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                        'status': 'INACTIVE',
                    }
                ],
            },
            {
                'id': '3',
                'organization': 'a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                'createdBy': '2ad74630-dd65-11ed-bee6-9ff0bb10e1af@a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                'createTime': 1709745245074,
                'lastModifiedBy': '2ad74630-dd65-11ed-bee6-9ff0bb10e1af@a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                'lastModifiedTime': 1709745245074,
                'stepNumber': 3,
                'sequenceId': '9fc8db2c-2465-497a-a7f8-3fcacbdb4c5e:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                'ignoreError': True,
                'status': 'INACTIVE',
                'type': 'JOB_STEP',
                'jobs': [
                    {
                        'id': '37db1142-6b9d-4114-9d02-406c9ee5170c:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                        'jobId': '810e7bf0-01b4-4751-8ebf-e78d19f47602:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                        'sequenceId': '9fc8db2c-2465-497a-a7f8-3fcacbdb4c5e:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                        'stepId': 'e9271c6c-9a09-4b90-ab61-da6be5660522:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                        'organization': 'a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                        'status': 'INACTIVE',
                    }
                ],
            },
            {
                'id': '4',
                'organization': 'a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                'createdBy': '2ad74630-dd65-11ed-bee6-9ff0bb10e1af@a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                'createTime': 1709745245074,
                'lastModifiedBy': '2ad74630-dd65-11ed-bee6-9ff0bb10e1af@a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                'lastModifiedTime': 1709745245074,
                'stepNumber': 4,
                'sequenceId': '9fc8db2c-2465-497a-a7f8-3fcacbdb4c5e:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                'ignoreError': True,
                'status': 'INACTIVE',
                'type': 'JOB_STEP',
                'jobs': [
                    {
                        'id': '671f7e62-8cb9-4d4d-a11b-d4f7eecd1469:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                        'jobId': 'efdb14d4-43e6-4a51-a899-11dfbceb5fa8:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                        'sequenceId': '9fc8db2c-2465-497a-a7f8-3fcacbdb4c5e:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                        'stepId': '0c3558d5-7674-49d3-9c5b-b5eedc22cef0:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                        'organization': 'a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                        'status': 'INACTIVE',
                    }
                ],
            },
        ],
        'status': 'DISABLED',
        'lastRunTime': None,
        'nextRunTime': None,
    }
    return JobSequence(json, MockControlHub())


@pytest.fixture(scope="function")
def dummy_job():
    json = {
        'id': '032c6fd8-73f4-4e7a-b9f3-728e722c5658:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
        'name': 'Job for simple pipeline',
        'description': None,
        'organization': 'a2df1e64-dd65-11ed-bee6-3bf718d3c508',
        'creator': '2ad74630-dd65-11ed-bee6-9ff0bb10e1af@a2df1e64-dd65-11ed-bee6-3bf718d3c508',
        'createTime': 1706488259410,
        'lastModifiedBy': '2ad74630-dd65-11ed-bee6-9ff0bb10e1af@a2df1e64-dd65-11ed-bee6-3bf718d3c508',
        'lastModifiedOn': 1706488259410,
        'destroyer': None,
        'deleteTime': 0,
        'jobDeleted': False,
        'pipelineName': 'simple pipeline',
        'pipelineId': '1de2a77c-de5b-4fda-ba58-fdb4495542e8:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
        'pipelineCommitId': 'ab2741a2-28a1-451a-8f6c-9bf4c14433b8:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
        'rulesId': '53fa784b-95e3-429d-870b-1f9855ecfda2:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
        'pipelineCommitLabel': 'v1',
        'labels': ['dockerdep'],
        'currentJobStatus': {
            'id': '2a58e614-69b8-4650-9961-3c2300a69303:admin',
            'jobId': '810e7bf0-01b4-4751-8ebf-e78d19f47602:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
            'pipelineCommitId': 'ab2741a2-28a1-451a-8f6c-9bf4c14433b8:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
            'runCount': 1,
            'user': '2ad74630-dd65-11ed-bee6-9ff0bb10e1af@a2df1e64-dd65-11ed-bee6-3bf718d3c508',
            'startTime': 1706488680656,
            'finishTime': 0,
            'errorMessage': None,
            'color': 'RED',
            'sdcIds': ['da4e8833-b8a5-4121-a81e-bd610b7e4122'],
            'status': 'ACTIVE',
            'errorInfos': [],
            'warnings': [
                "JOBRUNNER_62 - Not responding Data Collectors execution engines '[http://3e8da0bd1150:18630]'",
                "JOBRUNNER_24 - Cannot failover Data Collectors '[http://3e8da0bd1150:18630]' as no instances available for failover",
            ],
            'ackTrackers': [
                {
                    'sdcId': 'da4e8833-b8a5-4121-a81e-bd610b7e4122',
                    'createTime': 1706488680906,
                    'ackStatus': 'SUCCESS',
                    'message': None,
                    'eventType': 'SAVE_PIPELINE',
                },
                {
                    'sdcId': 'da4e8833-b8a5-4121-a81e-bd610b7e4122',
                    'createTime': 1706488681002,
                    'ackStatus': 'SUCCESS',
                    'message': None,
                    'eventType': 'START_PIPELINE',
                },
            ],
            'pipelineOffsets': None,
            'pipelineStatus': [
                {
                    'sdcId': 'da4e8833-b8a5-4121-a81e-bd610b7e4122',
                    'name': 'simplepip__810e7bf0-01b4-4751-8ebf-e78d19f47602__a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                    'title': 'simple pipeline',
                    'jobId': '810e7bf0-01b4-4751-8ebf-e78d19f47602:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                    'localPipeline': False,
                    'status': 'RUNNING',
                    'lastReportedTime': 1706598687372,
                    'worker': [],
                    'message': None,
                    'clusterMode': False,
                }
            ],
            'upgradeStatus': None,
            'pipelineCommitLabel': None,
            'edge': False,
            'inputRecordCount': 0,
            'outputRecordCount': 0,
            'errorRecordCount': 0,
            'lastReportedMetricTime': 0,
            'enginePipelineId': 'simplepip__810e7bf0-01b4-4751-8ebf-e78d19f47602__a2df1e64-dd65-11ed-bee6-3bf718d3c508',
            'runtimeAttributes': [],
        },
        'currentUpgradeStatus': None,
        'parentJobId': None,
        'systemJobId': None,
        'numInstances': 1,
        'migrateOffsets': True,
        'statsRefreshInterval': 60000,
        'runtimeParameters': '{}',
        'edge': False,
        'timeSeries': False,
        'forceStopTimeout': 120000,
        'maxRetriesForFailedJob': -1,
        'provenanceMetaData': None,
        'jobTemplate': False,
        'templateJobId': None,
        'cdConfig': None,
        'rawJobTags': [],
        'jobTags': [],
        'executorType': 'COLLECTOR',
        'globalMaxRetries': -1,
        'needsManualAck': True,
        'staticParameters': [],
        'archived': False,
        'deleteAfterCompletion': False,
        'draftRun': False,
        'jobSequence': False,
    }
    return Job(json, MockControlHub())


@pytest.fixture(scope="function")
def dummy_jobs():
    jobs = []
    json = {
        'id': '032c6fd8-73f4-4e7a-b9f3-728e722c5658:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
        'name': 'Job for simple pipeline',
        'description': None,
        'organization': 'a2df1e64-dd65-11ed-bee6-3bf718d3c508',
        'creator': '2ad74630-dd65-11ed-bee6-9ff0bb10e1af@a2df1e64-dd65-11ed-bee6-3bf718d3c508',
        'createTime': 1706488259410,
        'lastModifiedBy': '2ad74630-dd65-11ed-bee6-9ff0bb10e1af@a2df1e64-dd65-11ed-bee6-3bf718d3c508',
        'lastModifiedOn': 1706488259410,
        'destroyer': None,
        'deleteTime': 0,
        'jobDeleted': False,
        'pipelineName': 'simple pipeline',
        'pipelineId': '1de2a77c-de5b-4fda-ba58-fdb4495542e8:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
        'pipelineCommitId': 'ab2741a2-28a1-451a-8f6c-9bf4c14433b8:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
        'rulesId': '53fa784b-95e3-429d-870b-1f9855ecfda2:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
        'pipelineCommitLabel': 'v1',
        'labels': ['dockerdep'],
        'currentJobStatus': {
            'id': '2a58e614-69b8-4650-9961-3c2300a69303:admin',
            'jobId': '810e7bf0-01b4-4751-8ebf-e78d19f47602:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
            'pipelineCommitId': 'ab2741a2-28a1-451a-8f6c-9bf4c14433b8:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
            'runCount': 1,
            'user': '2ad74630-dd65-11ed-bee6-9ff0bb10e1af@a2df1e64-dd65-11ed-bee6-3bf718d3c508',
            'startTime': 1706488680656,
            'finishTime': 0,
            'errorMessage': None,
            'color': 'RED',
            'sdcIds': ['da4e8833-b8a5-4121-a81e-bd610b7e4122'],
            'status': 'ACTIVE',
            'errorInfos': [],
            'warnings': [
                "JOBRUNNER_62 - Not responding Data Collectors execution engines '[http://3e8da0bd1150:18630]'",
                "JOBRUNNER_24 - Cannot failover Data Collectors '[http://3e8da0bd1150:18630]' as no instances available for failover",
            ],
            'ackTrackers': [
                {
                    'sdcId': 'da4e8833-b8a5-4121-a81e-bd610b7e4122',
                    'createTime': 1706488680906,
                    'ackStatus': 'SUCCESS',
                    'message': None,
                    'eventType': 'SAVE_PIPELINE',
                },
                {
                    'sdcId': 'da4e8833-b8a5-4121-a81e-bd610b7e4122',
                    'createTime': 1706488681002,
                    'ackStatus': 'SUCCESS',
                    'message': None,
                    'eventType': 'START_PIPELINE',
                },
            ],
            'pipelineOffsets': None,
            'pipelineStatus': [
                {
                    'sdcId': 'da4e8833-b8a5-4121-a81e-bd610b7e4122',
                    'name': 'simplepip__810e7bf0-01b4-4751-8ebf-e78d19f47602__a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                    'title': 'simple pipeline',
                    'jobId': '810e7bf0-01b4-4751-8ebf-e78d19f47602:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                    'localPipeline': False,
                    'status': 'RUNNING',
                    'lastReportedTime': 1706598687372,
                    'worker': [],
                    'message': None,
                    'clusterMode': False,
                }
            ],
            'upgradeStatus': None,
            'pipelineCommitLabel': None,
            'edge': False,
            'inputRecordCount': 0,
            'outputRecordCount': 0,
            'errorRecordCount': 0,
            'lastReportedMetricTime': 0,
            'enginePipelineId': 'simplepip__810e7bf0-01b4-4751-8ebf-e78d19f47602__a2df1e64-dd65-11ed-bee6-3bf718d3c508',
            'runtimeAttributes': [],
        },
        'currentUpgradeStatus': None,
        'parentJobId': None,
        'systemJobId': None,
        'numInstances': 1,
        'migrateOffsets': True,
        'statsRefreshInterval': 60000,
        'runtimeParameters': '{}',
        'edge': False,
        'timeSeries': False,
        'forceStopTimeout': 120000,
        'maxRetriesForFailedJob': -1,
        'provenanceMetaData': None,
        'jobTemplate': False,
        'templateJobId': None,
        'cdConfig': None,
        'rawJobTags': [],
        'jobTags': [],
        'executorType': 'COLLECTOR',
        'globalMaxRetries': -1,
        'needsManualAck': True,
        'staticParameters': [],
        'archived': False,
        'deleteAfterCompletion': False,
        'draftRun': False,
        'jobSequence': False,
    }
    for i in range(NUM_OF_JOBS):
        json_copy = dict(json)
        json_copy['id'] = i
        jobs.append(Job(json_copy, MockControlHub()))

    return jobs


@pytest.fixture(scope="function")
def dummy_step():
    json = {
        'id': 'ac3558d5-7674-49d3-9c5b-b5eedc22cef0:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
        'organization': 'aasf1e64-dd65-11ed-bee6-3bf718d3c508',
        'createdBy': '2ad74630-dd65-11ed-bee6-9ff0bb10e1af@a2df1e64-dd65-11ed-bee6-3bf718d3c508',
        'createTime': 1709745245074,
        'lastModifiedBy': '2ad74630-dd65-11ed-bee6-9ff0bb10e1af@a2df1e64-dd65-11ed-bee6-3bf718d3c508',
        'lastModifiedTime': 1709745245074,
        'stepNumber': 4,
        'sequenceId': '9fc8db2c-2465-497a-a7f8-3fcacbdb4c5e:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
        'ignoreError': True,
        'status': 'INACTIVE',
        'type': 'JOB_STEP',
        'jobs': [
            {
                'id': '671f7e62-8cb9-4d4d-a11b-d4f7eecd1469:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                'jobId': 'efdb14d4-43e6-4a51-a899-11dfbceb5fa8:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                'sequenceId': '9fc8db2c-2465-497a-a7f8-3fcacbdb4c5e:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                'stepId': '0c3558d5-7674-49d3-9c5b-b5eedc22cef0:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                'organization': 'a2df1e64-dd65-11ed-bee6-3bf718d3c508',
                'status': 'INACTIVE',
            }
        ],
    }
    return Step(json, MockControlHub())


def test_get_job_sequence_builder():
    job_sequence_builder = ControlHub.get_job_sequence_builder(MockControlHub())
    assert isinstance(job_sequence_builder, JobSequenceBuilder)
    assert isinstance(job_sequence_builder._control_hub, MockControlHub)

    assert job_sequence_builder._job_sequence == JOB_SEQUENCE_EMPTY_JSON

    job_sequence_builder.add_start_condition(START_TIME_2099, END_TIME_2099, UTC_TIME_Z0NE, BASIC_CRON_TAB_MASK)
    assert job_sequence_builder._job_sequence['startTime'] == START_TIME_2099
    assert job_sequence_builder._job_sequence['endTime'] == END_TIME_2099
    assert job_sequence_builder._job_sequence['timezone'] == UTC_TIME_Z0NE
    assert job_sequence_builder._job_sequence['crontabMask'] == BASIC_CRON_TAB_MASK

    name, description = 'TEST NAME', 'TEST DESC'
    job_sequence = job_sequence_builder.build(name=name, description=description)
    assert isinstance(job_sequence, JobSequence)
    assert job_sequence.name == name
    assert job_sequence.description == description


def test_steps_getter(job_sequence):
    assert isinstance(job_sequence.steps, SeekableList)
    assert len(job_sequence.steps) == NUM_OF_STEPS

    for idx, step in enumerate(job_sequence.steps):
        assert isinstance(step, Step)
        assert step.step_number == idx + 1


@pytest.mark.parametrize(
    "step_to_move_index, target_step_number, id_to_correct_position_map, swap",
    [
        (3, 1, {'1': 2, '2': 3, '3': 4, '4': 1}, False),
        (0, 3, {'1': 3, '2': 1, '3': 2, '4': 4}, False),
        (-1, 1, {'1': 4, '2': 2, '3': 3, '4': 1}, True),
        (1, 3, {'1': 1, '2': 3, '3': 2, '4': 4}, True),
    ],
)
def test_move_step(job_sequence, step_to_move_index, target_step_number, id_to_correct_position_map, swap):
    step_to_move = job_sequence.steps[step_to_move_index]
    index_to_move = target_step_number
    id = job_sequence.id

    job_sequence.move_step(step_to_move, index_to_move, swap)

    # _data will now have [job_sequence.id, payload_data], assert that is accurate
    assert job_sequence._data[0] == id

    for step_payload in job_sequence._data[1]:
        assert step_payload['id'] in id_to_correct_position_map
        assert id_to_correct_position_map[step_payload['id']] == step_payload['stepNumber']


@pytest.mark.parametrize(
    "swap",
    [False, True],
)
def test_move_step_with_index_same_as_step_number_of_step(job_sequence, swap):
    step_to_move = job_sequence.steps[-1]

    with pytest.raises(ValueError):
        job_sequence.move_step(step_to_move, step_to_move.step_number, swap)


@pytest.mark.parametrize(
    "swap",
    [False, True],
)
def test_move_step_with_target_step_number_greater_than_number_of_steps(job_sequence, swap):
    with pytest.raises(ValueError):
        job_sequence.move_step(job_sequence.steps[0], 5, swap)


@pytest.mark.parametrize(
    "swap",
    [False, True],
)
def test_move_step_with_incorrect_step_type(job_sequence, swap):
    with pytest.raises(TypeError):
        job_sequence.move_step('ABC', 2, swap)


@pytest.mark.parametrize(
    "swap",
    [False, True],
)
def test_move_step_with_incorrect_target_step_number_type(job_sequence, swap):
    with pytest.raises(TypeError):
        job_sequence.move_step(job_sequence.steps[0], 'ABC', swap)


def test_move_step_with_incorrect_swap_type(job_sequence):
    with pytest.raises(TypeError):
        job_sequence.move_step(job_sequence.steps[0], 2, 'ABC')


@pytest.mark.parametrize(
    "job",
    ['1', ['1'], 1, [2]],
)
def test_mark_job_as_finished_with_incorrect_type(job_sequence, job):
    # trigger setter
    with pytest.raises(TypeError):
        job_sequence.mark_job_as_finished(job)


def test_mark_job_as_finished(job_sequence, dummy_job):
    dummy_job.job_sequence = True
    assert job_sequence.mark_job_as_finished(dummy_job).response.json() == dummy_job.job_id


def test_get_history_log_incorrect_value(job_sequence):
    with pytest.raises(ValueError):
        job_sequence.get_history_log('1', '2')


@pytest.mark.parametrize(
    "step",
    ['1', ['1'], 1, [2]],
)
def test_remove_step_incorrect_type(job_sequence, step):
    with pytest.raises(TypeError):
        job_sequence.remove_step(step)


def test_remove_step_with_step_not_in_sequence(job_sequence, dummy_step):
    with pytest.raises(ValueError):
        job_sequence.remove_step(dummy_step)


def test_remove_step(job_sequence):
    step = job_sequence.steps[0]
    id = job_sequence.id
    step_ids_after_removal = {'2': 1, '3': 2, '4': 3}

    job_sequence.remove_step(step)

    assert job_sequence._data[0] == id
    for step_data in job_sequence._data[1]:
        assert step_data['id'] != step.id
        assert step_data['id'] in step_ids_after_removal
        assert step_ids_after_removal[step_data['id']] == step_data['stepNumber']


@pytest.mark.parametrize(
    "job",
    ['1', ['1'], 1, [2]],
)
def test_add_step_incorrect_jobs_type(job_sequence, job):
    with pytest.raises(TypeError):
        job_sequence.add_step_with_jobs(job)


@pytest.mark.parametrize(
    "parallel_jobs, ignore_error",
    [("0", True), (True, "1"), ("0", False), (False, "1")],
)
def test_add_step_incorrect_parallel_jobs_ignore_error_type(job_sequence, dummy_job, parallel_jobs, ignore_error):
    with pytest.raises(TypeError):
        job_sequence.add_step_with_jobs([dummy_job], parallel_jobs, ignore_error)


def test_add_step_with_job_that_is_in_a_job_sequence(job_sequence, dummy_job):
    dummy_job.job_sequence = True

    with pytest.raises(ValueError):
        job_sequence.add_step_with_jobs([dummy_job])


@pytest.mark.parametrize(
    "ignore_error",
    [True, False],
)
def test_add_step_parallel_jobs_true(job_sequence, dummy_jobs, ignore_error):
    id = job_sequence.id

    job_sequence.add_step_with_jobs(dummy_jobs, True, ignore_error)

    assert job_sequence._data[0] == id
    job_ids = [job.job_id for job in dummy_jobs]
    assert job_sequence._data[1] == [{"stepNumber": NUM_OF_STEPS + 1, "ignoreError": ignore_error, "jobIds": job_ids}]


@pytest.mark.parametrize(
    "ignore_error",
    [True, False],
)
def test_add_step_parallel_jobs_false(job_sequence, dummy_jobs, ignore_error):
    job_sequence_id = job_sequence.id

    job_sequence.add_step_with_jobs(dummy_jobs, False, ignore_error)

    assert job_sequence._data[0] == job_sequence_id
    for idx, job in enumerate(dummy_jobs):
        assert job_sequence._data[1][idx] == {
            "stepNumber": NUM_OF_STEPS + idx + 1,
            "ignoreError": ignore_error,
            "jobIds": [job.job_id],
        }


def test_create_steps_payload(job_sequence):
    job_sequence_payload = job_sequence._create_steps_payload()
    job_sequence_ids_to_step_payload_map = {step_payload['id']: step_payload for step_payload in job_sequence_payload}

    for step in job_sequence.steps:
        assert step.id in job_sequence_ids_to_step_payload_map

        job_ids = [job['jobId'] for job in step.jobs]
        assert job_ids == job_sequence_ids_to_step_payload_map[step.id]['jobIds']

        assert step.step_number == job_sequence_ids_to_step_payload_map[step.id]['stepNumber']

        assert step.ignore_error == job_sequence_ids_to_step_payload_map[step.id]['ignoreError']
