from sqlalchemy import Column, Integer, String, Date, BIGINT, Boolean, ForeignKey
from database import Base

class UserTable(Base):
    __tablename__ = "mstr_login"
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    password = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    role_id = Column(Integer, nullable=True)
    contact_number= Column(BIGINT(), nullable= False)
    created_at = Column(Date, nullable=True)
    is_active =Column(Boolean, nullable = False)



class Role(Base):
    __tablename__ = "mstr_role"
    id = Column(Integer, primary_key=True)
    role_name = Column(String(255), unique= True)


class ActiveUser(Base):
    __tablename__ = "mstr_user"
    login_id =Column(Integer,ForeignKey('mstr_customer.id') ,primary_key=True)
    email  = Column(String(255),nullable= False)
    user_type_id = Column(Integer, nullable=True)
    ref_id = Column(Integer, nullable=True)
    first_name= Column(String(255), nullable=True)
    last_name= Column(String(255), nullable=True)
    contact_number= Column(BIGINT(), nullable=True)
    role_type= Column(String(255), nullable=True)
    department_id= Column(Integer, nullable=True)
    designation_id= Column(Integer, nullable=True)
    user_type= Column(String(255), nullable=True)



class MotorClaim  (Base):
    __tablename__ ="motor_claim_details"
    id = Column(Integer, nullable= False, primary_key=True)
    claim_no = Column(Integer, nullable= False)
    product_id = Column(Integer, ForeignKey('mstr_login.id'))
    # customer_id = Column(Integer, ForeignKey('mstr_login.id'))
    policy_number = Column(BIGINT, nullable= False)
    insurer_id = Column(BIGINT, nullable= False)
    customer_mobile_no = Column(BIGINT, nullable= False)
    claim_no = Column(String, nullable=False)



class motor_claim_form_details(Base):
    __tablename__ ="motor_claim_form_details"
    id= Column(Integer, primary_key= True)
    motor_claim_details_id = Column(Integer, ForeignKey("motor_claim_details.id"))


class MotorCustomer(Base):
    __tablename__= "mstr_customer"
    id =Column(Integer, primary_key=True)
    name= Column(String, nullable= False)    

class MotorProduct(Base):
    __tablename__="mstr_product"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    workflow_id= Column(Integer, nullable= False)


    





