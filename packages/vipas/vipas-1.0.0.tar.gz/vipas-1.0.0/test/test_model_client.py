import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from vipas.model import ModelClient
from vipas.config import Config
from vipas.exceptions import ClientException, UnauthorizedException, ConnectionException
import os

class TestModelClient(unittest.TestCase):
    def setUp(self):
        # Setup the configuration and the ModelClient
        with patch('vipas.config.os') as mock_env:
            mock_env.getenv.return_value = 'fake_value'
            self.config = Config()
            
        self.client = ModelClient(configuration=self.config)

        # Mocking the RESTClientObject within ModelClient
        self.client.rest_client = MagicMock()

        # Prepare a RESTResponse to use in tests
        self.mock_response = {"status" : "success"}

    def test_async_model_predict_success(self):
        # Setup mock response
        self.client.rest_client.request.return_value = self.mock_response

        # Call the predict function
        result = self.client.predict(model_id="test-model", input_data="Sample data")

        # Check if the result is as expected
        self.assertEqual(result, {"status": "success"})

        # Ensure that the request was called with correct parameters
        self.client.rest_client.request.assert_called_with(
            'test-model',
            self.config.host + '/async_predict',
            headers={'Accept': '*/*', 'vps-auth-token': 'fake_value', 'vps-env-type': 'vipas-external'},
            body="Sample data",
            async_mode=True
        )

    def test_sync_model_predict_success(self):
        # Setup mock response
        self.client.rest_client.request.return_value = self.mock_response

        # Call the predict function
        result = self.client.predict(model_id="test-model", input_data="Sample data", async_mode=False)

        # Check if the result is as expected
        self.assertEqual(result, {"status": "success"})

        # Ensure that the request was called with correct parameters
        self.client.rest_client.request.assert_called_with(
            'test-model',
            self.config.host + '/predict',
            headers={'Accept': '*/*', 'vps-auth-token': 'fake_value', 'vps-env-type': 'vipas-external'},
            body="Sample data",
            async_mode=False
        )
        
    def test_predict_api_failure_input_validation_failed(self):
        # Setup mock response
        self.client.rest_client.request.return_value = self.mock_response

        over_1mb_string = 'a' * 11*1024*1024 #More than 10 MB input
        with self.assertRaises(ClientException):
            self.client.predict(model_id="test-model", input_data=over_1mb_string)
    
    def test_predict_api_failure_for_request_unauthorization_exception(self):
        self.client.rest_client.request.side_effect = UnauthorizedException(status=400)
        with self.assertRaises(UnauthorizedException):
            self.client.predict(model_id="test-model", input_data="Sample data")

    def test_predict_api_failure_for_request_connection_exception(self):
        self.client.rest_client.request.side_effect = ConnectionException(status=400)
        with self.assertRaises(ConnectionException):
            self.client.predict(model_id="test-model", input_data="Sample data")

    def test_predict_client_failure_for_request_unexpected_exception(self):
        # Patch the environment variable within this test
        self.client.rest_client.request.side_effect = ClientException(status=400)
        with self.assertRaises(ClientException):
            self.client.predict(model_id="test-model", input_data="Sample data")

if __name__ == '__main__':
    unittest.main()
