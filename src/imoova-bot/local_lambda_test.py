import os
from unittest.mock import patch
from lambda_function import lambda_handler


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
    def get_parameter(self, *args, **kwargs):
        assert 'Name' in kwargs
        param = os.getenv(kwargs['Name'])
        assert param is not None
        return {
            'Parameter': {
                'Value': param,
            }
        }


if __name__ == '__main__':
    with patch('boto3.client', mock_ssm_client_builder):
        lambda_handler(None, None)
