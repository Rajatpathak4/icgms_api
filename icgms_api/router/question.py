
from fastapi import APIRouter
from datetime import datetime, timedelta
from pydantic import BaseModel

router = APIRouter()


class TimeSlot(BaseModel):
    start: str = "00:00"
    end: str = "23:59"
    interval: int = 15

def generate_time_slots(slot: TimeSlot):
    start_time = datetime.strptime(slot.start, "%H:%M")
    end_time = datetime.strptime(slot.end, "%H:%M")
    time_slots = []
    while start_time <= end_time:
        time_slots.append(start_time.strftime("%H:%M"))
        start_time += timedelta(minutes=slot.interval)
    return time_slots

@router.get("/get-time-slot")
def get_time_slot(start_time: str,end_time: str):
    slot = TimeSlot(start=start_time, end=end_time)
    time_slots = generate_time_slots(slot)
    return time_slots

    
