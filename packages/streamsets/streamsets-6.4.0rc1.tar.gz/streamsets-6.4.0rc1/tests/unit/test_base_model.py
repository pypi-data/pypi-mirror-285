# Copyright 2023 StreamSets Inc.

# fmt: off
import json
from copy import copy, deepcopy

import pytest

from streamsets.sdk.sch_models import BaseModel

# fmt: on


@pytest.fixture(scope="function")
def base_model_data():
    data = {
        "commitId": "24786589-b45f-4656-afce-1a9fc7460801:458a1537-9831-11ed-91d7-576b84801428",
        "topologyId": "447a9fbc-2124-4597-8215-55eb7989bda2:458a1537-9831-11ed-91d7-576b84801428",
        "organization": "458a1537-9831-11ed-91d7-576b84801428",
        "lastModifiedBy": "35ac586e-9831-11ed-91d7-559988873bf7@458a1537-9831-11ed-91d7-576b84801428",
        "lastModifiedOn": 1688595384128,
        "name": "sample_topology",
        "description": None,
        "parentVersion": "0",
        "version": "1",
        "committer": "35ac586e-9831-11ed-91d7-559988873bf7",
        "commitMessage": None,
        "commitTime": 1688595384128,
        "draft": False,
        "fooProperty": "foo",
        "defaultTopology": False,
        "topologyDefinition": '{"schemaVersion": "1", '
        '"topologyNodes": [{"nodeType": "SYSTEM", {"label": "Dev Raw Data Source 1", '
        '"colorIcon": "Origin_Dev_Raw_Data_Source.png", "xPos": 100, "yPos": 125.0}}'
        '"instanceName": "DevRawDataSource_1:SYSTEM:1688620416884"',
        "provenanceMetaData": {"foo": "baz"},
    }
    return data


@pytest.fixture(scope="module")
def attributes_to_ignore():
    return ['provenanceMetaData']


@pytest.fixture(scope="module")
def attributes_to_remap():
    # Mapping is {"new_attribute": "original_attribute"}
    return {'committed_by': 'committer', 'topology_name': 'name'}


@pytest.fixture(scope="module")
def repr_metadata():
    return ['topology_id', 'topology_name']


class Helper(BaseModel):
    def __init__(self, data, base_model_data, attributes_to_ignore, attributes_to_remap, repr_metadata):
        super().__init__(
            data=base_model_data,
            attributes_to_ignore=attributes_to_ignore,
            attributes_to_remap=attributes_to_remap,
            repr_metadata=repr_metadata,
        )
        self.return_value = json.dumps(data)
        self.data = data

    @property
    def foo_property(self):
        return self.data

    @foo_property.setter
    def foo_property(self, data):
        self.data = json.dumps(data)


def test_data_ingest_sanity(base_model_data, attributes_to_ignore, attributes_to_remap, repr_metadata):
    base_model = BaseModel(
        data=base_model_data,
        attributes_to_ignore=attributes_to_ignore,
        attributes_to_remap=attributes_to_remap,
        repr_metadata=repr_metadata,
    )

    assert base_model._data_internal is base_model_data
    assert base_model._attributes_to_ignore is attributes_to_ignore
    assert base_model._attributes_to_remap is attributes_to_remap
    assert base_model._repr_metadata is repr_metadata


def test_getattr_name_in_attributes_to_remap(base_model_data, attributes_to_ignore, attributes_to_remap, repr_metadata):
    base_model = BaseModel(
        data=base_model_data,
        attributes_to_ignore=attributes_to_ignore,
        attributes_to_remap=attributes_to_remap,
        repr_metadata=repr_metadata,
    )

    assert base_model.committed_by == base_model_data['committer']
    assert base_model.topology_name == base_model_data['name']


