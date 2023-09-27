from fastapi import APIRouter
from core.ai import chat
from core.models import Message


router = APIRouter()

history = {}

@router.post("/web")
async def process_web_message(message: Message):
    chat_id = message.chat_id
    text = message.text
    history = history.get(chat_id, [])
    response, new_history = chat(text, history)
    history[chat_id] = new_history
    return {"message": response}
    