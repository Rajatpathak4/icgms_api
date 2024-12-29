from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi.security import HTTPBearer
from jose import jwt, JWTError
from models import UserTable, Role, ActiveUser, MotorClaim, motor_claim_form_details, MotorCustomer,MotorProduct
from database import Base, engine, get_db
from hashing import hash



app = FastAPI()
Base.metadata.create_all(bind=engine)

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
    




def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")




def get_current_user(
    token: str = Depends(oauth2_scheme),db: Session = Depends(get_db),):
    try:
        payload = decode_token(token.credentials) 
        user_id: int = payload.get("id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
        user = db.query(UserTable).filter(UserTable.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )





# Endpoint
@app.post("/token/{user_type_id}", response_model=Token)
def login( form_data: RoleDetailsResponse, db: Session = Depends(get_db)):
    user = db.query(UserTable).filter(UserTable.email == form_data.email).first()
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


@app.post("/get_count_user", response_model=LoginResponse)
def get_count_user(request: RoleDetailsResponse,db: Session = Depends(get_db), current_user: UserTable = Depends(get_current_user)):
    user = db.query(UserTable).filter(UserTable.email == request.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")

    if not hash.verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    role = db.query(Role).filter(Role.id == user.role_id).first()
    role_count = db.query(Role).filter(Role.id == user.role_id).count()
    # no_of_count = db.query(UserTable).filter(UserTable.role_id == request.email).count()

    return LoginResponse(role_id=user.role_id, role=role.role_name, no_of_role=role_count)



@app.post("/create_user", response_model=Token)
def create_user(create_user: CreateUser, db: Session = Depends(get_db)):
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



@app.post("/get-active-user-details")
def get_active_user_details(db: Session = Depends(get_db), current_user: UserTable = Depends(get_current_user)):
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

    return{
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


@app.post("/validate_role/{role_id}")
def validate_role(role_id: int, db: Session = Depends(get_db), current_user: UserTable = Depends(get_current_user)):
    user_role=db.query(Role).filter(Role.id == role_id).first()
    user_table= db.query(UserTable).filter(UserTable.role_id == role_id).first()
    return {
        "status": user_table.is_active,
        "role": user_role.role_name,
        "role_id": user_role.id
    }



@app.post("/get_all_claim_list_superadmin")
def get_all_claim_list_superadmin(db: Session = Depends(get_db), current_user: UserTable = Depends(get_current_user)):
    
    motor_claims = db.query(
        MotorClaim.id,     
        MotorClaim.claim_no,
        MotorClaim.product_id,
        MotorClaim.policy_number,
        MotorClaim.insurer_id,
        MotorClaim.customer_mobile_no,
        motor_claim_form_details.motor_claim_details_id,
        # MotorCustomer.name,
        MotorProduct.name,
        MotorProduct.workflow_id
    ).join(
        motor_claim_form_details, motor_claim_form_details.motor_claim_details_id == MotorClaim.id

    # ).join(MotorCustomer, MotorCustomer.id == MotorClaim.id
           
    ).join( MotorProduct, MotorProduct.id == current_user.id

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
            "mobile_no": claim.customer_mobile_no,
            # "customer_name": claim.name,
            "product_name": claim.name,
            "workflow_id": claim.workflow_id
        }
        for claim in motor_claims
    ]
