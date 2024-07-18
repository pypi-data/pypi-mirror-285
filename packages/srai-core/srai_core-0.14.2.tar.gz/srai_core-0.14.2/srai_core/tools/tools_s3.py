import json
from typing import Any, Optional, Tuple

import boto3
from botocore.exceptions import ClientError


def create_client_and_resource_s3(
    aws_access_key_id: str,
    aws_secret_access_key: str,
    aws_name_region: str,
) -> Tuple[Any, Any]:
    client_s3 = boto3.client(
        "s3",
        region_name=aws_name_region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    resource_s3 = boto3.resource(
        "s3",
        region_name=aws_name_region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    return client_s3, resource_s3


def bucket_exists(client_s3, resource_s3, bucket_name: str) -> bool:
    # print(type(client_s3))
    # print(type(resource_s3))
    try:
        client_s3.head_bucket(Bucket=bucket_name)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        else:
            raise Exception("fail")


def bucket_create_read_only(client_s3, resource_s3, bucket_name: str, aws_region_name: str) -> None:
    # Create the S3 bucket
    try:
        client_s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": aws_region_name})
        print(f"Bucket {bucket_name} created successfully.")
    except Exception as e:
        print(f"Error creating bucket: {e}")

    # Bucket policy - Grants read-only access to anonymous users
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AddPerm",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*",
            }
        ],
    }

    # Convert the policy to a JSON string
    policy_string = json.dumps(bucket_policy)

    # public_access_block = bucket_public_access_block_load(client_s3, resource_s3, bucket_name)
    # print(f"Public access block configuration: {public_access_block}")
    try:
        # Removing the public access block configuration
        client_s3.delete_public_access_block(Bucket=bucket_name)
        print(f"Public access block removed for bucket: {bucket_name}")
    except Exception as e:
        print(f"Error removing public access block: {e}")

    # Apply the bucket policy
    try:
        client_s3.put_bucket_policy(Bucket=bucket_name, Policy=policy_string)
        print(f"Read-only bucket policy applied to {bucket_name}.")
    except Exception as e:
        print(f"Error applying bucket policy: {e}")
    # Reapplying this this after seems wrong
    # Apply the public access block configuration
    # bucket_public_access_block_save(client_s3, resource_s3, bucket_name, **public_access_block)
    # print(f"Public access block configuration applied to {bucket_name}.")


def bucket_list(client_s3, resource_s3):
    response = client_s3.list_buckets()
    return [bucket["Name"] for bucket in response["Buckets"]]


def bucket_public_access_block_load(client_s3, resource_s3, name_bucket: str) -> dict:
    return client_s3.get_public_access_block(Bucket=name_bucket)["PublicAccessBlockConfiguration"]


def bucket_public_access_block_save(
    client_s3,
    resource_s3,
    name_bucket: str,
    BlockPublicAcls: Optional[bool] = None,
    IgnorePublicAcls: Optional[bool] = None,
    BlockPublicPolicy: Optional[bool] = None,
    RestrictPublicBuckets: Optional[bool] = None,
):
    try:
        dict_pabc = bucket_public_access_block_load(client_s3, resource_s3, name_bucket)
    except ClientError as client_error:
        if client_error.response["Error"]["Code"] == "NoSuchPublicAccessBlockConfiguration":
            dict_pabc = {
                "BlockPublicAcls": False,
                "IgnorePublicAcls": False,
                "BlockPublicPolicy": False,
                "RestrictPublicBuckets": False,
            }
        else:
            raise Exception("fail")
    changed = False
    if (not BlockPublicAcls is None) and (BlockPublicAcls != dict_pabc["BlockPublicAcls"]):
        dict_pabc["BlockPublicAcls"] = BlockPublicAcls
        changed = True

    if (not IgnorePublicAcls is None) and (IgnorePublicAcls != dict_pabc["IgnorePublicAcls"]):
        dict_pabc["IgnorePublicAcls"] = IgnorePublicAcls
        changed = True

    if (not BlockPublicPolicy is None) and (BlockPublicPolicy != dict_pabc["BlockPublicPolicy"]):
        dict_pabc["BlockPublicPolicy"] = BlockPublicPolicy
        changed = True

    if (not RestrictPublicBuckets is None) and (RestrictPublicBuckets != dict_pabc["RestrictPublicBuckets"]):
        dict_pabc["RestrictPublicBuckets"] = RestrictPublicBuckets
        changed = True

    if changed:
        client_s3.put_public_access_block(Bucket=name_bucket, PublicAccessBlockConfiguration=dict_pabc)


def bucket_read_policy(client_s3, resource_s3, name_bucket: str):
    return resource_s3.BucketPolicy(name_bucket).policy


def bucket_delete(client_s3, resource_s3, name_bucket: str):
    resource_s3.Bucket(name_bucket).delete()


def object_exists(client_s3, resource_s3, name_bucket: str, name_object: str):
    try:
        resource_s3.Object(name_bucket, name_object).load()
    except ClientError as client_error:
        if client_error.response["Error"]["Code"] == "404":
            return False
        elif client_error.response["Error"]["Code"] == "403":
            raise Exception("Access denied")
        else:
            raise Exception("fail")
    else:
        return True


@staticmethod
def object_save(client_s3, resource_s3, name_bucket: str, name_object: str, bytearray_object: bytearray):
    object_s3 = resource_s3.Object(name_bucket, name_object)
    object_s3.put(Body=bytearray_object)


@staticmethod
def object_is_public_save(client_s3, resource_s3, name_bucket: str, name_object: str, is_public: bool = False) -> None:
    object_s3_acl = resource_s3.ObjectAcl(name_bucket, name_object)
    if is_public:
        object_s3_acl.put(ACL="public-read")
    else:
        object_s3_acl.put(ACL="private")


@staticmethod
def object_is_public_load(client_s3, resource_s3, name_bucket: str, name_object: str) -> bool:
    object_s3_acl = resource_s3.ObjectAcl(name_bucket, name_object)
    # object_s3_acl.put(ACL='public-read')
    for grant in object_s3_acl.grants:
        if grant["Grantee"]["Type"] == "Group":
            if (
                grant["Permission"] == "READ"
                and grant["Grantee"]["URI"] == "http://acs.amazonaws.com/groups/global/AllUsers"
            ):
                return True
    return False
    # object_s3_acl.put(ACL='private')
    # object_s3_acl.load()
    # print(object_s3_acl.grants)


#    {'Grantee': {'Type': 'Group', 'URI': 'http://acs.amazonaws.com/groups/global/AllUsers'}, 'Permission': 'READ'}
# if is_public:
#     object_s3_acl.put(ACL='public-read')
# else:
#     object_s3_acl.put(ACL='private')


@staticmethod
def object_load(client_s3, resource_s3, name_bucket: str, name_object: str):
    return resource_s3.Object(name_bucket, name_object).get()["Body"].read()


@staticmethod
def object_delete(client_s3, resource_s3, name_bucket: str, name_object: str):
    resource_s3.Object(name_bucket, name_object).delete()


@staticmethod
def object_size(client_s3, resource_s3, name_bucket: str, name_object: str):
    return resource_s3.Bucket(name_bucket).Object(name_object).content_length


@staticmethod
def list_name_object_for_prefix(client_s3, resource_s3, name_bucket, prefix):
    bucket = resource_s3.Bucket(name_bucket)
    object_summary_iterator = bucket.objects.filter(
        Delimiter=",",
        EncodingType="url",
        MaxKeys=1000,
        Prefix=prefix,
    )
    list_name_object = []
    for object_summary in object_summary_iterator:
        list_name_object.append(object_summary.key)

    return list_name_object
