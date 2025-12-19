from fastapi import APIRouter
from services.booking_service import (
    book_appointment,
    list_appointments
)

router = APIRouter()


@router.post("/book")
def book(data: dict):
    success, message = book_appointment(data)
    return {
        "success": success,
        "message": message
    }


@router.get("/appointments")
def appointments():
    return list_appointments()
