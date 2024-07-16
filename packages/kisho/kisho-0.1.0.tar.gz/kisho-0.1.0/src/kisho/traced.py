import openai
from functools import wraps
import logging
import uuid
import os
import sys
import requests
import datetime
import base64
import ulid  # pip install ulid-py

# Set up logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

decorators = []

KISHO_API_KEY = None
BACKPROXY_URL = "https://db-server-omega.vercel.app"
PUSH = True
session_id = str(uuid.uuid4())

# Add a configuration function


# Update functions to use the global KISHO_API_KEY
def get_user_info(api_key=KISHO_API_KEY):
    print
    headers = {
        "Kisho-Api-Key": api_key,
    }
    response = requests.get(f"{BACKPROXY_URL}/get-user-info", headers=headers)
    # print(response)
    return response.json()


def push_to_fastapi(data, table="Trace"):
    if not PUSH:
        return

    logger.info(f"Pushing data to FastAPI server: {data}")
    headers = {
        "Content-Type": "application/json",
        "Kisho-Api-Key": KISHO_API_KEY,
        "Kisho-Table": table,
        "Authorization": "KISHO-BETA-KEY",
    }
    response = requests.post(
        f"{BACKPROXY_URL}/push-data", json={"data": data}, headers=headers
    )

    logger.info(f"FastAPI server response: {response.json()}")

    if response.status_code != 200:
        raise Exception(f"Data log failed: {response.json()}")


def modify_fastapi_session(session_id, data, table="Session"):
    if not PUSH:
        return

    logger.info(f"Modifying session {session_id} with data: {data}")
    headers = {
        "Content-Type": "application/json",
        "Kisho-Api-Key": KISHO_API_KEY,
        "Kisho-Table": table,
        "ID": session_id,
    }
    response = requests.post(
        f"{BACKPROXY_URL}/modify-data", json={"data": data}, headers=headers
    )

    logger.info(f"FastAPI server response: {response.json()}")

    if response.status_code != 200:
        raise Exception(f"Data log failed: {response.json()}")


def object_to_dict(obj, memo=None):
    if memo is None:
        memo = set()
    elif id(obj) in memo:
        return None  # Skip objects that have already been processed

    memo.add(id(obj))

    if isinstance(obj, dict):
        result = {k: object_to_dict(v, memo) for k, v in obj.items()}
    elif hasattr(obj, "__dict__"):
        result = {k: object_to_dict(v, memo) for k, v in obj.__dict__.items()}
    elif isinstance(obj, (list, tuple, set)):
        result = [object_to_dict(item, memo) for item in obj]
    elif isinstance(obj, bytes):
        # Encode binary data as base64 string
        result = base64.b64encode(obj).decode("utf-8")
    else:
        result = obj

    memo.remove(id(obj))
    return result


def configure(api_key, backproxy_url="https://db-server-omega.vercel.app"):
    global KISHO_API_KEY, BACKPROXY_URL, user_id, project_id
    KISHO_API_KEY = api_key
    BACKPROXY_URL = backproxy_url

    # Get user info and set user_id and project_id
    user_info = get_user_info(api_key)

    if user_info is None:
        raise Exception("API KEY INVALID OR NOT FOUND")

    user_id = user_info["project"]["authorId"]

    project_id = user_info["project"]["id"]

    # Generate a unique session ID

    data = {
        "id": session_id,
        "projectId": project_id,
        "sessionStart": str(datetime.datetime.now()),
    }

    push_to_fastapi(data, table="Session")


class TracedChatCompletions:
    def __init__(self, client):
        self.client = client

    def create(self, *args, **kwargs):
        # Capture the input
        captured_input = {"args": args, "kwargs": kwargs, "session_id": session_id}
        logger.info(f"Session {session_id}: Captured input: {captured_input}")

        name = kwargs.pop("name", "default_name")
        metadata = kwargs.pop("metadata", {})
        tags = kwargs.pop("tags", [])
        input = kwargs.pop("input", None)
        if isinstance(input, str):
            input = {"input": input}
        elif isinstance(input, dict):
            input = {k: str(v) for k, v in input.items()}
        input_json = input

        # Check if streaming is enabled
        if kwargs.get("stream", False):
            return self._create_stream(name, metadata, tags, *args, **kwargs)
        else:
            # Send the modified request to the actual OpenAI client
            response = self.client.chat.completions.create(*args, **kwargs)
            logger.info(f"Session {session_id}: Received response: {response}")

            # Push trace data
            created_response = {
                "prompt": kwargs,
                "name": name,
                "inputs": input_json,
                "metadata": metadata,
                "id": ulid.new().str,
                "sessionId": session_id,
                "userId": user_id,
                "tags": object_to_dict(tags),
                "response": object_to_dict(response),
            }
            push_to_fastapi(created_response)

            return response

    def _create_stream(self, name, metadata, tags, *args, **kwargs):
        response = self.client.chat.completions.create(*args, **kwargs)
        complete_response = ""
        final_response = []
        for chunk in response:
            logger.info(f"Session {session_id}: Received chunk: {chunk}")
            delta_content = chunk.choices[0].delta.content
            complete_response += delta_content if delta_content else ""
            final_response.append(chunk)
            yield chunk

        logger.info(
            f"Session {session_id}: Complete streamed response: {complete_response}"
        )

        created_response = {
            "prompt": kwargs,
            "name": name,
            "metadata": metadata,
            "id": session_id,
            "sessionId": session_id,
            "userId": user_id,
            "tags": object_to_dict(tags),
            "response": object_to_dict(final_response),
        }
        push_to_fastapi(created_response)

        return complete_response


class TracedChat:
    def __init__(self, client):
        self.client = client
        self.completions = TracedChatCompletions(client)


class TracedOpenAI:
    def __init__(self, client):
        self.client = client
        self.chat = TracedChat(client)


def trace_oai(client):
    return TracedOpenAI(client)


def log_io(input, output=None, metadata=None, dataset_id=None, agent=None):
    if isinstance(input, str):
        input = {"input": input}
    elif isinstance(input, dict):
        input = {k: str(v) for k, v in input.items()}
    input_json = input

    # if isinstance(output, str):
    #     output = {"output": output}
    # elif isinstance(output, dict):
    #     output = {k: str(v) for k, v in output.items()}
    # output_json = output
    if metadata is None:
        metadata = {}

    logger.info(
        f"Session {session_id}: Logging IO with input: {input}, output: {output}, metadata: {metadata}, dataset_id: {dataset_id}"
    )

    log_entry = {
        "id": str(ulid.ULID()),
        "createdAt": datetime.datetime.now().isoformat(),
        # "session_id": session_id,
        # "user_id": user_id,
        "projectId": project_id,
        "input": input_json,
        "output": output,
        "metadata": object_to_dict(metadata),
        # "dataset_id": dataset_id,
        "agentName": agent,
    }

    # Push the log entry to FastAPI
    push_to_fastapi(log_entry, table="Data")


def trace_function(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(
            f"Session {session_id}: Tracing function '{func.__name__}' with args: {args} and kwargs: {kwargs}"
        )
        result = func(*args, **kwargs)
        logger.info(
            f"Session {session_id}: Function '{func.__name__}' returned: {result}"
        )

        decorators.append(
            {
                "timestamp": datetime.datetime.now().isoformat(),
                "function": func.__name__,
                "args": str(args),
                "kwargs": str(kwargs),
                "return_value": str(result),
                "decorator": "trace_function",
            }
        )

        # push the data to fastapi's session's decorators and modify the session
        modify_fastapi_session(session_id, {"decorators": decorators})

        return result

    return wrapper
