# fmt: off
import pytest

from streamsets.sdk.sch_api import Command
from streamsets.sdk.sch_models import CollectionModelResults, Engine, Engines
from streamsets.sdk.utils import get_random_string

# fmt: on

NUM_OF_ENGINES = 5


class MockControlHub:
    def __init__(self, value):
        self.api_client = MockApiClient(value)
        self.organization = 'DUMMY ORG'


class MockApiClient:
    def __init__(self, value):
        self.value = value

    def get_engine(self, **kwargs):
        return Command(self, MockResponse(self.value))

    def get_all_registered_engines(self, **kwargs):
        return Command(self, MockResponse(self.value))


class MockResponse:
    def __init__(self, value):
        self.value = value

    def json(self):
        return self.value


@pytest.fixture(scope="function")
def get_engine_response_collector_json():
    json = {
        'id': get_random_string(),
        'organization': '1a1b7cf4-862e-11ed-94d5-41a005fd7967',
        'httpUrl': 'http://f8728e856446:18630',
        'version': '5.6.0',
        'labels': [],
        'reportedLabels': ['deployment'],
        'pipelinesCommitted': [],
        'lastReportedTime': 1697835654564,
        'startUpTime': 1696872736374,
        'offsetProtocolVersion': 2,
        'edge': False,
        'cpuLoad': 0.7079236552920763,
        'totalMemory': 16606822400.0,
        'usedMemory': 581667472.0,
        'memoryUsedPercentage': 0.03502581396908297,
        'pipelinesCount': 0,
        'responding': True,
        'idSeparator': '__',
        'executorType': 'COLLECTOR',
        'maxCpuLoad': 80.0,
        'maxMemoryUsed': 100.0,
        'maxPipelinesRunning': 1000000,
        'cspDeploymentId': '14dc3111-b89d-488a-b9c1-4c6d7a767c39:1a1b7cf4-862e-11ed-94d5-41a005fd7967',
        'deploymentId': None,
        'buildTime': 1687277400000,
        'overrideEngineMaxes': False,
        'lastShutdownTimestamp': None,
    }

    return json


@pytest.fixture(scope="function")
def get_engine_response_transformer_json():
    json = {
        'id': get_random_string(),
        'organization': '1a1b7cf4-862e-11ed-94d5-41a005fd7967',
        'httpUrl': 'http://f8728e856446:18630',
        'version': '5.6.0',
        'labels': [],
        'reportedLabels': ['deployment'],
        'pipelinesCommitted': [],
        'lastReportedTime': 1697835654564,
        'startUpTime': 1696872736374,
        'offsetProtocolVersion': 2,
        'edge': False,
        'cpuLoad': 0.7079236552920763,
        'totalMemory': 16606822400.0,
        'usedMemory': 581667472.0,
        'memoryUsedPercentage': 0.03502581396908297,
        'pipelinesCount': 0,
        'responding': True,
        'idSeparator': '__',
        'executorType': 'TRANSFORMER',
        'maxCpuLoad': 80.0,
        'maxMemoryUsed': 100.0,
        'maxPipelinesRunning': 1000000,
        'cspDeploymentId': '14dc3111-b89d-488a-b9c1-4c6d7a767c39:1a1b7cf4-862e-11ed-94d5-41a005fd7967',
        'deploymentId': None,
        'buildTime': 1687277400000,
        'overrideEngineMaxes': False,
        'lastShutdownTimestamp': None,
    }

    return json


@pytest.fixture(scope="function")
def get_all_registered_engines_response_collector_json(get_engine_response_collector_json):
    json = {'totalCount': 1, 'offset': 50, 'len': 50, 'data': []}
    get_engine_response_collector_json['id'] += '{}'
    for i in range(NUM_OF_ENGINES):
        get_engine_response_collector_json['id'].format(i)
        json['data'].append(get_engine_response_collector_json)

    return json


@pytest.fixture(scope="function")
def get_all_registered_engines_response_transformer_json(get_engine_response_transformer_json):
    json = {'totalCount': 1, 'offset': 50, 'len': 50, 'data': []}
    get_engine_response_transformer_json['id'] += '{}'
    for i in range(NUM_OF_ENGINES):
        get_engine_response_transformer_json['id'].format(i)
        json['data'].append(get_engine_response_transformer_json)

    return json


@pytest.mark.parametrize(
    "engine_json",
    ["get_all_registered_engines_response_collector_json", "get_all_registered_engines_response_transformer_json"],
)
def test_engines_sanity(engine_json, request):
    engine_json = request.getfixturevalue(engine_json)

    mock_control_hub = MockControlHub(engine_json)
    e = Engines(mock_control_hub)

    response = e._get_all_results_from_api()

    assert isinstance(response, CollectionModelResults)
    assert response.results == engine_json
    assert len(response.results['data']) == NUM_OF_ENGINES
    assert response.class_type == Engine
    assert response.class_kwargs['control_hub'] == mock_control_hub


@pytest.mark.parametrize(
    "engine_json",
    ["get_engine_response_collector_json", "get_engine_response_transformer_json"],
)
def test_engines_get_with_id(engine_json, request):
    engine_json = request.getfixturevalue(engine_json)
    mock_control_hub = MockControlHub(engine_json)
    e = Engines(mock_control_hub)

    response = e._get_all_results_from_api(id='123')

    assert isinstance(response, CollectionModelResults)
    assert response.results == [engine_json]
    assert response.class_type == Engine
    assert response.class_kwargs['control_hub'] == mock_control_hub


@pytest.mark.parametrize(
    "engine_json,engine_type",
    [("get_engine_response_collector_json", "COLLECTOR"), ("get_engine_response_transformer_json", "TRANSFORMER")],
)
def test_engines_get_with_id_and_type(engine_json, engine_type, request):
    engine_json = request.getfixturevalue(engine_json)
    mock_control_hub = MockControlHub(engine_json)
    e = Engines(mock_control_hub)

    response = e._get_all_results_from_api(engine_type=engine_type, id='123')

    assert isinstance(response, CollectionModelResults)
    assert response.results == [engine_json]
    assert response.class_type == Engine
    assert response.class_kwargs['control_hub'] == mock_control_hub


@pytest.mark.parametrize(
    "engine_json,engine_type",
    [("get_engine_response_collector_json", "TRANSFORMER"), ("get_engine_response_transformer_json", "COLLECTOR")],
)
def test_engines_get_with_incorrect_type(engine_json, engine_type, request):
    engine_json = request.getfixturevalue(engine_json)
    e = Engines(MockControlHub(engine_json))

    with pytest.raises(TypeError):
        e._get_all_results_from_api(engine_type=engine_type, id='123')


def test_engines_get_with_invalid_type(get_engine_response_collector_json):
    e = Engines(MockControlHub(get_engine_response_collector_json))

    with pytest.raises(ValueError):
        e._get_all_results_from_api(engine_type='DUMMY TYPE', id='123')
