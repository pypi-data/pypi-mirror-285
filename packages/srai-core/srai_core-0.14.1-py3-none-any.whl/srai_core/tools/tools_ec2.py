import json
import os
import sys
import time


def load_list_image_description(
    client_ec2,
    resource_ec2,
):
    # self | amazon | aws-marketplace

    if os.path.isfile("list_image_description.json"):
        with open("list_image_description.json", "r") as file:
            return json.load(file)

    list_image_description = client_ec2.describe_images(Owners=["amazon"])["Images"]
    with open("list_image_description.json", "w") as file:
        json.dump(list_image_description, file)
    return list_image_description


def load_list_name_region(
    client_ec2,
    resource_ec2,
):
    response = client_ec2.describe_regions()
    return [region["RegionName"] for region in response["Regions"]]
    # print('Regions:', response['Regions'])


def load_list_name_availability_zone(
    client_ec2,
    resource_ec2,
):
    response = client_ec2.describe_availability_zones()
    return [region["ZoneName"] for region in response["AvailabilityZones"]]


def load_list_sir_id(client_ec2, resource_ec2):
    response = client_ec2.describe_spot_instance_requests()
    list_sir_id_pending = []
    list_sir_id_fulfilled = []
    # print(response)
    for sir in response["SpotInstanceRequests"]:
        if sir["Status"]["Code"] == "fulfilled":
            list_sir_id_fulfilled.append(sir["SpotInstanceRequestId"])
        else:
            list_sir_id_pending.append(sir["SpotInstanceRequestId"])
    return list_sir_id_pending, list_sir_id_fulfilled


def load_list_instance_id_from_list_sir_id(client_ec2, resource_ec2, list_sir_id):
    list_filter = [{"Name": "spot-instance-request-id", "Values": list_sir_id}]
    response = client_ec2.describe_spot_instance_requests(Filters=list_filter)
    list_instance_id = []
    for sir in response["SpotInstanceRequests"]:
        if sir["Status"]["Code"] == "fulfilled":
            list_instance_id.append(sir["InstanceId"])
    return list_instance_id


def load_instance_id_from_sir_id(client_ec2, resource_ec2, sir_id):
    list_instance_id = load_list_instance_id_from_list_sir_id(client_ec2, resource_ec2, [sir_id])
    if len(list_instance_id) == 1:
        return list_instance_id[0]
    else:
        print()
        return None


def load_list_instance_description(client_ec2, resource_ec2, dict_tag={}):
    response = client_ec2.describe_instances()
    list_instance_description = []
    for list_instance_description_part in response["Reservations"]:
        for instance_description in list_instance_description_part["Instances"]:
            list_instance_description.append(instance_description)
    return list_instance_description


def load_list_instance_id(client_ec2, resource_ec2):
    list_instance_description = load_list_instance_description(
        client_ec2,
        resource_ec2,
    )
    return [instance_description["InstanceId"] for instance_description in list_instance_description]


def instance_launch_spot(
    client_ec2,
    resource_ec2,
    type_instance: str,
    name_availability_zone: str,
):
    # , count=1, is_spot=False, name_type='generel'
    # type_instance = 't2.medium' # for hosting web services
    # type_instance = 't3.xlarge'
    # size_volume_gb=100,

    price_spot = instance_load_spot_price(
        client_ec2,
        resource_ec2,
        type_instance,
        name_availability_zone,
    )
    print("price: " + price_spot)
    price_spot_bid = str(float(price_spot) * 1.1)
    print("bid: " + price_spot_bid)
    sys.stdout.flush()

    sir_id = instance_request_spot(client_ec2, resource_ec2, price_spot_bid, type_instance)
    print(sir_id)
    sys.stdout.flush()
    sir_await_fulfilled(client_ec2, resource_ec2, sir_id)
    instance_id = load_instance_id_from_sir_id(client_ec2, resource_ec2, sir_id)
    print(instance_id)
    sys.stdout.flush()
    instance_await_running(client_ec2, resource_ec2, instance_id)
    return instance_id

    # image_id = 'ami-04b29aaed8d74f8f3' #Machine learning instance AMI (at least 75 GB)
    # type_instance = 't2.medium'
    # return self.instance_launch(type_instance=type_instance, image_id=image_id, size_volume_gb=100, address_id=None)


# in usd per hour
# 'p2.large' has not spot price? should be like $0.3094 per Hour
# def instance_load_spot_price(client_ec2, resource_ec2, type_instance='t2.medium'):
def instance_load_spot_price(
    client_ec2,
    resource_ec2,
    type_instance: str,
    name_availability_zone: str,
):
    list_type_instance = [type_instance]
    response = client_ec2.describe_spot_price_history(
        InstanceTypes=list_type_instance,
        MaxResults=1,
        ProductDescriptions=["Linux/UNIX (Amazon VPC)"],
        AvailabilityZone=name_availability_zone,
    )

    # print(response['SpotPriceHistory'])
    return response["SpotPriceHistory"][0]["SpotPrice"]


def instance_request_spot(client_ec2, resource_ec2, spot_price, type_instance="t2.medium"):
    launch_specification = create_launch_specification_spot(client_ec2, resource_ec2, type_instance)
    response = client_ec2.request_spot_instances(
        InstanceCount=1,
        LaunchSpecification=launch_specification,
        SpotPrice=spot_price,
        Type="one-time",
    )
    # print(response)
    sir_id = response["SpotInstanceRequests"][0]["SpotInstanceRequestId"]
    return sir_id


