# VIPAS AI Platform SDK
The Vipas AI Python SDK provides a simple and intuitive interface to interact with the Vipas AI platform. This SDK allows you to easily make predictions using pre-trained models hosted on the Vipas AI platform.

## Requirements.

Python 3.7+

## Installation & Usage
### pip install

You can install vipas sdk from the pip repository, using the following command:

```sh
pip install vipas
```
(you may need to run `pip` with root permission: `sudo pip install vipas`)

Then import the package:
```python
import vipas
```

## Getting Started

To get started with the Vipas AI Python SDK, you need to create a ModelClient object and use it to make predictions. Below is a step-by-step guide on how to do this.

### Basic Usage

1. Import the necessary modules:
```python
from vipas import model
```

2. Create a ModelClient object:
```python
vps_model_client = model.ModelClient()
```

3. Make a prediction:

```python
model_id = "<MODEL_ID>"
api_response = vps_model_client.predict(model_id=model_id, input_data="<INPUT_DATA>")
```

### Handling Exceptions
The SDK provides specific exceptions to handle different error scenarios:

1. UnauthorizedException: Raised when the API key is invalid or missing.
2. NotFoundException: Raised when the model is not found.
3. BadRequestException: Raised when the input data is invalid.
4. ForbiddenException: Raised when the user does not have permission to access the model.
5. ConnectionException: Raised when there is a connection error.
6. RateLimitException: Raised when the rate limit is exceeded.
7. ClientException: Raised when there is a client error.

### Asynchronous Inference Mode
Asynchronous Inference Mode is a near-real-time inference option that queues incoming requests and processes them asynchronously. This mode is suitable when you need to handle `large payloads` as they arrive or run models with long inference processing times that do not require sub-second latency. `By default, the predict method operates in asynchronous mode`, which will poll the status endpoint until the result is ready. This is ideal for batch processing or tasks where immediate responses are not critical.


#### Asynchronous Inference Mode Example
```python
api_response = vps_model_client.predict(model_id=model_id, input_data="<INPUT_DATA>", async_mode=True)
```
### Real-Time Inference Mode
Real-Time Inference Mode is designed for use cases requiring real-time predictions. In this mode, the predict method processes the request immediately and returns the result without polling the status endpoint. This mode is ideal for applications that need quick, real-time responses and can afford to handle potential timeouts for long-running inferences. It is particularly suitable for interactive applications where users expect immediate feedback.

#### Real-Time Inference Mode Example
```python
api_response = vps_model_client.predict(model_id=model_id, input_data="<INPUT_DATA>", async_mode=False)
```

### Detailed Explanation
#### Asynchronous Inference Mode
##### Description:
This mode allows the system to handle requests by queuing them and processing them as resources become available. It is beneficial for scenarios where the inference task might take longer to process, and an immediate response is not necessary.

##### Behavior:
The system polls the status endpoint to check if the result is ready and returns the result once processing is complete.

##### Ideal For:
Batch processing, large payloads, long-running inference tasks.

##### Default Setting:
By default, async_mode is set to True to support heavier inference requests.

##### Example Usage:

```python
api_response = vps_model_client.predict(model_id=model_id, input_data="<INPUT_DATA>", async_mode=True)
```

#### Real-Time Inference Mode
##### Description:
This mode is intended for use cases that require immediate results. The system processes the request directly and returns the result without polling.

##### Behavior:
The request is processed immediately, and the result is returned. If the inference takes longer than 29 seconds, a 504 Gateway Timeout error is returned.

##### Ideal For:
Applications requiring sub-second latency, interactive applications needing immediate feedback.

##### Example Usage:

```python
api_response = vps_model_client.predict(model_id=model_id, input_data="<INPUT_DATA>", async_mode=False)
```

By understanding and choosing the appropriate mode for your use case, you can optimize the performance and responsiveness of your AI applications on Vipas.AI.


### Example Usage for ModelClient using asychronous inference mode

```python
from vipas import model
from vipas.exceptions import UnauthorizedException, NotFoundException, ClientException
from vipas.logger import LoggerClient

logger = LoggerClient(__name__)

def main():
    # Create a ModelClient object
    vps_model_client = model.ModelClient()

    # Make a prediction
    try:
        model_id = "<MODEL_ID>"
        api_response = vps_model_client.predict(model_id=model_id, input_data="<INPUT_DATA>")
        logger.info(f"Prediction response: {api_response}")
    except UnauthorizedException as err:
        logger.error(f"UnauthorizedException: {err}")
    except NotFoundException as err:
        logger.error(f"NotFoundException: {err}")
    except ClientException as err:
        logger.error(f"ClientException: {err}")

main()

```

## Logging
The SDK provides a LoggerClient class to handle logging. Here's how you can use it:

### LoggerClient Usage

1. Import the `LoggerClient` class:
```python
from vipas.logger import LoggerClient
```

2. Initialize the `LoggerClient`:
```python
logger = LoggerClient(__name__)
```

3. Log messages at different levels:
```python
logger.debug("This is a debug message")
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")
logger.critical("This is a critical message")

```

### Example of LoggerClient
Here is a complete example demonstrating the usage of the LoggerClient:

```python
from vipas.logger import LoggerClient

def main():
    logger = LoggerClient(__name__)
    
    logger.info("Starting the main function")
    
    try:
        # Example operation
        result = 10 / 2
        logger.debug(f"Result of division: {result}")
    except ZeroDivisionError as e:
        logger.error("Error occurred: Division by zero")
    except Exception as e:
        logger.critical(f"Unexpected error: {str(e)}")
    finally:
        logger.info("End of the main function")

main()
``` 

## Author
VIPAS.AI

## License
This project is licensed under the terms of the [vipas.ai license](LICENSE.md).

By following the above guidelines, you can effectively use the VIPAS AI Python SDK to interact with the VIPAS AI platform for making predictions, handling exceptions, and logging activities.




