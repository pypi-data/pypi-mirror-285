import json
import re
from datetime import datetime, timedelta
from decimal import Decimal
from functools import cached_property
from typing import Dict

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from reach_commons.utils import DecimalEncoder, build_update_params_for_attributes


# noinspection PyMethodMayBeStatic
class BaseDynamoDBClient:
    def __init__(
        self,
        region_name="us-east-1",
        profile_name=None,
    ):
        self.region_name = region_name
        self.profile_name = profile_name


class DynamoDBClient(BaseDynamoDBClient):
    @cached_property
    def client(self):
        session = boto3.Session(
            region_name=self.region_name, profile_name=self.profile_name
        )
        return session.client("dynamodb")

    def put_item(self, table_name, item):
        return self.client.put_item(TableName=table_name, Item=item)


class SMSConversationsComonQueries:
    @staticmethod
    def get_conversation_between_numbers(table, number1, number2, start_time, end_time):
        chat_id = f"CHAT#{min(number1, number2)}#{max(number1, number2)}"

        response = table.query(
            KeyConditionExpression=Key("PK").eq(chat_id)
            & Key("SK").between(start_time, end_time)
        )

        return response["Items"]

    @staticmethod
    def clean_phone_number(phone_number):
        return re.sub(r"\D", "", phone_number)

    @staticmethod
    def add_message_to_conversation(table, from_number, to_number, body):
        from_number = SMSConversationsComonQueries.clean_phone_number(from_number)
        to_number = SMSConversationsComonQueries.clean_phone_number(to_number)

        chat_id = f"CHAT#{min(from_number, to_number)}#{max(from_number, to_number)}"
        timestamp = datetime.utcnow().isoformat() + "Z"
        conversation_key = f"{chat_id}#TIMESTAMP#{timestamp}"

        ttl_epoch = int((datetime.utcnow() + timedelta(days=365)).timestamp())

        item = {
            "PK": chat_id,
            "SK": conversation_key,
            "from": from_number,
            "to": to_number,
            "created_at": timestamp,
            "body": body,
            "TimeToExist": ttl_epoch,
        }

        table.put_item(Item=item)

        for number in [from_number, to_number]:
            index_item = {
                "PK": f"CONV#{number}",
                "SK": f"{chat_id}#{timestamp}",
                "created_at": timestamp,
            }
            table.put_item(Item=index_item)

    @staticmethod
    def add_phone_owner(table, phone_number, owner_name, owner_type, business_id=None):
        item = {
            "PK": f"OWNER#{phone_number}",
            "SK": "INFO",
            "name": owner_name,
            "type": owner_type,
        }

        if business_id:
            item["business_id"] = business_id

        table.put_item(Item=item)

    @staticmethod
    def get_phone_owner(table, phone_number):
        response = table.get_item(Key={"PK": f"OWNER#{phone_number}", "SK": "INFO"})

        return response.get("Item")


class BusinessReviewsCommonQueries:
    @staticmethod
    def get_review_business_info(table, business_id: str) -> Dict:
        query_params = {
            "KeyConditionExpression": Key("PK").eq(f"business#{business_id}")
            & Key("SK").eq("info")
        }

        response = table.query(**query_params)

        if response["Items"]:
            business_info = response["Items"][0]
            return business_info
        else:
            return {}

    @staticmethod
    def patch_business_info(
        table,
        business_id: str,
        business_info: Dict,
        created_at_isoformat: str = None,
    ) -> str:
        filtered_info = {k: v for k, v in business_info.items() if v is not None}
        filtered_info = json.loads(
            json.dumps(filtered_info, cls=DecimalEncoder), parse_float=Decimal
        )

        try:
            table.put_item(
                Item={
                    "PK": f"business#{business_id}",
                    "SK": "info",
                    "created_at": created_at_isoformat
                    if created_at_isoformat
                    else datetime.utcnow().isoformat(),
                    **filtered_info,
                },
                ConditionExpression="attribute_not_exists(PK) AND attribute_not_exists(SK)",
            )
            return "insert"
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                (
                    update_expr,
                    attr_values,
                    attr_names,
                ) = build_update_params_for_attributes(filtered_info)
                table.update_item(
                    Key={"PK": f"business#{business_id}", "SK": "info"},
                    UpdateExpression=update_expr,
                    ExpressionAttributeValues=attr_values,
                    ExpressionAttributeNames=attr_names,
                )
                return "update"
            else:
                raise
