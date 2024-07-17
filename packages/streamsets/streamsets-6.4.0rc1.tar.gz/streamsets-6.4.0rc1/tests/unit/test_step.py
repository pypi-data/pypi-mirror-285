# Copyright 2024 StreamSets Inc.

# fmt: off
import pytest

from streamsets.sdk.sch_models import Job, JobSequence
from streamsets.sdk.utils import SeekableList

# fmt: on
START_TIME_2099 = 4200268800
END_TIME_2099 = 4200268800
START_TIME_2100 = 4237401600
END_TIME_2100 = 4237996800
UTC_TIME_Z0NE = ' UTC'
BASIC_CRON_TAB_MASK = '0/1 * 1/1 * ? *'
NUM_OF_STEPS = 4
NUM_OF_JOBS = 3

JOB_SEQUENCE_EMPTY_JSON = {
    "id": 0,
    "name": None,
    "description": None,
    "startTime": None,
    "endTime": None,
    "timezone": None,
    "crontabMask": None,
    "status": None,
    "nextRunTime": None,
}
JOB_JSON = {
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
}


class MockControlHub:
    def __init__(self):
        self.api_client = MockApiClient()
        self.organization = 'DUMMY ORG'

    @property
    def jobs(self):
        return MockResponse('dummy')


class MockApiClient:
    def __init__(self):
        self.value = 'value'

    def mark_job_as_finished(self, value):
        return MockReturn(value)

    def get_job_sequence_log_history(self, value1, value2, value3):
        return MockReturn([value1, value2, value3])

    def add_step_jobs_to_job_sequence(self, value1, value2):
        return MockReturn({value1: value2})

    def update_job_sequence_steps(self, value):
        pass

    def update_steps_of_job_sequence(self, value1, value2):
        return MockReturn({'steps': value2})

    def get_jobs(self, job_ids):
        result = []
        for job_id in job_ids:
            json_copy = dict(JOB_JSON)
            json_copy['id'] = job_id
            result.append(json_copy)
        return MockReturn(result)


class MockReturn:
    def __init__(self, value):
        self.response = MockResponse(value)


class MockResponse:
    def __init__(self, value):
        self.value = value

    def json(self):
        return self.value

    def get(self, job_id):
        json_copy = dict(JOB_JSON)
        json_copy['id'] = job_id
        job = Job(json_copy, MockControlHub())
        return job


@pytest.fixture(scope="function")
def job_sequence_with_steps():
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
                'id': 'cb817030-c625-432c-ab6b-0918f27f5a16:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
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
                'id': '2c4e67ca-ef55-42fb-83ae-82a3a6d0fc2c:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
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
                'id': 'e9271c6c-9a09-4b90-ab61-da6be5660522:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
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
                'id': '0c3558d5-7674-49d3-9c5b-b5eedc22cef0:a2df1e64-dd65-11ed-bee6-3bf718d3c508',
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
def job_within_job_sequence():
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
    }
    return Job(json, MockControlHub())


@pytest.fixture(scope="function")
def dummy_jobs():
    jobs = []
    for i in range(NUM_OF_JOBS):
        json_copy = dict(JOB_JSON)
        json_copy['id'] = i
        jobs.append(Job(json_copy, MockControlHub()))

    return jobs


def test_step_jobs(job_sequence_with_steps):
    step = job_sequence_with_steps.steps[0]

    assert isinstance(step.step_jobs, SeekableList)
    assert len(step.step_jobs) == 1
    assert isinstance(step.step_jobs[0], Job)
    assert step._data['jobs'][0]['jobId'] == step.step_jobs[0].job_id


def test_remove_jobs(job_sequence_with_steps):
    step = job_sequence_with_steps.steps[0]
    step_jobs = step.step_jobs

    assert len(step_jobs) == 1
    id = step.id
    job_to_remove = step_jobs[0]

    step.remove_jobs(job_to_remove)

    assert step._data['id'] == id
    assert len(step._data['jobIds']) == 0


def test_remove_jobs_invalid_type(job_sequence_with_steps):
    step = job_sequence_with_steps.steps[0]

    with pytest.raises(TypeError):
        step.remove_jobs('invalid string')


def test_remove_jobs_with_job_that_isnt_in_step(job_sequence_with_steps):
    step1, step2 = job_sequence_with_steps.steps[0], job_sequence_with_steps.steps[1]

    with pytest.raises(ValueError):
        step1.remove_jobs(step2.step_jobs[0])


def test_add_job_incorrect_jobs_type(job_sequence_with_steps):
    step = job_sequence_with_steps.steps[0]

    with pytest.raises(TypeError):
        step.add_jobs('1')

    with pytest.raises(TypeError):
        step.add_jobs(['1'])


def test_add_job_incorrect_ignore_error_type(job_sequence_with_steps, dummy_jobs):
    step = job_sequence_with_steps.steps[0]
    job = dummy_jobs[0]
    job._data['jobSequence'] = None

    with pytest.raises(TypeError):
        step.add_jobs([job], ignore_error='1')


def test_add_job_with_job_that_is_in_another_job_sequence(job_sequence_with_steps, dummy_jobs):
    step = job_sequence_with_steps.steps[0]
    job = dummy_jobs[0]
    job._data['jobSequence'] = job_sequence_with_steps

    with pytest.raises(ValueError):
        step.add_jobs([job])
