import json


async def test_node_extension_manager(jp_fetch):
    # When
    response = await jp_fetch("vp4jl", "node_extension_manager")

    # Then
    assert response.code == 200
    payload = json.loads(response.body)
    assert payload
