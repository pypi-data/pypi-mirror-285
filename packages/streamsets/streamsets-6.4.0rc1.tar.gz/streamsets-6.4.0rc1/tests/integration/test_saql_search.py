# Copyright 2023 StreamSets Inc.

# fmt: off
import json

import pytest

from streamsets.sdk.utils import get_random_string

# fmt: on

NUM_PIPELINES = 2
NUM_JOBS = 2

# TODO: Add tests for more saql_search_types than just PIPELINE


@pytest.fixture(scope="module")
def sample_saql_pipeline_searches(sch):
    """A set of trivial pipelines:

    dev_data_generator >> trash
    """
    pipeline_searches = []
    for i in range(NUM_PIPELINES):
        pipeline_searches.append(
            sch.api_client.create_saql_pipeline_search(
                {
                    "name": "SAMPLE_PIPELINE_SEARCH_{}_{}".format(i, get_random_string()),
                    "type": "PIPELINE",
                    "mode": "BASIC",
                    "query": "name==*tmp_query*",
                }
            ).response.json()
        )
    try:
        yield pipeline_searches
    finally:
        for search in pipeline_searches:
            sch.api_client.remove_saql_pipeline_search(search["id"])


@pytest.fixture(scope="module")
def sample_saql_job_searches(sch):
    """A set of trivial pipelines:

    dev_data_generator >> trash
    """
    job_searches = []
    for i in range(NUM_PIPELINES):
        job_searches.append(
            sch.api_client.create_saql_job_search(
                {
                    "name": "SAMPLE_JOB_SEARCH_{}_{}".format(i, get_random_string()),
                    "type": "JOB_INSTANCE",
                    "mode": "BASIC",
                    "query": "name==*tmp_query*",
                }
            ).response.json()
        )
    try:
        yield job_searches
    finally:
        for search in job_searches:
            sch.api_client.remove_saql_job_search(search["id"])


@pytest.fixture(scope="module")
def sample_saql_search_object(sch):
    """
    Trivial SAQL Search builder:
    """
    # build the SAQLSearch Object
    builder = sch.get_saql_search_builder('PIPELINE')
    builder.add_filter(
        property_name='name',
        property_operator='contains',
        property_value='TEST_NAME',
        property_condition_combiner='AND',
    )
    obj = builder.build('TEST NAME {}'.format(get_random_string()))

    yield obj


def test_saql_pipeline_search_api(sch, sample_saql_pipeline_searches):
    pipeline_searches = sch.api_client.get_saql_pipeline_searches(
        "SAMPLE_PIPELINE_SEARCH_1", "PIPELINE"
    ).response.json()
    assert pipeline_searches["totalCount"] == 1


def test_saql_job_search_api(sch, sample_saql_job_searches):
    job_searches = sch.api_client.get_saql_job_searches("SAMPLE_JOB_SEARCH_1", "JOB_INSTANCE").response.json()
    assert job_searches["totalCount"] == 1


def test_saql_favorite_job_api(sch, sample_saql_job_searches):
    job_searches = sch.api_client.get_saql_job_searches("SAMPLE_JOB_SEARCH_1", "JOB_INSTANCE").response.json()
    assert job_searches["totalCount"] == 1

    search = job_searches['data'][0]
    sch.api_client.create_saql_fav_job(search['id']).response.json()

    favorite_job = sch.api_client.get_saql_job_searches("SAMPLE_JOB_SEARCH_1", "JOB_INSTANCE").response.json()
    assert favorite_job["totalCount"] == 1
    assert favorite_job['data'][0]['favorite']['favorite']


def test_saql_favorite_pipeline_api(sch, sample_saql_pipeline_searches):
    job_searches = sch.api_client.get_saql_pipeline_searches("SAMPLE_PIPELINE_SEARCH_1", "PIPELINE").response.json()
    assert job_searches["totalCount"] == 1
    search = job_searches['data'][0]

    sch.api_client.create_saql_fav_pipeline(search['id']).response.json()

    favorite_pipeline = sch.api_client.get_saql_pipeline_searches(
        "SAMPLE_PIPELINE_SEARCH_1", "PIPELINE"
    ).response.json()
    assert favorite_pipeline["totalCount"] == 1
    assert favorite_pipeline['data'][0]['favorite']['favorite']


