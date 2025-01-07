from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from dependencies import get_current_user
from pydantic import BaseModel
from models import UserTable, RoleType, ManageMasterUser, ActiveUser, GetDepartment, GetDesignation, ManageMasterUser
 

router= APIRouter(tags=["MANAGE USER MASTER"])

class ManageUser(BaseModel):
    user_type: str
    role_type: str
    first_name: str
    last_name: str
    email: str
    department_id: int
    designation_id: int
    contact_number: int

@router.post("/add-user")
def add_user_master(request: ManageUser, db:Session = Depends(get_db), current_user:UserTable= Depends(get_current_user)):
    add_user= db.query(
        ManageMasterUser.user_type,
        RoleType.role_type,
        UserTable.first_name,
        UserTable.last_name,
        UserTable.email,
        ActiveUser.department_id,
        ActiveUser.designation_id,
        UserTable.contact_number
    ).join(ManageMasterUser, ManageMasterUser.id == current_user.id
    ).join(RoleType, RoleType.id == current_user.id
    ).join(ActiveUser, ActiveUser.login_id ==current_user.id
    ).filter(current_user.email == request.email).first()

    if not add_user:
        raise HTTPException(status_code=404, detail= "Details not found")
    else:
        db.add(add_user)
        db.commit()
        db.refresh(add_user)
        return {add_user}


class GetUserList(BaseModel):
  page_number: int
  record_per_page: int
  user_type: str  

@router.post("/get-all-user-list")
def get_user_list(request: GetUserList, db:Session= Depends(get_db), current_user:UserTable= Depends(get_current_user)):
    get_user_list= db.query(
        ActiveUser.user_type_id,
        ActiveUser.ref_id,
        ActiveUser.login_id,
        ActiveUser.created_by,
        ActiveUser.created_at,
        ActiveUser.department_id,
        ActiveUser.designation_id,
        ActiveUser.branch_code,
        ActiveUser.branch_name,
        UserTable.email,
        UserTable.first_name,
        UserTable.last_name,
        UserTable.contact_number,
        GetDepartment.name,
        GetDesignation.designation_name,
        ManageMasterUser.user_type

    ).join(
        ManageMasterUser, ManageMasterUser.user_type == request.user_type
    ).join(
        UserTable, UserTable.id == ActiveUser.login_id
    ).join(
        GetDepartment, GetDepartment.id == ActiveUser.department_id
    ).join(
        GetDesignation, GetDesignation.id == ActiveUser.designation_id
    ).join(
        ManageMasterUser, ManageMasterUser.id == ActiveUser.ref_id
    ).filter(UserTable.id == ActiveUser.login_id).all()

    return get_user_list
