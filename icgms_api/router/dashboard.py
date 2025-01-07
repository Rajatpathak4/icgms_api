from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import date
from models import MotorClaim, MotorProduct  
from database import get_db
from sqlalchemy import func

router = APIRouter(tags=["DASHBOARD"])

class GetComposition(BaseModel):
    start_date: date
    end_date: date


@router.post("/get-composition-of-claim-initiated")
def get_composition_of_claim_initiated(request: GetComposition, db: Session = Depends(get_db)):   
    compositions = db.query(
        MotorClaim.product_id,
        MotorProduct.name,
        func.count(MotorClaim.id).label("count")
    ).join(
        MotorProduct, MotorProduct.id == MotorClaim.product_id
    ).filter(
        MotorClaim.policy_from >= request.start_date,
        MotorClaim.policy_to <= request.end_date
    ).group_by(
        MotorClaim.product_id, MotorProduct.name
    ).all()

    total_initiated = db.query(func.count(MotorClaim.id)).filter(
        MotorClaim.policy_from >= request.start_date,
        MotorClaim.policy_to <= request.end_date
    ).scalar()
    
    return [
        {
            "status": "TRUE",
            "msg": "Data Load Successfully",
            "value": [
                {
                    "product_id": comp.product_id,
                    "product_name": comp.name,
                    "total_initiated": total_initiated,
                    "total_count": comp.count,
                    "percentage": round((comp.count / total_initiated) * 100, 2),
                    "total_initiated_per": f"{round((comp.count / total_initiated) * 100, 2)}%",
                    "color": [
                        "#00E396",
                        "#FEB019",
                        "#FF4560",
                        "#39ff33",
                        "#a233ff"
                    ]
                }
                for comp in compositions
            ]
        }
    ]


class TaskDistribution(BaseModel):
    start_date: date
    end_date: date
    product_id: int

@router.post("/get-task-distribution")
def get_task_distribution(request: TaskDistribution, db: Session= Depends(get_db)):
    return {
        "details": "Successfull"
    }
        
