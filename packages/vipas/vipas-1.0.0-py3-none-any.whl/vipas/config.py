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
from urllib.parse import unquote
from vipas.exceptions import ClientException

class Config:
    """This class contains various settings of the vipas API client.

    :param vps_auth_token: Variable to store the API key for a particular user.

    Example:
    config = Configuration(
       vps_auth_token = <your_api_key>
    )

    """

    def __init__(self, vps_auth_token=None) -> None:
        """
            Constructor for the configuration class
        """
        self.host = "https://proxy.vipas.ai" 
        """
            Default Host for the proxy service.
        """

        # Authentication Settings
        self.vps_auth_token = None
        self.vps_app_id = None
        self.vps_env_type = "vipas-external"

        if vps_auth_token:
            self.vps_auth_token = vps_auth_token
        """
            Variable to store API key for a particular user.
        """

        if not self.vps_auth_token:
            self.setup_api_key()

    def setup_api_key(self):
        """Set up API key based on environment."""
        env_type = os.getenv("VPS_ENV_TYPE")
        if env_type == "vipas-streamlit":
            self.host = os.getenv("VPS_PROXY_INTERNAL_URL")
            self.vps_auth_token = self.extract_websocket_api_key()
            self.vps_app_id = self.extract_websocket_app_id()
            self.vps_env_type = env_type
        else:
            self.vps_auth_token = os.getenv("VPS_AUTH_TOKEN")
            if self.vps_auth_token is None or len(self.vps_auth_token) == 0:
                raise ClientException(400, "VPS_AUTH_TOKEN is not set in the environment variables or it is empty")

    def extract_websocket_api_key(self):
        """Extract API key from WebSocket headers in Streamlit."""
        try:
            from streamlit.web.server.websocket_headers import _get_websocket_headers
            headers = _get_websocket_headers()
            if headers and 'Cookie' in headers:
                cookie_string = headers['Cookie']
                cookies = {k.strip(): unquote(v.strip()) for k, v in 
                        (cookie.split('=') for cookie in cookie_string.split(';'))}
                
                if 'vps-auth-token' in cookies and len(cookies['vps-auth-token']) > 0:
                    return cookies['vps-auth-token']
                else:
                    return ""
            else:
                return ""
        except ImportError:
            raise ClientException(500, "Failed to import streamlit module")
        except Exception as e:
            raise ClientException(500, str(e))
        
    def extract_websocket_app_id(self):
        """Extract app id from WebSocket headers in Streamlit."""
        try:
            from streamlit.web.server.websocket_headers import _get_websocket_headers
            headers = _get_websocket_headers()
            if headers and 'Cookie' in headers:
                cookie_string = headers['Cookie']
                cookies = {k.strip(): unquote(v.strip()) for k, v in
                        (cookie.split('=') for cookie in cookie_string.split(';'))}
                if 'vps-app-id' in cookies and len(cookies['vps-app-id']) > 0:
                    return cookies['vps-app-id']
                else:
                    return ""
            else:
                return ""
        except ImportError:
            raise ClientException(500, "Failed to import streamlit module")
        except Exception as e:
            raise ClientException(500, str(e))

    def get_vps_auth_token(self):
        """
            Gets API key for a particular user.
        """
        if self.vps_auth_token is not None:
            return self.vps_auth_token
        return None
    
    def get_vps_app_id(self):
        """
            Gets app id for a particular user.
        """
        if self.vps_app_id is not None:
            return self.vps_app_id
        return None
    
    def get_vps_env_type(self):
        """
            Gets environment type for a particular user.
        """
        if self.vps_env_type is not None:
            return self.vps_env_type
        return None
