"""Unit tests for DynamoClient using moto."""

from __future__ import annotations

import boto3
import pytest
from moto import mock_aws  # type: ignore[import-untyped]

from gridiron.db.dynamo import DynamoClient, TABLE_NAME


@pytest.fixture()
def dynamo_table():  # type: ignore[return]
    with mock_aws():
        client = boto3.client("dynamodb", region_name="us-east-1")
        client.create_table(
            TableName=TABLE_NAME,
            KeySchema=[
                {"AttributeName": "pk", "KeyType": "HASH"},
                {"AttributeName": "sk", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "pk", "AttributeType": "S"},
                {"AttributeName": "sk", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        yield DynamoClient(region="us-east-1")


def test_put_and_get(dynamo_table: DynamoClient) -> None:
    dynamo_table.put_item("FF#TEST#1", "META", {"value": "hello", "count": 42})
    item = dynamo_table.get_item("FF#TEST#1", "META")
    assert item is not None
    assert item["value"] == "hello"
    assert item["count"] == 42


def test_get_missing_returns_none(dynamo_table: DynamoClient) -> None:
    item = dynamo_table.get_item("FF#MISSING", "META")
    assert item is None


def test_update_item(dynamo_table: DynamoClient) -> None:
    dynamo_table.put_item("FF#TEST#2", "META", {"name": "old", "score": 10})
    dynamo_table.update_item("FF#TEST#2", "META", {"name": "new"})
    item = dynamo_table.get_item("FF#TEST#2", "META")
    assert item is not None
    assert item["name"] == "new"
    assert item["score"] == 10  # unchanged


def test_query_prefix(dynamo_table: DynamoClient) -> None:
    pk = "FF#ROSTER#abc#1"
    dynamo_table.put_item(pk, "SNAPSHOT#1", {"roster_id": 1})
    dynamo_table.put_item(pk, "SNAPSHOT#2", {"roster_id": 2})
    dynamo_table.put_item(pk, "OTHER#x", {"roster_id": 99})

    results = dynamo_table.query_prefix(pk, sk_prefix="SNAPSHOT#")
    assert len(results) == 2
    roster_ids = {r["roster_id"] for r in results}
    assert roster_ids == {1, 2}


def test_delete_item(dynamo_table: DynamoClient) -> None:
    dynamo_table.put_item("FF#TEST#3", "META", {"data": "x"})
    dynamo_table.delete_item("FF#TEST#3", "META")
    assert dynamo_table.get_item("FF#TEST#3", "META") is None
