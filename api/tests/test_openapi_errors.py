from typing import Any

import pytest
from fastapi.testclient import TestClient

ERROR_SCHEMA = {"$ref": "#/components/schemas/ErrorResponse"}


def documented_error(spec: dict[str, Any], path: str, status: str) -> Any:
    response = spec["paths"][path]["get"]["responses"][status]
    return response["content"]["application/json"]["schema"]


@pytest.fixture
def spec(client: TestClient) -> dict[str, Any]:
    body: dict[str, Any] = client.get("/openapi.json").json()
    return body


@pytest.mark.parametrize("path", ["/pois", "/pois/{poi_id}"])
def test_422_is_documented_with_its_real_shape(spec: dict[str, Any], path: str) -> None:
    assert documented_error(spec, path, "422") == ERROR_SCHEMA


def test_404_of_the_detail_is_documented(spec: dict[str, Any]) -> None:
    assert documented_error(spec, "/pois/{poi_id}", "404") == ERROR_SCHEMA


def test_fastapi_default_validation_error_is_no_longer_advertised(spec: dict[str, Any]) -> None:
    assert "HTTPValidationError" not in spec["components"]["schemas"]
    assert spec["components"]["schemas"]["ErrorResponse"]["properties"]["detail"]["type"] == (
        "string"
    )
