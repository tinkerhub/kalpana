from openai import OpenAI
from utils.openai_utils import (
    create_thread,
    upload_message,
    get_run_status,
    get_assistant_message,
    create_assistant,
    transcribe_audio
)
from utils.redis_utils import (
    get_redis_value,
    set_redis,
)
import json
import time
import os

from dotenv import load_dotenv

load_dotenv(
    dotenv_path="ops/.env",
)

openai_api_key = os.getenv("OPENAI_API_KEY")

assistant_id = get_redis_value("assistant_id")

client = OpenAI(
    api_key=openai_api_key,
)

assistant = create_assistant(client, assistant_id)

def chat(chat_id, input_message):
    history = get_redis_value(chat_id)
    if history == None:
        history = {
            "thread_id": None,
            "run_id": None,
            "status": None,
        }
    else:
        history = json.loads(history)
    thread_id = history.get("thread_id")
    run_id = history.get("run_id")
    status = history.get("status")

    try:
        run = client.beta.threads.runs.retrieve(thread_id, run_id)
    except Exception as e:
        run = None
    try:
        thread = client.beta.threads.retrieve(thread_id)
    except Exception as e:
        thread = create_thread(client)

    
    run = upload_message(client, thread.id, input_message, assistant.id)
    run, status = get_run_status(run, client, thread)

    assistant_message = get_assistant_message(client, thread.id)

    history = {
        "thread_id": thread.id,
        "run_id": run.id,
        "status": status,
    }
    history = json.dumps(history)
    set_redis(chat_id, history)

    return assistant_message, history
    

def audio_chat(chat_id, audio_file):
    input_message = transcribe_audio(audio_file, client)
    print(f"The input message is : {input_message}")
    assistant_message, history =  chat(chat_id, input_message)
    return assistant_message, history    