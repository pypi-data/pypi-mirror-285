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

import logging
import sys

class LoggerClient:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.character_limit = 300
        self.log_level = logging.DEBUG
        self._setup_logger()

    def _setup_logger(self):
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Create console handler and set level to debug
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(self.log_level)
        ch.setFormatter(formatter)
        
        # Add handler to logger if it does not already exist
        if not self.logger.handlers:
            self.logger.addHandler(ch)
            self.logger.setLevel(self.log_level)

    def _truncate_message(self, message):
        if len(message) > self.character_limit:
            return message[:self.character_limit] + '...'
        return message

    def debug(self, message, *args, **kwargs):
        truncated_message = self._truncate_message(message)
        self.logger.debug(truncated_message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        truncated_message = self._truncate_message(message)
        self.logger.info(truncated_message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        truncated_message = self._truncate_message(message)
        self.logger.warning(truncated_message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        truncated_message = self._truncate_message(message)
        self.logger.error(truncated_message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        truncated_message = self._truncate_message(message)
        self.logger.critical(truncated_message, *args, **kwargs)