def sir_await_fulfilled(client_ec2, resource_ec2, sir_id):
    print("await spot_instance_request_fulfilled")
    sys.stdout.flush()
    waiter = client_ec2.get_waiter("spot_instance_request_fulfilled")
    waiter.wait(SpotInstanceRequestIds=[sir_id])
    instance_id = load_instance_id_from_sir_id(client_ec2, resource_ec2, sir_id)
    while not instance_id:
        time.sleep(1)
        instance_id = load_instance_id_from_sir_id(client_ec2, resource_ec2, sir_id)
    print("spot_instance_request_fulfilled")
    sys.stdout.flush()
    return instance_id


def load_list_sir_description(client_ec2):
    response = client_ec2.describe_spot_instance_requests()
    return response["SpotInstanceRequests"]


# TODO use this for regular ones as well
def create_launch_specification_spot(
    client_ec2,
    resource_ec2,
    type_instance="t2.medium",
    name_availability_zone="us-east-1a",
):
    name_key = "south_river_main"
    id_image = "ami-04b29aaed8d74f8f3"  # Machine learning instance AMI (at least 75 GB) #TODO replace this a we are using mostly docker

    # list_security_group = [{'GroupName': 'string','GroupId': 'string'}]
    list_security_group_id = ["sg-001a357692a7d0ee7"]  # Any
    list_mapping_block_device = [
        {
            "DeviceName": "/dev/sda1",
            "Ebs": {
                "DeleteOnTermination": True,
                "SnapshotId": "snap-0f968e137b5347031",
                "VolumeSize": 100,
                "VolumeType": "gp2",
                "Encrypted": False,
            },
        }
    ]
    launch_specification = {}
    launch_specification["ImageId"] = id_image
    launch_specification["KeyName"] = name_key
    # launch_specification['SecurityGroups'] = list_security_group
    launch_specification["SecurityGroupIds"] = list_security_group_id
    launch_specification["InstanceType"] = type_instance
    launch_specification["Placement"] = {"AvailabilityZone": name_availability_zone}
    launch_specification["BlockDeviceMappings"] = list_mapping_block_device
    return launch_specification


# def instance_launch_small(client_ec2,resource_ec2, ):
#     image_id = '' #Machine learning instance AMI (at least 75 GB)
#     type_instance = '' #get the smallest amount of
#     # spin up a machine
#     return self.instance_launch(type_instance=type_instance, image_id=image_id, size_volume_gb=100, address_id=None)


def instance_launch_general(client_ec2, resource_ec2, size_volume_gb=100, address_id=None):
    image_id = "ami-04b29aaed8d74f8f3"  # Machine learning instance AMI (at least 75 GB)
    type_instance = "t2.medium"
    return instance_launch(
        client_ec2,
        resource_ec2,
        type_instance=type_instance,
        image_id=image_id,
        size_volume_gb=100,
        address_id=None,
    )


# def instance_launch_train(client_ec2,resource_ec2, ):
#     image_id = 'ami-04b29aaed8d74f8f3' #Machine learning instance AMI (at least 75 GB)
#     type_instance = 'p2.large' #get the smallest amount of
#     # spin up a machine
#     return self.instance_launch(type_instance=type_instance, image_id=image_id, size_volume_gb=100, address_id=None)


def instance_launch(client_ec2, resource_ec2, type_instance: str, size_volume_gb=100, address_id=None):
    # spin up a machine
    KeyName = "south_river_main"
    InstanceType = type_instance
    ImageId = "ami-04b29aaed8d74f8f3"
    SecurityGroupIds = ["sg-001a357692a7d0ee7"]  # Any
    BlockDeviceMappings = [
        {
            "DeviceName": "/dev/sda1",
            "Ebs": {
                "DeleteOnTermination": True,
                "SnapshotId": "snap-0f968e137b5347031",
                "VolumeSize": 100,
                "VolumeType": "gp2",
                "Encrypted": False,
            },
        }
    ]

    instance = resource_ec2.create_instances(
        BlockDeviceMappings=BlockDeviceMappings,
        ImageId=ImageId,
        SecurityGroupIds=SecurityGroupIds,
        InstanceType=InstanceType,
        KeyName=KeyName,
        MinCount=1,
        MaxCount=1,
    )[0]

    if address_id:  # attach ip
        address = resource_ec2.VpcAddress(address_id)
        address.associate(instance.instance_id)
    return instance.instance_id


def instance_get_hostname(client_ec2, resource_ec2, instance_id):
    hostname = resource_ec2.Instance(instance_id).public_dns_name
    return hostname


def instance_await_running(client_ec2, resource_ec2, instance_id):
    waiter = client_ec2.get_waiter("instance_running")
    waiter.wait(InstanceIds=[instance_id])


def instance_await_terminated(client_ec2, resource_ec2, instance_id):
    waiter = client_ec2.get_waiter("instance_terminated")
    waiter.wait(InstanceIds=[instance_id])


def instance_terminate(client_ec2, resource_ec2, instance_id):
    list_instance_id = [instance_id]
    client_ec2.terminate_instances(InstanceIds=list_instance_id)


def instance_terminate_all(client_ec2, resource_ec2):
    list_instance_id = load_list_instance_id(client_ec2, resource_ec2)
    client_ec2.terminate_instances(InstanceIds=list_instance_id)
