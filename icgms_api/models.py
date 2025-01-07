from sqlalchemy import Column, Integer, String, Date, BIGINT, Boolean, ForeignKey, TIMESTAMP
from database import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, date


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
    email = Column(String, nullable=False, unique=True)




class Role(Base):
    __tablename__ = "mstr_role"
    id = Column(Integer, primary_key=True)
    role_name = Column(String(255), unique= True)
    created_at= Column(Date, nullable= False)



class ActiveUser(Base):
    __tablename__ = "mstr_user"
    login_id =Column(Integer,ForeignKey('mstr_customer.id') ,primary_key=True)
    user_type_id = Column(Integer, nullable=True)
    ref_id = Column(Integer, nullable=True)
    first_name= Column(String(255), nullable=True)
    last_name= Column(String(255), nullable=True)
    department_id= Column(Integer, nullable=True)
    designation_id= Column(Integer, nullable=True)
    # user_type= Column(String(255), nullable=True)
    created_by= Column(Integer, nullable= False)
    created_at= Column(Date, nullable= False)
    branch_name= Column(String(255), nullable= False)
    branch_code= Column(String(255), nullable= False)



class MotorClaim(Base):
    __tablename__ ="motor_claim_details"
    id = Column(Integer, nullable= False, primary_key=True)
    claim_no = Column(String(255), nullable= False)
    product_id = Column(Integer, ForeignKey('mstr_login.id'))
    policy_number = Column(Integer, nullable= False)
    insurer_id = Column(BIGINT, nullable= False)
    customer_mobile_no = Column(BIGINT, nullable= False)
    claim_no = Column(String(255), nullable=False)
    status = Column(String(255), nullable= False)
    policy_from= Column(Date, nullable= False)
    policy_to= Column(Date, nullable= False)




class motor_claim_form_details(Base):
    __tablename__ ="motor_claim_form_details"
    id= Column(Integer, primary_key= True)
    motor_claim_details_id = Column(Integer, ForeignKey("motor_claim_details.id"))

class MotorInsurer(Base):
    __tablename__="mstr_insurer"
    id= Column(Integer, primary_key= True)
    name= Column(String(255), nullable= False)

class MotorCustomer(Base):
    __tablename__= "mstr_customer"
    id =Column(Integer, primary_key=True)
    name= Column(String, nullable= False)    

class MotorProduct(Base):
    __tablename__="mstr_product"
    id = Column(Integer,ForeignKey("mstr_login.id"), primary_key=True)
    name = Column(String(255), nullable=False)
    workflow_id= Column(Integer, nullable= False)


class WorkflowStep(Base):
    __tablename__= "workflow_steps"
    id= Column(Integer, primary_key= True)
    workflow_id = Column(Integer, nullable= False)
    name= Column(String(255), nullable= False)
    route = Column(String(255), nullable=False)
    child = Column(String(255), nullable= False)
    role_id = Column(Integer, nullable= False)


class FormDetails(Base):
    __tablename__="form_details"
    id= Column(Integer, primary_key= True)
    form_render_type= Column(nullable=True)


class FormStep(Base):
    __tablename__ ="form_steps"
    id= Column(Integer,ForeignKey('mstr_login.id'), primary_key= True)
    title= Column(String(255), nullable= False)
    form_id = Column(Integer,ForeignKey('form_details.id'), nullable= False)

class FormField(Base):
    __tablename__="form_fields"
    id= Column(Integer, primary_key= True, nullable= False)
    form_id= Column(Integer,ForeignKey('form_steps.id'))
    label= Column(String(255), nullable= False)
    field_name= Column(String(255), nullable= False)
    field_type= Column(String(255), nullable= False)
    placeholder= Column(String(255), nullable= False)
    field_input_type= Column(String(255), nullable= False)



class FormValidation(Base):
    __tablename__ = "form_field_validations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    field_id: Mapped[int] = mapped_column(Integer, nullable=False)
    validation_type: Mapped[str] = mapped_column(String, nullable=False)
    error_message: Mapped[str] = mapped_column(String, nullable=False)


class FormOption(Base):
    __tablename__= "form_field_options"
    id= Column(Integer, primary_key= True)
    field_id = Column(Integer,ForeignKey('form_fields.id'))
    option_label = Column(String(255), nullable= False)
    option_value = Column(String(255), nullable= False)


class GetCountry(Base):
    __tablename__="mstr_country"
    id = Column(Integer, primary_key=True)
    country_name= Column(String, nullable= False)
    created_at= Column(Date, nullable= False)
    created_by= Column(Integer, nullable= False)

class GetState(Base):
      __tablename__="mstr_state"
      id = Column(Integer, primary_key=True)
      state_name= Column(String, nullable= False)
      country_id= Column(Integer, ForeignKey("mstr_country.id"),nullable= False)
      created_at= Column(Date, nullable= False)
      created_by= Column(Integer, nullable= False)


class GetCity(Base):
    __tablename__="mstr_city"
    id = Column(Integer, primary_key=True)
    city_name= Column(String, nullable= False)
    state_id= Column(Integer, ForeignKey("mstr_state.id"),nullable= False)
    created_at= Column(Date, nullable= False)
    created_by= Column(Integer, nullable= False)


class GetDocument(Base):
    __tablename__="mstr_document"
    id = Column(Integer, primary_key=True)
    file_name=Column(String(255), nullable= False)
    path= Column(String(255),nullable= False)
    is_verified= Column(Boolean, nullable= False)
    module_name= Column(String(255), nullable= False)
    created_by= Column(Integer, nullable=False)
    created_at= Column(Date, nullable= False)


class GetZones(Base):
    __tablename__="mstr_zone"
    id = Column(Integer, primary_key=True)
    name= Column(String(255), nullable= False)
    created_by= Column(Integer, nullable= False)
    created_at= Column(Date, nullable= False)


class GetDepartment(Base):
    __tablename__="mstr_department"
    id= Column(Integer, primary_key=True)
    name= Column(String(255), nullable= False)
    created_by= Column(Integer, nullable= False)
    created_at= Column(Date, nullable= False)

class GetDesignation(Base):
    __tablename__="mstr_designation"
    id= Column(Integer, primary_key=True)
    designation_name= Column(String(255), nullable= False)
    created_at= Column(Date, nullable= False)
    created_by= Column(Integer, nullable= False)


class GetBranch(Base):
    __tablename__="mstr_branch"
    id= Column(Integer, primary_key=True)
    created_by= Column(Integer, nullable= False)
    created_at= Column(TIMESTAMP,default=datetime.now, nullable= False)
    branch_code= Column(Integer, nullable= False)
    branch_name= Column(String(255), nullable= False)
    country_id = Column(Integer,ForeignKey("mstr_country.id"), nullable= False)
    city_id= Column(Integer,ForeignKey("mstr_city.id"), nullable= False)
    state_id= Column(Integer,ForeignKey("mstr_state.id"), nullable= False)
    zone_id= Column(Integer, ForeignKey("mstr_zone.id"), nullable= False)
    pincode= Column(Integer, nullable= False)
    latitude= Column(Integer, nullable= False)
    longitude= Column(Integer, nullable= False)
    status= Column(Boolean, nullable= False)
    address= Column(String(255), nullable= False)



# MANAGE MASTER USER    
class ManageMasterUser(Base):
    __tablename__= "mstr_user_type"
    id= Column(Integer, primary_key=True, nullable= False)
    user_type= Column(String, nullable= False)


class RoleType(Base):
    __tablename__="mstr_role_type"
    id= Column(Integer, primary_key= True, nullable= False)
    role_type= Column(String, nullable= False)


    




    





