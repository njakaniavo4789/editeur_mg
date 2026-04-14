import os
import logging
from dotenv import load_dotenv

load_dotenv()

import google.generativeai as genai

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_INSTRUCTION = (
    "Tsy maintsy mamaly amin'ny teny malagasy foana ianao, "
    "na inona na inona fiteny ampiasain'ny olona miresaka aminao. "
    "Raha misy teny teknika dia azonao hazavaina amin'ny teny malagasy tsotra. "
    "Ianao dia mpanolo-tsaina amin'ny fanoratra teny malagasy. "
    "Manampia amin'ny fanitsiana teny, fanomezana hevitra, ary fanatsarana ny fanoratana."
)

_sessions = {}


def get_chat_session(user_id: str = "default"):
    if user_id not in _sessions:
        if not GEMINI_API_KEY:
            return None
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_INSTRUCTION
        )
        _sessions[user_id] = model.start_chat(history=[])
    return _sessions[user_id]


def envoyer_message(message: str, user_id: str = "default") -> str:
    if not GEMINI_API_KEY:
        return "Chatbot tsy misy API key. Mba amboary ny .env file."

    try:
        chat = get_chat_session(user_id)
        if chat is None:
            return "Chatbot tsy ampy intelo."
        response = chat.send_message(message)
        return response.text
    except Exception as e:
        logger.error(f"Chatbot error: {e}")
        return f"Nisy olana : {str(e)[:100]}"


def reset_session(user_id: str = "default"):
    if user_id in _sessions:
        del _sessions[user_id]
