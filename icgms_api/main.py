from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from passlib.context import CryptContext
from fastapi.security import HTTPBearer
from models import UserTable, Role, ActiveUser, MotorClaim, motor_claim_form_details, MotorCustomer, MotorProduct, WorkflowStep, FormDetails,  FormField, FormStep, MotorInsurer, FormValidation, FormOption
from database import Base, engine, get_db
from hashing import hash
from router import master, master_branch, manage_user_master, question, dashboard
from dependencies import create_access_token, get_current_user
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="ICGMS DEVELOPMENT")
Base.metadata.create_all(bind=engine)

app.include_router(master.router)
app.include_router(master_branch.router)
app.include_router(manage_user_master.router)
app.include_router(question.router)
app.include_router(dashboard.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins='*',
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)



SECRET_KEY = "f388c51edeecf2d5dc5fe61e529c20cc286aa221a98c568d61d111e3d54ba0a1"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = HTTPBearer()

class RoleDetailsResponse(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    role: str
    role_id: int
    no_of_role: int

class CreateUser(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    role_id: int

class Token(BaseModel):
    access_token: str
    token_type: str


@app.post("/token/{user_type_id}", response_model=Token, tags=["SUPERADMIN"])
def login(user_type_id: int, form_data: RoleDetailsResponse, db: Session = Depends(get_db)):
    try:
        user = db.query(UserTable).filter(UserTable.role_id == user_type_id, UserTable.email == form_data.email).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not hash.verify_password(form_data.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        role = db.query(Role).filter(Role.id == user.role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        no_of_role = db.query(UserTable).filter(UserTable.role_id == user.role_id).count()

        access_token = create_access_token(data={
            "email": user.email,
            "id": user.id,
            "user_type_id": user.role_id,
            "user_role": role.role_name,
            "contact": user.contact_number,
        })
 
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "role_id": user.role_id,
            "role": role.role_name,
            "name": f"{user.first_name} {user.last_name}",
            "no_of_role": no_of_role
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


@app.post("/get_count_user", response_model=LoginResponse, tags=["SUPERADMIN"])
def get_count_user(request: RoleDetailsResponse, db: Session = Depends(get_db), current_user: UserTable = Depends(get_current_user)):
    try:
        user = db.query(UserTable).filter(UserTable.email == request.email).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid user")

        if not hash.verify_password(request.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid password")

        role = db.query(Role).filter(Role.id == user.role_id).first()
        role_count = db.query(Role).filter(Role.id == user.role_id).count()

        return LoginResponse(role_id=user.role_id, role=role.role_name, no_of_role=role_count)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get count user: {str(e)}")

@app.post("/create_user", response_model=Token, tags=["SUPERADMIN"])
def create_user(create_user: CreateUser, db: Session = Depends(get_db)):
    try:
        existing_user = db.query(UserTable).filter(UserTable.email == create_user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

        hashed_password = hash.get_hashed_password(create_user.password)
        new_user = UserTable(
            email=create_user.email,
            first_name=create_user.first_name,
            last_name=create_user.last_name,
            password=hashed_password,
            role_id=create_user.role_id,
            created_at=datetime.utcnow(),
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        access_token = create_access_token(data={"email": new_user.email, "role_id": new_user.role_id})
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User creation failed: {str(e)}")

@app.post("/get-active-user-details", tags=["SUPERADMIN"])
def get_active_user_details(db: Session = Depends(get_db), current_user: UserTable = Depends(get_current_user)):
    try:
        active_user = db.query(
            ActiveUser.login_id,
            ActiveUser.user_type_id,
            Role.role_name,
            ActiveUser.department_id,
            ActiveUser.designation_id,
            ActiveUser.ref_id,
            ActiveUser.role_type
        ).join(
            Role, Role.id == ActiveUser.login_id
        ).filter(
            ActiveUser.login_id == current_user.id 
        ).first()
        if not active_user:
            raise HTTPException(status_code=404, detail="Active user details not found")

        return {
            "login_id": active_user.login_id,
            "email": current_user.email,
            "user_type_id": active_user.user_type_id,
            "ref_id": active_user.ref_id,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "contact_number": current_user.contact_number,
            "role_type": active_user.role_type,
            "department_id": active_user.department_id,
            "designation_id": active_user.designation_id,
            "user_type": active_user.role_name,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get active user details: {str(e)}")

@app.post("/validate_role/{role_id}", tags=["SUPERADMIN"])
def validate_role(role_id: int, db: Session = Depends(get_db), current_user: UserTable = Depends(get_current_user)):
    try:
        user_role = db.query(Role).filter(Role.id == role_id).first()
        user_table = db.query(UserTable).filter(UserTable.role_id == role_id).first()
        return {
            "status": user_table.is_active,
            "role": user_role.role_name,
            "role_id": user_role.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Role validation failed: {str(e)}")


@app.post("/get_all_claim_list_superadmin", tags=["SUPERADMIN"])
def get_all_claim_list_superadmin(db: Session = Depends(get_db), current_user: UserTable = Depends(get_current_user)):
    try:
        motor_claims = db.query(
            MotorClaim.id,     
            MotorClaim.claim_no,
            MotorClaim.product_id,
            MotorClaim.policy_number,
            MotorClaim.insurer_id,
            MotorClaim.customer_mobile_no,
            motor_claim_form_details.motor_claim_details_id,
            MotorClaim.status,
            MotorProduct.name.label('product_name'),
            MotorInsurer.name.label('insurer_name'),
            WorkflowStep.workflow_id,
            WorkflowStep.child,
            WorkflowStep.route,
            WorkflowStep.name.label('workflow'),
            WorkflowStep.role_id,
        ).join(
            motor_claim_form_details, motor_claim_form_details.motor_claim_details_id == MotorClaim.id
        ).join(MotorCustomer, MotorCustomer.id == MotorClaim.id
        ).join(MotorProduct, MotorProduct.id == current_user.id
        ).join(WorkflowStep, WorkflowStep.id == current_user.id
        ).join(MotorInsurer, MotorInsurer.id == current_user.id
        ).filter(
            motor_claim_form_details.motor_claim_details_id == MotorClaim.id  
        ).all()

        return [
            {
                "claim_id": claim.id,
                "motor_claim_details_id": claim.motor_claim_details_id,
                "claim_no": claim.claim_no,
                "product_id": claim.product_id,
                "policy_number": claim.policy_number,
                "insurer_id": claim.insurer_id,
                "insurer_name": claim.insurer_name,
                "mobile_no": claim.customer_mobile_no,
                "status": claim.status,
                "product_name": claim.product_name,
                "workflow_id": claim.workflow_id,
                "name": claim.workflow,
                "route": claim.route,
                "child": claim.child,
                "role_id": [claim.role_id ]        
            }
            for claim in motor_claims
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get all claims list: {str(e)}")


@app.get("/get_form/{form_id}", tags=["SUPERADMIN"])
def get_dynamic_form_json(

    form_id: int,
    step_no: int,
    db: Session = Depends(get_db),
    current_user: UserTable = Depends(get_current_user),
):
    try:
        UserForm = (
            db.query(
                FormDetails.form_render_type,
                FormStep.id.label("step_id"),
                FormStep.title.label("step_title"),
                FormField.label,
                FormField.field_name,
                FormField.field_input_type.label("type"),
                FormField.placeholder,
                FormValidation.validation_type.label("name"),
                FormValidation.error_message.label("message"),
                FormOption.option_label.label("labeloption"),
                FormOption.option_value.label("valueoption"),
            )
            .join(FormStep, FormStep.form_id == FormDetails.id)
            .join(FormField, FormField.form_id == FormDetails.id)
            .outerjoin(FormValidation, FormValidation.field_id == FormField.id)
            .outerjoin(FormOption, FormOption.field_id == FormField.id)
            .filter(FormDetails.id == form_id)
            .all()
        )

        if not UserForm:
            raise HTTPException(status_code=404, detail="Form not found")

        step_data = {
            "form_render_type": UserForm[0].form_render_type,
            "step_id": UserForm[0].step_id,
            "step_title": UserForm[0].step_title,
            "data": []
        }

        field_map = {}

        for form in UserForm:
            field_key = (form.label, form.field_name, form.type, form.placeholder)

            if field_key not in field_map:
                field_map[field_key] = {
                    "label": form.label,
                    "name": form.field_name,
                    "type": form.type,
                    "placeholder": form.placeholder,
                    "validations": [],
                    "options": []
                }

            if form.name and form.message:
                field_map[field_key]["validations"].append({
                    "name": form.name,
                    "message": form.message
                })

            if form.labeloption and form.valueoption:
                field_map[field_key]["options"].append({
                    "label": form.labeloption,
                    "value": form.valueoption
                })

        step_data["data"].extend(field_map.values())

        return step_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dynamic form: {str(e)}")
    

@app.post("/server-time", tags=["SUPERADMIN"])
def get_server_time(db: Session= Depends(get_db)):
    return {"serverTime": datetime.now()}