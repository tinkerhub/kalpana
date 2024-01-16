from dotenv import load_dotenv
from utils.redis_utils import set_redis
import time
import os


load_dotenv(
    dotenv_path="ops/.env",
)

openai_api_key = os.getenv("OPENAI_API_KEY")

MAIN_PROMPT_PATH = os.getenv("MAIN_PROMPT_PATH")

with open(MAIN_PROMPT_PATH, "r") as f:
    MAIN_PROMPT = f.read()

DATA_FILE_PATH = "data/data.pdf"

def create_assistant(client, assistant_id):
    try:
        assistant = client.beta.assistants.retrieve(assistant_id=assistant_id)
        return assistant
    except Exception as e:
        file = client.files.create(
            file=open(DATA_FILE_PATH, "rb"),
            purpose='assistants'
        )
        print(file.id)
        assistant = client.beta.assistants.create(
            name="Complaint Assistant",
            instructions=MAIN_PROMPT,
            model="gpt-4-1106-preview",
            tools=[
                    {
                        "type": "retrieval"
                    }
                ],
            file_ids=[
                file.id
            ]
        )
        set_redis("assistant_id", assistant.id)
        return assistant
    
def create_thread(client):
    thread = client.beta.threads.create()
    return thread

def upload_message(client, thread_id, input_message, assistant_id):
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=input_message
    )

    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )
    
    return run

def get_run_status(run, client, thread):
    i = 0

    while run.status not in ["completed", "failed"]:
        if i>0:
            time.sleep(10)

        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        i += 1
    return run, run.status

def get_assistant_message(client, thread_id):
    messages = client.beta.threads.messages.list(
        thread_id=thread_id,
    )
    return messages.data[0].content[0].text.value


def transcribe_audio(audio_file, client):
    transcript = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
    )
    return transcript.text