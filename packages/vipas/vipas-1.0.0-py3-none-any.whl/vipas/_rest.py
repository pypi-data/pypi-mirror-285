# coding: utf-8
"""
  Copyright (c) 2024 Vipas.AI

  All rights reserved. This program and the accompanying materials
  are made available under the terms of a proprietary license which prohibits
  redistribution and use in any form, without the express prior written consent
  of Vipas.AI.
  
  This code is proprietary to Vipas.AI and is protected by copyright and
  other intellectual property laws. You may not modify, reproduce, perform,
  display, create derivative works from, repurpose, or distribute this code or any portion of it
  without the express prior written permission of Vipas.AI.
  
  For more information, contact Vipas.AI at legal@vipas.ai
"""  # noqa: E501
import json
import httpx
import time

from vipas.exceptions import ClientException

class RESTClientObject:
    def __init__(self, configuration) -> None:
        timeout = httpx.Timeout(300.0) # All requests will timeout after 300 seconds in all operations
        self.client = httpx.Client(timeout=timeout)

    def request(self, model_id, url, headers=None, body=None, async_mode=True):
        """Perform requests.

        :param method: http request method
        :param url: http request url
        :param headers: http request headers
        :param body: request json body, for `application/json`
        """
        # Prepare headers and body for the request
        headers = headers or {}

        if body is not None:
            body = json.dumps(body)

        try:
            if async_mode:
                # Make the HTTP request using httpx
                predict_data = self._handle_async_request(model_id, url, headers=headers, body=body)
            else:
                # Make the HTTP request using httpx
                predict_data = self._handle_sync_request(model_id, url, headers=headers, body=body)
            
            return self._process_predict_response(predict_data)
        
        except ClientException as e:
            raise e

    def _handle_sync_request(self, model_id, url, headers=None, body=None):
        """Handles synchronous requests."""
        try:
            predict_response = self.client.request("POST", f"{url}?model_id={model_id}", headers=headers, content=body)
            predict_response.raise_for_status()
            predict_data = predict_response.json()

            return predict_data
        except httpx.HTTPStatusError as e:
            # Handle any HTTP errors that occur while making the request
            error_detail = predict_response.json().get('detail', predict_response.text)
            raise ClientException.from_response(http_resp=predict_response, body=error_detail, data=None)
        except httpx.RequestError as e:
            # Handle any Request errors that occur while making the request
            raise ClientException(status=400, body="Bad Gateway: Request Error occurred, please try again.", data=None)
        except Exception as e:
            # Handle any other exceptions that may occur
            raise ClientException(status=500, body="Internal Server Error: Unexpected error occurred, please try again.", data=None)

    def _handle_async_request(self, model_id, url, headers=None, body=None):
        """Handles asynchronous requests."""
        try:
            task_response = self.client.request("POST", f"{url}/add_task?model_id={model_id}", headers=headers, content=body)
            task_response.raise_for_status()
            task_data = task_response.json()
                
            transaction_id = task_data.get("transaction-id", None)
        except httpx.HTTPStatusError as e:
            # Handle any HTTP errors that occur while making the request
            error_detail = task_response.json().get('detail', task_response.text)
            raise ClientException.from_response(http_resp=task_response, body=error_detail, data=None)
        except httpx.RequestError as e:
            # Handle any Request errors that occur while making the request
            raise ClientException(status=400, body="Bad Gateway: Request Error occurred, please try again.", data=None)
        except Exception as e:
            # Handle any other exceptions that may occur
            raise ClientException(status=500, body="Internal Server Error: Unexpected error occurred, please try again.", data=None)
        
        #Retrying to get the status for the current transaction id 
        return self._poll_status_and_get_result(url, headers, transaction_id)
        
    def _poll_status_and_get_result(self, url, headers, transaction_id):
        """Polls the status endpoint and retrieves the result."""
        poll_intervals = [1, 3, 3, 3, 5, 5]  # Initial intervals
        max_poll_time = 300  # Max poll time in seconds
        total_time = 0

        while total_time < max_poll_time:
            try:
                status_response = self.client.request("GET", f"{url}/status?transaction-id={transaction_id}", headers=headers)
                status_response.raise_for_status()
                status_data = status_response.json()
                
                status = status_data.get("status")
                if status.startswith("completed") or status.startswith("failed"):
                    return self._get_result(url, headers, transaction_id)

            except httpx.RequestError as e:
                raise ClientException(status=400, body="Bad Gateway: Request Error occurred, please try again.", data=None)
            except httpx.HTTPStatusError as e:
                error_detail = status_response.json().get('detail', status_response.text)
                raise ClientException.from_response(http_resp=status_response, body=error_detail, data=None)
            except ClientException as e:
                raise e
            except Exception as e:
                raise ClientException(status=500, body="Internal Server Error: Unexpected error occurred, please try again.", data=None)

            # Wait before retrying
            interval = poll_intervals.pop(0) if poll_intervals else 5  # Use 5 seconds interval if no more intervals
            total_time += interval
            time.sleep(interval)

        raise ClientException(status=504, body="Gateway Timeout: Polling timed out, please try again.", data=None)
    
    def _get_result(self, url, headers, transaction_id):
        """Retrieves the result from the result endpoint."""
        try:
            result_response = self.client.request("GET", f"{url}/result?transaction-id={transaction_id}", headers=headers)
            result_response.raise_for_status()
            result_data = result_response.json()
            return result_data
        
        except httpx.RequestError as e:
            raise ClientException(status=400, body="Bad Gateway: Request Error occurred, please try again.", data=None)
        except httpx.HTTPStatusError as e:
            error_detail = result_response.json().get('detail', result_response.text)
            raise ClientException.from_response(http_resp=result_response, body=error_detail, data=None)
        except Exception as e:
            raise ClientException(status=500, body="Internal Server Error: Unexpected error occurred, please try again.", data=None)

    def _process_predict_response(self, predict_data):
        """Processes the predict response."""
        payload_type = predict_data.get("payload_type", None)
        if payload_type == "url":
            try:
                return self._get_output_data_from_url(predict_data)
            except ClientException as e:
                raise e
        elif payload_type == "content":
            return predict_data.get("output_data", None)
        else:
            raise ClientException(status=500, body="Internal Server Error: Unexpected error occurred, please try again.", data=None)
        
    def _get_output_data_from_url(self, predict_data):
        """Retrieves output data from the provided URL."""
        try:
            output_data_response = self.client.request("GET", predict_data.get("payload_url"))
            output_data_response.raise_for_status()
            output_data = output_data_response.json()

            extractor = predict_data.get("extractor", None)
            if extractor is not None:
                # Define the function and execute the logic from the schema string
                local_vars = {'output_data': output_data}
                exec(extractor, globals(), local_vars)
                output_data = local_vars['extracted_output_data']
            
            return output_data
        except httpx.HTTPStatusError as e:
            error_detail = output_data_response.json().get('detail', output_data_response.text)
            raise ClientException.from_response(http_resp=output_data_response, body=error_detail, data=None)
        except httpx.RequestError as e:
            # Handle any errors that occur while making the request
            raise ClientException(status=400, body="Bad Gateway: Request Error occurred, please try again.", data=None)
        except Exception as e:
            # Handle any other exceptions that may occur
            raise ClientException(status=500, body="Internal Server Error: Unexpected error occurred, please try again.", data=None)
