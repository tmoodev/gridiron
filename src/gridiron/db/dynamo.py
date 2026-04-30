"""DynamoDB access layer — all FF# prefixed keys on datatrav-ops table."""

from __future__ import annotations

from typing import Any

import boto3
import structlog
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from mypy_boto3_dynamodb import DynamoDBClient

log = structlog.get_logger(__name__)

TABLE_NAME = "datatrav-ops"


class DynamoClient:
    def __init__(self, region: str = "us-east-1") -> None:
        self._client: DynamoDBClient = boto3.client("dynamodb", region_name=region)
        self._resource = boto3.resource("dynamodb", region_name=region)
        self._table = self._resource.Table(TABLE_NAME)

    def put_item(self, pk: str, sk: str, item: dict[str, Any]) -> None:
        """Upsert an item. pk and sk are merged into item automatically."""
        self._table.put_item(Item={"pk": pk, "sk": sk, **item})
        log.debug("dynamo.put_item", pk=pk, sk=sk)

    def get_item(self, pk: str, sk: str) -> dict[str, Any] | None:
        """Return item dict or None if not found."""
        resp = self._table.get_item(Key={"pk": pk, "sk": sk})
        item = resp.get("Item")
        log.debug("dynamo.get_item", pk=pk, sk=sk, found=item is not None)
        return item  # type: ignore[return-value]

    def query_prefix(
        self,
        pk: str,
        sk_prefix: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Query all items for a pk, optionally filtering sk by prefix."""
        kwargs: dict[str, Any] = {
            "KeyConditionExpression": Key("pk").eq(pk),
            "Limit": limit,
        }
        if sk_prefix:
            kwargs["KeyConditionExpression"] &= Key("sk").begins_with(sk_prefix)
        resp = self._table.query(**kwargs)
        items: list[dict[str, Any]] = resp.get("Items", [])
        log.debug("dynamo.query_prefix", pk=pk, sk_prefix=sk_prefix, count=len(items))
        return items

    def update_item(
        self,
        pk: str,
        sk: str,
        updates: dict[str, Any],
    ) -> None:
        """Partial update — only the specified fields are written."""
        if not updates:
            return
        expr_parts = []
        attr_names: dict[str, str] = {}
        attr_values: dict[str, Any] = {}
        for i, (k, v) in enumerate(updates.items()):
            placeholder = f"#f{i}"
            value_key = f":v{i}"
            expr_parts.append(f"{placeholder} = {value_key}")
            attr_names[placeholder] = k
            attr_values[value_key] = v
        expression = "SET " + ", ".join(expr_parts)
        self._table.update_item(
            Key={"pk": pk, "sk": sk},
            UpdateExpression=expression,
            ExpressionAttributeNames=attr_names,
            ExpressionAttributeValues=attr_values,
        )
        log.debug("dynamo.update_item", pk=pk, sk=sk, fields=list(updates.keys()))

    def delete_item(self, pk: str, sk: str) -> None:
        """Delete an item by primary key."""
        try:
            self._table.delete_item(Key={"pk": pk, "sk": sk})
            log.debug("dynamo.delete_item", pk=pk, sk=sk)
        except ClientError as exc:
            log.error("dynamo.delete_item.error", pk=pk, sk=sk, error=str(exc))
            raise
