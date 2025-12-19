from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


@router.post("/interact")
def interact(req: ChatRequest):
    user_message = req.message

    # TEMPORARY LOGIC (safe placeholder)
    # Later this will call triage_agent + booking_service
    reply = f"I received your message: '{user_message}'"

    return {
        "reply": reply
    }