def test_saql_saved_searches_pipeline(sch):
    try:
        response = sch.api_client.create_saql_pipeline_search(
            {"name": "TEST_PIPELINE_SEARCH", "type": "PIPELINE", "mode": "BASIC", "query": "name==*tmp_query*"}
        ).response.json()
        saql_searches = sch.saql_saved_searches_pipeline.get_all(name='TEST_PIPELINE_SEARCH')
        assert len(saql_searches) == 1
    finally:
        sch.api_client.remove_saql_pipeline_search(response["id"])


def test_saql_saved_searches_fragment(sch):
    try:
        response = sch.api_client.create_saql_pipeline_search(
            {"name": "SAMPLE_FRAGMENT_SEARCH", "type": "FRAGMENT", "mode": "BASIC", "query": "name==*tmp_query*"}
        ).response.json()
        saql_searches = sch.saql_saved_searches_fragment.get_all(name='SAMPLE_FRAGMENT_SEARCH')
        assert len(saql_searches) == 1
    finally:
        sch.api_client.remove_saql_pipeline_search(response["id"])


def test_saql_saved_searches_job_instance(sch):
    try:
        response = sch.api_client.create_saql_job_search(
            {
                "name": "SAMPLE_JOB_INSTANCE_SEARCH",
                "type": "JOB_INSTANCE",
                "mode": "BASIC",
                "query": "name==*tmp_query*",
            }
        ).response.json()
        saql_searches = sch.saql_saved_searches_job_instance.get_all(name='SAMPLE_JOB_INSTANCE_SEARCH')
        assert len(saql_searches) == 1
    finally:
        sch.api_client.remove_saql_job_search(response["id"])


def test_saql_saved_searches_job_template(sch):
    try:
        response = sch.api_client.create_saql_job_search(
            {
                "name": "SAMPLE_JOB_TEMPLATE_SEARCH",
                "type": "JOB_TEMPLATE",
                "mode": "BASIC",
                "query": "name==*tmp_query*",
            }
        ).response.json()
        saql_searches = sch.saql_saved_searches_job_template.get_all(name='SAMPLE_JOB_TEMPLATE_SEARCH')
        assert len(saql_searches) == 1
    finally:
        sch.api_client.remove_saql_job_search(response["id"])


def test_saql_saved_searches_job_draft_run(sch):
    try:
        response = sch.api_client.create_saql_job_search(
            {
                "name": "SAMPLE_JOB_DRAFT_RUN_SEARCH",
                "type": "JOB_DRAFT_RUN",
                "mode": "BASIC",
                "query": "name==*tmp_query*",
            }
        ).response.json()
        saql_searches = sch.saql_saved_searches_draft_run.get_all(name='SAMPLE_JOB_DRAFT_RUN_SEARCH')
        assert len(saql_searches) == 1
    finally:
        sch.api_client.remove_saql_job_search(response["id"])


def test_saql_builder(sch):
    # create/test builder with filters
    builder = sch.get_saql_search_builder('PIPELINE')
    assert len(builder.query) == 0
    builder.add_filter(
        property_name='name',
        property_operator='contains',
        property_value='TEST_NAME',
        property_condition_combiner='AND',
    )
    assert len(builder.query) == 1

    # test builder object
    obj = builder.build('TEST NAME')
    assert obj.name == 'TEST NAME'
    assert obj.type == 'PIPELINE'
    assert isinstance(obj.query, str)


def test_saql_builder_with_incorrect_saql_search_type(sch):
    try:
        sch.get_saql_search_builder(saql_search_type='FOO', mode='BASIC')
    except Exception as exception:
        assert isinstance(exception, ValueError)


def test_saql_builder_with_incorrect_saql_search_mode(sch):
    try:
        sch.get_saql_search_builder(saql_search_type='PIPELINE', mode='foo')
    except Exception as exception:
        assert isinstance(exception, ValueError)


def test_saql_builder_with_incorrect_property_name(sch):
    builder = sch.get_saql_search_builder('PIPELINE')
    try:
        builder.add_filter(
            property_name='foo',
            property_operator='contains',
            property_value='TEST_NAME',
            property_condition_combiner='AND',
        )
    except Exception as exception:
        assert isinstance(exception, ValueError)


