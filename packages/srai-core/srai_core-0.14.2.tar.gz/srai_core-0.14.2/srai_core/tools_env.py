import datetime
import os
import time
from base64 import b64decode
from typing import Any

import boto3


def get_posix_timestamp():  # TODO move to core
    return int(time.mktime(datetime.datetime.now().timetuple()))


def get_string_from_env(env_name: str) -> str:
    value = os.environ.get(env_name)
    if value is None:
        raise Exception(f"Environment variable {env_name} is not set")
    return value


def get_string_from_env_base64(env_name: str) -> str:
    value_base64 = get_string_from_env(env_name)
    return b64decode(value_base64).decode("utf-8")


def get_path_from_env(env_name: str) -> str:
    path_file = get_string_from_env(env_name)
    if not os.path.exists(path_file):
        raise Exception(f"Path {path_file} does not exist")
    return path_file


def get_client_ec2() -> Any:
    aws_access_key_id = get_string_from_env("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = get_string_from_env("AWS_SECRET_ACCESS_KEY")
    aws_region_name = get_string_from_env("AWS_REGION_NAME")
    return boto3.client(
        "ec2",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region_name,
    )


def get_resource_ec2() -> Any:
    aws_access_key_id = get_string_from_env("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = get_string_from_env("AWS_SECRET_ACCESS_KEY")
    aws_region_name = get_string_from_env("AWS_REGION_NAME")
    return boto3.resource(
        "ec2",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region_name,
    )


def get_client_s3() -> Any:
    aws_access_key_id = get_string_from_env("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = get_string_from_env("AWS_SECRET_ACCESS_KEY")
    aws_region_name = get_string_from_env("AWS_REGION_NAME")
    return boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region_name,
    )


def get_client_ecr() -> Any:
    aws_access_key_id = get_string_from_env("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = get_string_from_env("AWS_SECRET_ACCESS_KEY")
    aws_region_name = get_string_from_env("AWS_REGION_NAME")
    return boto3.client(
        "ecr",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region_name,
    )


def get_client_ecs() -> Any:
    aws_access_key_id = get_string_from_env("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = get_string_from_env("AWS_SECRET_ACCESS_KEY")
    aws_region_name = get_string_from_env("AWS_REGION_NAME")
    return boto3.client(
        "ecs",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region_name,
    )
