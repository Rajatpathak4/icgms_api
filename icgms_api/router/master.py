from fastapi import APIRouter, Depends, HTTPException, status
from dependencies import get_current_user
from sqlalchemy.orm import Session
from models import UserTable, GetCountry, GetState, GetCity, GetDocument, GetZones, GetBranch, GetDepartment, Role, GetDesignation
from database import  get_db
from pydantic import BaseModel



router= APIRouter(tags=["USER MASTER"])



@router.post("/get-countries")
def get_countries(db: Session= Depends(get_db), current_user: UserTable= Depends(get_current_user)):
    country= db.query(GetCountry).all()
    return [
        {
        "country_name": country.country_name,
        "created_at": country.created_at,
        "id": country.id,
        "created_by": country.created_by
    }
    for country in country
]



class state(BaseModel):
    country_id: int


@router.post("/get-states")
def get_states(request: state, db: Session = Depends(get_db), current_user: UserTable = Depends(get_current_user)):
    states = (
        db.query(
            GetState.id,
            GetState.state_name,
            GetState.country_id,
            GetState.created_at,
            GetState.created_by,
        )
        .join(GetCountry, GetCountry.id == GetState.country_id)  
        .filter(GetState.country_id == request.country_id) 
        .all()
    )
    
    return [
        {
            "created_by": state.created_by,
            "created_at": state.created_at,
            "state_name": state.state_name,
            "country_id": state.country_id,
            "id": state.id,
        }
        for state in states
    ]


class city(BaseModel):
    state_id: int


@router.post("/get-cities")
def get_cities(request: city, db: Session = Depends(get_db), current_user: UserTable = Depends(get_current_user)):
    cities = (
        db.query(GetCity)
        .join(GetState, GetState.id == GetCity.state_id)
        .filter(GetCity.state_id == request.state_id)
        .all()
    )
    return [
        {
            "state_id": city.state_id,
            "city_name": city.city_name,
            "id": city.id,
            "created_by": city.created_by,
            "created_at": city.created_at,
        }
        for city in cities
    ]



@router.post("/get-documents")
def get_documents(db: Session = Depends(get_db), current_user: UserTable= Depends(get_current_user)):
    documents = db.query(GetDocument).all()
    # return documents
    return [
        {
            "module_name": docs.module_name,
            "id": docs.id,
            "is_verified": docs.is_verified,
            "path": docs.path,
            "file_name": docs.file_name,
            "created_by": docs.created_by,
            "created_at": docs.created_at,
        }
        for docs in documents
    ]
    

@router.post("/get-zones")
def get_zones(db: Session = Depends(get_db), current_user: UserTable = Depends(get_current_user)):
    zones = db.query(GetZones).all()
    return [
        {
            "name": zone.name,
            "created_by": zone.created_by,
            "id": zone.id,
            "created_at": zone.created_at
        }
        for zone in zones
    ]


@router.post("/get-branches")
def get_branches(db: Session = Depends(get_db), current_user: UserTable = Depends(get_current_user)):
    branches = db.query(GetBranch).all()
    if not branches:
        return {
            "status": "FALSE",
            "msg": "No Data Found"
            }
    

@router.post("/get-departments")
def get_departments(db: Session = Depends(get_db), current_user: UserTable = Depends(get_current_user)):
    departments = db.query(GetDepartment).all()
    return [
        {
            "name": dept.name,
            "created_by":dept.created_by,
            "id": dept.id,
            "created_at": dept.created_at
        }
        for dept in departments
    ]


@router.post("/get-roles")
def get_roles(db: Session = Depends(get_db), current_user: UserTable = Depends(get_current_user)):
    roles= db.query(Role).all()
    return [
        {
            "created_at": role.created_at,
            "id": role.id,
            "role_name": role.role_name

        }
        for role in roles
    ]


@router.post("/get_designation")
def get_designation(db:Session= Depends(get_db), current_user: UserTable= Depends(get_current_user)):
    designation = db.query(GetDesignation).all()
    return [
        {
            "created_at": designation.created_at,
            "id":designation.id,
            "created_by":designation.created_by,
            "designation_name": designation.designation_name
        }
        for designation in designation
    ]
