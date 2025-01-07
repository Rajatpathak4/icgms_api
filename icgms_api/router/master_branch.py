from fastapi import APIRouter, Depends, HTTPException, status
from dependencies import get_current_user
from sqlalchemy.orm import Session
from models import UserTable, GetCountry, GetState, GetCity, GetZones, GetBranch
from database import  get_db
from pydantic import BaseModel
import os
import pandas as pd



router= APIRouter(tags=["MASTER BRANCH"])

class branch(BaseModel): 
  branch_code: int
  branch_name: str
  city: int
  state: int
  country: int
  zone:int
  pin_code: int
  address: str
  created_by: int
  status: bool
  latitude: int
  longitude: int


@router.post("/add-master-branch")
def add_master_branch(request: branch, db: Session = Depends(get_db), current_user: UserTable = Depends(get_current_user)):
    master_branch= GetBranch(branch_code = request.branch_code,
                            branch_name = request.branch_name,
                            city_id = request.city,
                            state_id= request.state,
                            country_id= request.country,
                            zone_id= request.zone,
                            pincode= request.pin_code,
                            address= request.address,
                            created_by= request.created_by,
                            status= request.status,
                            latitude= request.latitude,
                            longitude= request.longitude,

                            )
    db.add(master_branch)
    db.commit()
    db.refresh(master_branch)
    return {
          "status": master_branch.status,
          "msg":" branch added successfully"
       
    }
       


class MasterBranch(BaseModel):
   record_per_page: int
   page_number: int

@router.post("/get-master-branch")
def get_master_branch(request: MasterBranch, db: Session= Depends(get_db), current_user: UserTable= Depends(get_current_user)):
   if request.record_per_page <= 0:
      return {"error": "record_per_page must be greater than 0"}
   offset = (request.page_number - 1) * request.record_per_page
   branches = db.query(GetBranch).offset(offset).limit(request.record_per_page).all()
   return {"branches": branches}


class UpdateBranch(BaseModel):
   branch_code: str
   branch_name: str
   city_id: int
   state_id: int
   country_id: int
   zone_id: int
   pincode: int
   address: str
   status: bool

@router.post("/update-master-branch/{id}")
def update_master_branch(id: int, request:UpdateBranch, db: Session= Depends(get_db), current_user: UserTable= Depends(get_current_user)):
   update_branch= db.query(GetBranch). filter(GetBranch.id == id).first()
   if not update_branch:
      return {
            "status": "error",
            "msg": f"No branch found with ID {id}"
        }
   else:
    update_branch.branch_code = request.branch_code
    update_branch.branch_name = request.branch_name
    update_branch.city_id = request.city_id
    update_branch.state_id = request.state_id
    update_branch.country_id = request.country_id
    update_branch.zone_id = request.zone_id
    update_branch.pincode = request.pincode
    update_branch.address = request.address
    update_branch.status = request.status

    db.commit()
    db.refresh(update_branch)
    return {    
       "status": update_branch.status,
        "msg": "Data updated successfully",
        "value": {
           "data":{}
        }
    }


@router.post("/get-branch-by_id/{id}")
def get_branch_data(id: int, db:Session= Depends(get_db), current_user: UserTable= Depends(get_current_user)):
   branch_id= db.query(
      GetCountry.id.label("country_id"),
      GetCountry.country_name,
      GetState.id.label("state_id"),
      GetState.state_name,
      GetCity.id.label("city_id"),
      GetCity.city_name,
      GetZones.id.label("zone_id"),
      GetZones.name.label("zone_name"),
      GetBranch.id.label("branch_id"),
      GetBranch.branch_code,
      GetBranch.branch_name,
      GetBranch.address
      
      ).join(GetCountry, GetBranch.country_id == GetCountry.id
      ).join(GetState, GetBranch.state_id == GetState.id
      ).join(GetCity, GetBranch.city_id == GetCity.id
      ).join(GetZones, GetBranch.zone_id == GetZones.id
      ).filter(GetBranch.id == id).all()
   
   return [
      {
          "country_id": branch.country_id,
      "country_name": branch.country_name,
      "state_id": branch.state_id,
      "state_name": branch.state_name,
      "city_id": branch.city_id,
      "city_name": branch.city_name,
      "zone_id": branch.zone_id,
      "zone_name": branch.zone_name,
      "branch_id": branch.branch_id,
      "branch_code": branch.branch_code,
      "branch_name": branch.branch_name,
      "address": branch.address,
      }
      for branch in branch_id
   ]


class DeleteBranch(BaseModel):
   delete_id: int

@router.post("/delete-branch")
def delete_branch_data(request: DeleteBranch, db: Session= Depends(get_db), current_user: UserTable= Depends(get_current_user)):
   delete_branch= db.query(GetBranch).filter(GetBranch.id == request.delete_id).delete()
   if not delete_branch:
      raise HTTPException(status_code=404, detail="Branch not found")
   else:
      db.commit()
      return [
         {
            "detail": "Branch Deleted Successfully"
         }
      ]
   


@router.post("/export-excel-branch")
def export_branch_data(db: Session = Depends(get_db), current_user: UserTable = Depends(get_current_user)):
    export_data = (
        db.query(
            GetCountry.country_name,
            GetCity.city_name,
            GetState.state_name,
            GetZones.name,
            GetBranch.branch_code,
            GetBranch.branch_name,
            GetBranch.pincode,
            GetBranch.address,
            GetBranch.status
        )
        .join(GetCountry, GetBranch.country_id == GetCountry.id)
        .join(GetCity, GetBranch.city_id == GetCity.id)
        .join(GetState, GetBranch.state_id == GetState.id)
        .join(GetZones, GetBranch.zone_id == GetZones.id)
        .all()
    )

    if not export_data:
        return {"error": "No data found for the given branches."}

    df = pd.DataFrame(export_data)

    upload_dir = "upload_files"
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, "branch_data.xlsx")
    df.to_excel(file_path, index=False)

    return {"message": "Data exported successfully", "file_path": file_path}