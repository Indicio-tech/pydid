"""Test Resource."""

import pytest
from pydid.resource import Resource, IndexedResource


def test_resource():
    Resource()


def test_resource_json_transforms():
    class Test(Resource):
        one: str

    assert Test(one="test").to_json() == '{"one": "test"}'
    assert Test.from_json('{"one": "test"}') == Test(one="test")


def test_dereference_as():
    class One(Resource):
        pass

    class Two(Resource):
        pass

    class Test(IndexedResource):
        def _index_resources(self):
            pass

        def dereference(self, reference: str) -> Resource:
            return One()

    assert isinstance(Test().dereference_as(One, "test"), One)
    with pytest.raises(ValueError):
        Test().dereference_as(Two, "test")
