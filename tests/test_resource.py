from pydid.resource import Resource


def test_resource():
    Resource()


def test_resource_json_transforms():
    class Test(Resource):
        one: str

    assert Test(one="test").to_json() == '{"one": "test"}'
    assert Test.from_json('{"one": "test"}') == Test(one="test")
