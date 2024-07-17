# Copyright Streamsets 2023

import pytest

from streamsets.sdk.sch_models import DeploymentBuilder, Pipeline
from streamsets.sdk.sch_models import PipelineBuilder as SchSdcPipelineBuilder
from streamsets.sdk.sch_models import StPipelineBuilder as SchStPipelineBuilder
from streamsets.sdk.sdc_models import PipelineBuilder as SdcPipelineBuilder
from streamsets.sdk.st_models import PipelineBuilder as StPipelineBuilder

JOB_SEQUENCE_BUILDER_JSON = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'description': {'type': 'string'},
        'startTimeEnabled': {'type': 'boolean'},
        'startTime': {'type': 'integer', 'format': 'int64'},
        'repeatEnabled': {'type': 'boolean'},
        'crontabMask': {'type': 'string'},
        'endTimeCondition': {'type': 'string', 'enum': ['NEVER', 'ON']},
        'endTime': {'type': 'integer', 'format': 'int64'},
        'timezone': {'type': 'string'},
        'status': {'type': 'string', 'enum': ['INACTIVE', 'ACTIVE', 'DISABLED', 'ERROR']},
    },
}

JOB_SEQUENCE_EMPTY_JSON = {
    "id": None,
    "name": None,
    "description": None,
    "startTime": None,
    "endTime": None,
    "timezone": None,
    "crontabMask": None,
    "status": None,
    "startTimeEnabled": None,
    "repeatEnabled": None,
    "endTimeCondition": None,
    "nextRunTime": None,
}


@pytest.fixture(scope="function")
def pipeline_builder_json():
    data = {
        "pipelineId": 1,
        'commitId': 1,
        'name': 'Test Pipeline',
        'version': 1,
        "sdcId": "f0c68f66-9bf9-41cb-869a-2f703970d356",
        "pipelineConfig": {
            "schemaVersion": 6,
            "version": 39,
            "pipelineId": None,
            "title": "Pipeline Test",
            "description": "",
            "uuid": "13ee6ba6-f738-459c-b7e1-0002f2d13248",
            "configuration": [],
            "uiInfo": {},
            "info": {},
            "fragments": [],
            "stages": [],
            "errorStage": {
                "instanceName": "errorStageStageInstance",
                "library": "streamsets-datacollector-basic-lib",
                "stageName": "com_streamsets_pipeline_stage_destination_devnull_ToErrorNullDTarget",
                "stageVersion": "1",
                "configuration": [],
                "uiInfo": {"stageType": "TARGET", "label": "Error -Discard"},
                "inputLanes": [],
                "outputLanes": [],
                "eventLanes": [],
                "services": [],
            },
        },
    }

    return data


@pytest.fixture(scope="function")
def pipeline_builder_definitions():
    data = {
        'stages': [
            {  # snowflake destination
                "services": [],
                "description": "Fast data upload to Snowflake with Data Drift and CDC support",
                "name": "com_streamsets_pipeline_stage_destination_snowflake_SnowflakeDTarget",
                "type": "TARGET",
                "className": "com.streamsets.pipeline.stage.destination.snowflake.SnowflakeDTarget",
                "label": "Snowflake",
                "version": "18",
                "library": "streamsets-datacollector-sdc-snowflake-lib",
                "libraryLabel": "Snowflake Library",
                "configDefinitions": [
                    {
                        "fieldName": "snowflakeConnectionSelection",
                        "description": "",
                        "name": "config.snowflake.snowflakeConnectionSelection",
                        "type": "MODEL",
                        "defaultValue": "MANUAL",
                        "label": "Connection",
                        "connectionType": "STREAMSETS_SNOWFLAKE",
                        "model": {
                            "labels": ["None"],
                            "values": ["MANUAL"],
                            "configDefinitions": None,
                            "modelType": "VALUE_CHOOSER",
                            "compositeConfigDefinitions": None,
                            "valuesProviderClass": "com.streamsets.pipeline.api."
                            "ConnectionDef$Constants$ConnectionChooserValues",
                            "filteringConfig": "",
                        },
                    }
                ],
                "icon": "snowflake.png",
                "errorStage": False,
                "outputStreamLabels": None,
                "variableOutputStreams": False,
                "outputStreams": 0,
                "outputStreamLabelProviderClass": None,
                "inputStreamLabels": None,
                "inputStreams": -1,
                "inputStreamLabelProviderClass": "com.streamsets.pipeline.api.StageDef$DefaultInputStreams",
                "resetOffset": False,
                "outputStreamsDrivenByConfig": "",
                "producingEvents": False,
                "preconditions": True,
                "statsAggregatorStage": False,
            },
            {
                'services': [],
                'label': 'Trash',
                'name': 'com_streamsets_pipeline_stage_destination_devnull_NullDTarget',
                'type': 'TARGET',
                'className': 'com.streamsets.pipeline.stage.destination.devnull.NullDTarget',
                'version': '1',
                'eventDefs': [],
                'library': 'streamsets-datacollector-basic-lib',
                'privateClassLoader': False,
                'libraryLabel': 'Basic',
                'configDefinitions': [],
                'explorerSchema': None,
                'configGroupDefinition': {'classNameToGroupsMap': {}, 'groupNameToLabelMapList': []},
                'compositeConfigDefinitions': [],
                'icon': 'trash.png',
                'pipelineLifecycleStage': False,
                'statsAggregatorStage': False,
                'errorStage': False,
                'rawSourceDefinition': None,
                'outputStreamLabels': None,
                'variableOutputStreams': False,
                'outputStreams': 0,
                'outputStreamLabelProviderClass': None,
                'inputStreamLabels': None,
                'inputStreams': -1,
                'inputStreamLabelProviderClass': 'com.streamsets.pipeline.api.StageDef$DefaultInputStreams',
                'connectionVerifierStage': False,
                'offsetCommitTrigger': False,
                'executionModes': [
                    'STANDALONE',
                    'CLUSTER_BATCH',
                    'CLUSTER_YARN_STREAMING',
                    'CLUSTER_MESOS_STREAMING',
                    'EDGE',
                    'EMR_BATCH',
                ],
                'resetOffset': False,
            },
        ]
    }

    return data