def test_getattr_python_to_json_attribute(base_model_data, attributes_to_ignore, attributes_to_remap, repr_metadata):
    base_model = BaseModel(
        data=base_model_data,
        attributes_to_ignore=attributes_to_ignore,
        attributes_to_remap=attributes_to_remap,
        repr_metadata=repr_metadata,
    )
    assert base_model.topologyDefinition == base_model_data['topologyDefinition']
    assert base_model.topology_definition == base_model_data['topologyDefinition']


def test_setattr_python_to_json_attribute(base_model_data, attributes_to_ignore, attributes_to_remap, repr_metadata):
    data = {"foo": "baz"}
    helper_obj = Helper(data, base_model_data, attributes_to_ignore, attributes_to_remap, repr_metadata)
    assert helper_obj.foo_property == data  # Sanity check

    # Reassign value so property setter runs json.dumps()
    helper_obj.foo_property = data

    # Expect property setter to get called which returns a json.dumps() of data
    assert helper_obj.foo_property == helper_obj.return_value


def test_attributes_to_ignore_in_base_model(base_model_data, attributes_to_ignore, attributes_to_remap, repr_metadata):
    data = {"foo": "baz"}
    helper_obj = Helper(data, base_model_data, attributes_to_ignore, attributes_to_remap, repr_metadata)
    assert helper_obj._data["provenanceMetaData"] == base_model_data["provenanceMetaData"]  # Sanity check

    # Check if only the specified attribute is ignored
    assert hasattr(helper_obj, "topologyId")
    assert not hasattr(helper_obj, "provenanceMetaData")


def test_override_equal(base_model_data, attributes_to_ignore, attributes_to_remap, repr_metadata):
    base_model = BaseModel(
        data=base_model_data,
        attributes_to_ignore=attributes_to_ignore,
        attributes_to_remap=attributes_to_remap,
        repr_metadata=repr_metadata,
    )
    copy_base_model = BaseModel(
        data=base_model_data,
        attributes_to_ignore=attributes_to_ignore,
        attributes_to_remap=attributes_to_remap,
        repr_metadata=repr_metadata,
    )

    assert base_model == copy_base_model


def test_copying_base_model(base_model_data, attributes_to_ignore, attributes_to_remap, repr_metadata):
    # create a base model that has another base model object as an attribute
    base_model = BaseModel(
        data=base_model_data,
        attributes_to_ignore=attributes_to_ignore,
        attributes_to_remap=attributes_to_remap,
        repr_metadata=repr_metadata,
    )
    sub_base_model = BaseModel(
        data=base_model_data,
        attributes_to_ignore=attributes_to_ignore,
        attributes_to_remap=attributes_to_remap,
        repr_metadata=repr_metadata,
    )
    base_model.sub_base_model = sub_base_model

    # copy to ensure base models are equal but not the same, sub_base_model should be equal and same
    copy_base_model = copy(base_model)
    assert base_model == copy_base_model
    assert id(base_model) != id(copy_base_model)
    assert base_model.sub_base_model == copy_base_model.sub_base_model
    assert id(base_model.sub_base_model) == id(copy_base_model.sub_base_model)


def test_deep_copying_base_model(base_model_data, attributes_to_ignore, attributes_to_remap, repr_metadata):
    # create a base model that has another base model object as an attribute
    base_model = BaseModel(
        data=base_model_data,
        attributes_to_ignore=attributes_to_ignore,
        attributes_to_remap=attributes_to_remap,
        repr_metadata=repr_metadata,
    )
    sub_base_model = BaseModel(
        data=base_model_data,
        attributes_to_ignore=attributes_to_ignore,
        attributes_to_remap=attributes_to_remap,
        repr_metadata=repr_metadata,
    )
    base_model.sub_base_model = sub_base_model

    # deepcopy to ensure both base_model and sub_base_model are equal to deepcopy, but their ids shouldn't be
    deepcopy_base_model = deepcopy(base_model)
    assert base_model == deepcopy_base_model
    assert id(base_model) != id(deepcopy_base_model)
    assert base_model.sub_base_model == deepcopy_base_model.sub_base_model
    assert id(base_model.sub_base_model) != id(deepcopy_base_model.sub_base_model)