def test_saql_builder_with_incorrect_property_operator(sch):
    builder = sch.get_saql_search_builder('PIPELINE')
    try:
        builder.add_filter(
            property_name='name', property_operator='foo', property_value='TEST_NAME', property_condition_combiner='AND'
        )
    except Exception as exception:
        assert isinstance(exception, ValueError)


def test_saql_builder_with_incorrect_search_name_type(sch):
    builder = sch.get_saql_search_builder(saql_search_type='PIPELINE', mode='BASIC')
    builder.add_filter(
        property_name='name',
        property_operator='contains',
        property_value='TEST_NAME',
        property_condition_combiner='AND',
    )

    with pytest.raises(TypeError):
        builder.build(12)


def test_save_search(sch, sample_saql_search_object):
    response_save = {}
    try:
        # test basic save response details
        response = sch.save_saql_search(sample_saql_search_object)
        assert response.response.status_code == 200
        response_save = response.response.json()
        assert isinstance(response_save, dict)
        assert response_save['name'] == sample_saql_search_object.name
        assert response_save['type'] == 'PIPELINE'

        # test returned query
        response_json = json.loads(response_save['query'])
        assert len(response_json) == 1
        query = response_json[0]
        assert query['filter']['name'] == 'name'
        assert query['operator'] == 'contains'
        assert query['value'] == 'TEST_NAME'
        assert query['conditionCombiner'] == 'AND'
    finally:
        # remove the saql search
        if response_save.get("id", None):
            sch.api_client.remove_saql_pipeline_search(response_save["id"])


def test_mark_search_as_favorite(sch, sample_saql_search_object):
    response_save = {}
    try:
        response_save = sch.save_saql_search(sample_saql_search_object).response.json()

        # test marking a search as favorite
        saql_search = sch.saql_saved_searches_pipeline.get(name=sample_saql_search_object.name)
        response = sch.mark_saql_search_as_favorite(saql_search)
        assert response.response.status_code == 200
        response_favorite = response.response.json()
        assert response_favorite == saql_search.favorite
    finally:
        # remove the saql search
        if response_save.get("id", None):
            sch.api_client.remove_saql_pipeline_search(response_save["id"])


def test_remove_search(sch, sample_saql_search_object):
    response_save = {}
    try:
        response_save = sch.save_saql_search(sample_saql_search_object).response.json()

        # test remove a search
        saql_search = sch.saql_saved_searches_pipeline.get(name=sample_saql_search_object.name)
        response = sch.remove_saql_search(saql_search)
        assert response.response.status_code == 200
        response_remove = response.response.json()
        assert response_remove['id'] == response_save['id']
    except Exception as exception:
        # remove the saql search
        if response_save.get("id", None):
            sch.api_client.remove_saql_pipeline_search(response_save["id"])

        raise exception


def test_query_with_multiple_filters(sch):
    # build the SAQLSearch Object
    builder = sch.get_saql_search_builder('PIPELINE')

    builder.add_filter(
        property_name='name', property_operator='contains', property_value='SAMPLE', property_condition_combiner='AND'
    )
    builder.add_filter(
        property_name='name', property_operator='begins with', property_value='TEST', property_condition_combiner='AND'
    )
    builder.add_filter(
        property_name='modified_on',
        property_operator='is before',
        property_value='2023-04-03',
        property_condition_combiner='OR',
    )
    builder.add_filter(property_name='draft', property_operator='is true', property_condition_combiner='AND')
    builder.add_filter(property_name='commit_message', property_operator='is empty')

    saql_search_object = builder.build(name='TEST NAME')

    assert (
        saql_search_object.query == 'name == "*SAMPLE*" and name == "TEST*" and modified_on =lt= "2023-04-03"'
        ' or draft == true and commit_message =null= true'
    )

    response_save = {}
    try:
        # test basic save response details
        response = sch.save_saql_search(saql_search_object)
        assert response.response.status_code == 200
        response_save = response.response.json()
    finally:
        # remove the saql search
        if response_save.get("id", None):
            sch.api_client.remove_saql_pipeline_search(response_save["id"])
