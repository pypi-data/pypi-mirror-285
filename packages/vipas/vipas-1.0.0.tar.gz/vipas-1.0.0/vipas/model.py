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

import os
import pybreaker
import json
import asyncio
from typing import Tuple, Optional, List, Dict, Any
from pydantic import Field, StrictStr
from typing_extensions import Annotated
from ratelimit import limits, sleep_and_retry

from vipas.config import Config
from vipas import _rest
from vipas.exceptions import ClientException

RequestSerialized = Tuple[str, str, Dict[str, str], Optional[Any]]

class ModelClient:
    """
        Model client for Vipas API proxy service.
        :param config: Configuration object for this client
    """
    def __init__(self, configuration=None) -> None:
        # Every time a new client is created, we need to configure it
        if configuration is None:
            configuration = Config()
        self.configuration = configuration

        self.rest_client = _rest.RESTClientObject(configuration)
        self._configure_decorators()

    def _configure_decorators(self):
        vps_env_type = os.getenv('VPS_ENV_TYPE')
        if vps_env_type == 'vipas-streamlit':
            self.rate_limit = lambda func: func  # No-op decorator
            self.breaker = pybreaker.CircuitBreaker(fail_max=20, reset_timeout=60)  # 20 failures per minute
        else:
            self.breaker = pybreaker.CircuitBreaker(fail_max=10, reset_timeout=60)  # 10 failures per minute
            self.rate_limit = limits(calls=20, period=60)  # 20 calls per minute
        
        # Apply decorators dynamically for the predict method
        self.predict = self.breaker(self.predict)
        self.predict = self.rate_limit(self.predict)
        self.predict = sleep_and_retry(self.predict)

    def predict(
        self,
        model_id: Annotated[StrictStr, Field(description="Unique identifier for the model from which the prediction is requested")],
        input_data: Annotated[Any, Field(description="Input for the prediction")],
        async_mode: Annotated[bool, Field(description="Indicates whether the SDK operates in asynchronous mode or not.")] = True
    ) -> dict:
        """
            Get Model Prediction

            Retrieves predictions from a specified model based on the provided input data. This endpoint is useful for generating real-time predictions from machine learning models.

            :param model_id: Unique identifier for the model from which the prediction is requested (required)
            :type model_id: str

            :param input_data: Input for the prediction (required)
            :type input_data: Any

            :param async_mode: Indicates whether the SDK operates in asynchronous mode or not.
            :type async_mode: bool

            :return: Returns the result object.
        """
        if async_mode:
            return self.async_predict(model_id=model_id, input_data=input_data)
        
        return self.sync_predict(model_id=model_id, input_data=input_data)
    
    def sync_predict(
        self,
        model_id: Annotated[StrictStr, Field(description="Unique identifier for the model from which the prediction is requested")],
        input_data: Annotated[Any, Field(description="Input for the prediction")],  
    ) -> dict:
        """
            Handle Sync Model Prediction
        """
        # Validate input data size
        self._validate_input_data_size(input_data)

        _param = self._predict_serialize(
            model_id=model_id,
            input_data=input_data
        )

        response_data = self._call_api(
            *_param,
            async_mode=False
        )
        return response_data
    
    def async_predict(
        self,
        model_id: Annotated[StrictStr, Field(description="Unique identifier for the model from which the prediction is requested")],
        input_data: Annotated[Any, Field(description="Input for the prediction")],
    ) -> dict:
        """
            Handle Async Model Prediction
        """
        # Validate input data size
        self._validate_input_data_size(input_data)

        _param = self._async_predict_serialize(
            model_id=model_id,
            input_data=input_data
        )

        response_data = self._call_api(
            *_param
        )
        return response_data

    def _predict_serialize(
        self,
        model_id,
        input_data
    ) -> RequestSerialized:

        _header_params: Dict[str, Optional[str]] =  {}
        _body: Any = None
        
        if input_data is not None:
            _body = input_data

        # set the HTTP header `Accept`
        _header_params['Accept'] = '*/*'
        _header_params['vps-auth-token'] = self.configuration.get_vps_auth_token()
        _header_params['vps-env-type'] = self.configuration.get_vps_env_type()
        if self.configuration.get_vps_app_id():
            _header_params['vps-app-id'] = self.configuration.get_vps_app_id()

        #Request url
        url = self.configuration.host + '/predict'
        return model_id, url, _header_params, _body
    
    def _async_predict_serialize(
        self,
        model_id,
        input_data
    ) -> RequestSerialized:

        _header_params: Dict[str, Optional[str]] =  {}
        _body: Any = None
        
        if input_data is not None:
            _body = input_data

        # set the HTTP header `Accept`
        _header_params['Accept'] = '*/*'
        _header_params['vps-auth-token'] = self.configuration.get_vps_auth_token()
        _header_params['vps-env-type'] = self.configuration.get_vps_env_type()
        if self.configuration.get_vps_app_id():
            _header_params['vps-app-id'] = self.configuration.get_vps_app_id()

        #Request url
        url = self.configuration.host + '/async_predict'
        return model_id, url, _header_params, _body

    def _call_api(
        self,
        model_id,
        url,
        header_params=None,
        body=None,
        async_mode=True
    ) -> dict:
        """Makes the HTTP request (synchronous)
        :param method: Method to call.
        :param url: Path to method endpoint.
        :param header_params: Header parameters to be placed in the request header.
        :param body: Request body.
        :return: dict of response data.
        """

        try:
            # perform request and return response
            response_data = self.rest_client.request(
                model_id, url,
                headers=header_params,
                body=body,
                async_mode=async_mode
            )

        except ClientException as e:
            raise e

        return response_data
    
    def _validate_input_data_size(self, input_data):
        """
        Validates that the size of input_data is less than 10 MB.

        :param input_data: The data to validate.
        :raises ClientException: If the input_data size is greater than 10 MB.
        """
        max_size_mb = 10
        max_size_bytes = max_size_mb * 1024 * 1024  # Convert MB to bytes

        if isinstance(input_data, str):
            input_size = len(input_data)
        elif isinstance(input_data, bytes):
            input_size = len(input_data)
        elif isinstance(input_data, (list, dict)):
            input_size = len(json.dumps(input_data))
        else:
            # Convert other types to string and check their length
            input_size = len(str(input_data))

        if input_size > max_size_bytes:
            raise ClientException(413, f"Payload size more than {max_size_mb} MB is not allowed.")
