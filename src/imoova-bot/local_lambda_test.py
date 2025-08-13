import os
from unittest.mock import patch
from lambda_function import lambda_handler
import boto3


def patch_dynamo_with_local_dynamo(*args):
    assert args[0] == 'dynamodb'
    global original_boto3_resource
    return original_boto3_resource(
        'dynamodb',
        endpoint_url='http://localhost:8000',
        aws_access_key_id='dummy',
        aws_secret_access_key='dummy',
        region_name='local',
    )


def mock_ssm_client_builder(*args, **kwargs):
    assert args[0] == 'ssm'
    return MockSSMClient()


class MockSSMClient:
    """
    Mock SSM Client which fetches parameters from local Environment variables instead of AWS
    """

    def __init__(self):
        pass

    @staticmethod
    def get_parameter(*args, **kwargs):
        assert 'Name' in kwargs
        param = os.getenv(kwargs['Name'])
        assert param is not None
        return {
            'Parameter': {
                'Value': param,
            }
        }


if __name__ == '__main__':
    original_boto3_resource = boto3.resource
    with (patch('boto3.client', mock_ssm_client_builder),
          patch('boto3.resource', patch_dynamo_with_local_dynamo, spec=True)):
        print(lambda_handler(None, None))