class DummyEngines:
    def get(self, id):
        return DummyEngine()


class DummyEngine:
    def __init__(self):
        self._data = {'startUpTime': 0}
        self._sch_pipeline = {"sdcId": 0}


class MockControlHub:
    def __init__(self):
        self.organization = '12345'

    @property
    def engines(self):
        return DummyEngines()


@pytest.fixture(scope="function")
def sdc_pipeline_builder(pipeline_builder_json, pipeline_builder_definitions):
    return SdcPipelineBuilder(pipeline=pipeline_builder_json, definitions=pipeline_builder_definitions)


@pytest.fixture(scope="function")
def sch_sdc_pipeline_builder(pipeline_builder_json, sdc_pipeline_builder):
    return SchSdcPipelineBuilder(
        pipeline=pipeline_builder_json,
        data_collector_pipeline_builder=sdc_pipeline_builder,
        control_hub=MockControlHub(),
    )


@pytest.fixture(scope="function")
def st_pipeline_builder(pipeline_builder_json, pipeline_builder_definitions):
    return StPipelineBuilder(pipeline=pipeline_builder_json, definitions=pipeline_builder_definitions)


@pytest.fixture(scope="function")
def sch_st_pipeline_builder(pipeline_builder_json, st_pipeline_builder):
    return SchStPipelineBuilder(
        pipeline=pipeline_builder_json, transformer_pipeline_builder=st_pipeline_builder, control_hub=MockControlHub()
    )


@pytest.fixture(scope="function")
def deployment_builder_json():
    data = {
        'id': None,
        'organization': None,
        'name': None,
        'environment': None,
        'engineConfiguration': {
            'id': None,
            'organization': None,
            'stageLibs': None,
            'engineType': None,
            'engineVersionId': None,
            'engineVersion': None,
            'scalaBinaryVersion': None,
            'jvmConfig': {
                'id': None,
                'memoryConfigStrategy': None,
                'jvmMinMemory': None,
                'jvmMaxMemory': None,
                'jvmMinMemoryPercent': None,
                'jvmMaxMemoryPercent': None,
                'extraJvmOpts': None,
            },
            'externalResourcesUri': None,
            'advancedConfiguration': None,
            'labels': None,
            'lastStalenessTimestamp': None,
            'staleMessage': None,
            'creator': None,
            'createTime': None,
            'lastModifiedBy': None,
            'lastModifiedOn': None,
            'maxCpuLoad': None,
            'maxMemoryUsed': None,
            'maxPipelinesRunning': None,
        },
        'desiredInstances': None,
        'state': None,
        'status': None,
        'stateDisplayLabel': None,
        'statusDetail': None,
        'statusLastUpdated': None,
        'creator': None,
        'createTime': None,
        'lastModifiedBy': None,
        'lastModifiedOn': None,
        'deploymentTags': None,
        'rawDeploymentTags': None,
        'locked': None,
        'lockReference': None,
        'lockChangedAt': None,
        'lockChangedBy': None,
        'engineShutdownTimeout': None,
        'engineShutdownTimeoutTimestamp': None,
    }

    return data


@pytest.fixture(scope="function")
def self_deployment_builder(deployment_builder_json):
    additional_attributes = {'type': 'SELF', 'installType': None}

    data = {**deployment_builder_json, **additional_attributes}

    return DeploymentBuilder(data, MockControlHub())


@pytest.fixture(scope="function")
def gce_deployment_builder(deployment_builder_json):
    additional_attributes = {
        'type': 'GCE',
        'initScript': None,
        'machineType': None,
        'region': None,
        'allowedResourceLocations': None,
        'secretManagerReplicationPolicy': None,
        'zones': None,
        'blockProjectSshKeys': None,
        'publicSshKey': None,
        'trackingUrl': None,
        'instanceServiceAccountEmail': None,
        'tags': None,
        'resourceLabels': None,
        'subnetwork': None,
        'attachPublicIp': None,
    }

    data = {**deployment_builder_json, **additional_attributes}

    return DeploymentBuilder(data, MockControlHub())


@pytest.fixture(scope="function")
def ec2_deployment_builder(deployment_builder_json):
    additional_attributes = {
        'type': 'EC2',
        'initScript': None,
        'instanceType': None,
        'resourceTags': None,
        'sshKeySource': None,
        'sshKeyPairName': None,
        'instanceProfileArn': None,
        'trackingUrl': None,
    }

    data = {**deployment_builder_json, **additional_attributes}

    return DeploymentBuilder(data, MockControlHub())


@pytest.fixture(scope="function")
def azure_deployment_builder(deployment_builder_json):
    additional_attributes = {
        'type': 'AZURE_VM',
        'initScript': None,
        'vmSize': None,
        'sshKeySource': None,
        'sshKeyPairName': None,
        'publicSshKey': None,
        'resourceGroup': None,
        'resourceTags': None,
        'managedIdentity': None,
        'trackingUrl': None,
        'zones': None,
        'attachPublicIp': None,
    }

    data = {**deployment_builder_json, **additional_attributes}

    return DeploymentBuilder(data, MockControlHub())


@pytest.fixture(scope="function")
def kubernetes_deployment_builder(deployment_builder_json):
    additional_attributes = {
        'type': 'KUBERNETES',
        'kubernetesLabels': None,
        'memoryRequest': None,
        'cpuRequest': None,
        'memoryLimit': None,
        'cpuLimit': None,
        'yaml': None,
        'advancedMode': None,
        'hpa': None,
        'hpaMinReplicas': None,
        'hpaMaxReplicas': None,
        'hpaTargetCPUUtilizationPercentage': None,
    }

    data = {**deployment_builder_json, **additional_attributes}

    return DeploymentBuilder(data, MockControlHub())


@pytest.fixture(scope="function")
def pipeline_definitions():
    return {
        'stages': [
            {  # Snowflake destination
                'instanceName': 'Snowflake_01',
                'library': 'streamsets-datacollector-sdc-snowflake-lib',
                'stageName': 'com_streamsets_pipeline_stage_destination_snowflake_SnowflakeDTarget',
                'stageVersion': '18',
                'configuration': [],
                'services': [],
                'uiInfo': {'yPos': 50, 'stageType': 'TARGET', 'description': '', 'label': 'Snowflake 1', 'xPos': 60},
                'inputLanes': [],
                'outputLanes': [],
                'eventLanes': [],
            }
        ]
    }


@pytest.fixture(scope="function")
def pipeline_data_json(pipeline_definitions, request):
    return {
        'pipelineId': 1,
        'commitId': None,
        'name': 'Test Pipeline',
        'version': 1,
        'executorType': 'COLLECTOR' if 'sdc' in request.node.name else 'TRANSFORMER',
        'pipelineDefinitions': pipeline_definitions,
    }


@pytest.fixture(scope="function")
def sch_sdc_pipeline(
    pipeline_data_json,
    pipeline_definitions,
    sch_sdc_pipeline_builder,
    mocker,
):
    return Pipeline(
        pipeline=pipeline_data_json,
        pipeline_definition=pipeline_definitions,
        rules_definition=None,
        library_definitions={},
        control_hub=mocker.Mock(),
        builder=sch_sdc_pipeline_builder,
    )


@pytest.fixture(scope="function")
def sch_st_pipeline(
    pipeline_data_json,
    pipeline_definitions,
    sch_st_pipeline_builder,
    mocker,
):
    return Pipeline(
        pipeline=pipeline_data_json,
        pipeline_definition=pipeline_definitions,
        rules_definition=None,
        library_definitions={},
        control_hub=mocker.Mock(),
        builder=sch_st_pipeline_builder,
    )


@pytest.fixture(scope="function")
def azure_environment_json():
    data = {
        'id': None,
        'organization': None,
        'name': None,
        'type': 'AZURE',
        'userProvided': None,
        'credentialsType': None,
        'credentials': None,
        'allowSnapshotEngineVersions': None,
        'state': None,
        'status': None,
        'stateDisplayLabel': None,
        'statusDetail': None,
        'statusLastUpdated': None,
        'creator': None,
        'createTime': None,
        'lastModifiedBy': None,
        'lastModifiedOn': None,
        'environmentTags': None,
        'rawEnvironmentTags': None,
        'region': None,
        'vpcId': None,
        'subnetId': None,
        'securityGroupId': None,
        'resourceTags': None,
        'defaultResourceGroup': None,
        'defaultManagedIdentity': None,
    }

    return data
