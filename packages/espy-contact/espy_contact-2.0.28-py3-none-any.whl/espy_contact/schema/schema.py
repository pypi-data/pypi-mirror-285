"""Copyright 2024 Everlasting Systems and Solutions LLC (www.myeverlasting.net).
All Rights Reserved.

No part of this software or any of its contents may be reproduced, copied, modified or adapted, without the prior written consent of the author, unless otherwise indicated for stand-alone materials.

For permission requests, write to the publisher at the email address below:
office@myeverlasting.net

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
from datetime import datetime, date
from pydantic import BaseModel, EmailStr,Field, ConfigDict, field_validator,AnyHttpUrl
from espy_contact.util.enums import AccessRoleEnum, StatusEnum,GenderEnum,MonthEnum
from typing import List, Optional, Union
import uuid
class ReachBase(BaseModel):
    id: str
    timestamp: datetime
class SeoRequest(BaseModel):
    url: AnyHttpUrl = Field(description="Your website url")
class WebbuilderRequest(BaseModel):
    id: str
    content: str
    product_id: int

class UserResponse(BaseModel):
    id: Optional[int] = None
    timestamp: Optional[datetime] = datetime.now()
    first_name: str
    last_name: str
    email: EmailStr
    is_active: bool = False
    status: StatusEnum = StatusEnum.NEW
    roles: List[AccessRoleEnum]
    socialmedia: Optional[str] = None # comma separated string
    gender: GenderEnum
    token: Optional[str] = None

    @field_validator('roles')
    def validate_roles(cls, roles):
        if AccessRoleEnum.STUDENT in roles and AccessRoleEnum.ADMIN in roles:
            raise ValueError("User cannot have roles of Student and Admin at the same time")
        return roles
class AddressDto(BaseModel):
    id: Optional[int] = None
    street: str
    city: str
    state: str
    zip_code: int
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    country: str


class AppuserDto(UserResponse):
    model_config = ConfigDict(from_attributes=True)
    password: str
    address: Optional[AddressDto] = None


class EnrollmentDto(UserResponse):
    model_config = ConfigDict(from_attributes=True)
    dob: date
    gender: str
    nationality: str
    address: AddressDto
    parent_email: str
    current_school: str
    current_class: str
    achievements: str
    extracurricular: str
    parent_phone: str
    parent_name: str
    parent_occupation: str
    religion: str
    password: Optional[str] = None
    photo: Optional[Union[str, bytes]] = None
    birth_certificate: Optional[Union[str, bytes]] = None
    signature: str
    is_paid: Optional[bool] = False


class SchoolDto(BaseModel):
    id: Optional[int] = None
    name: str
    address: AddressDto
    owner_id: int
    email: Optional[EmailStr] = None
    status: Optional[StatusEnum] = StatusEnum.NEW


class SchoolResponse(BaseModel):
    id: str
    name: str
    create_at: datetime
    address_id: str
    owner_id: str


class AcademicHistory(ReachBase):
    """Student or teacher can have multiple AcademicHistory."""
    model_config = ConfigDict(from_attributes=True)

    school_name: str
    start_date: str
    end_date: str
    grade_level: str
    reason_for_leaving: str
    classroom: str  # ForeignKey to Classroom or String
    owner: AppuserDto  # ForeignKey to StudentProfile or None

    # teacher: Teacher  # Optional ForeignKey to Teacher (null allowed) or None

class GenDto(BaseModel):
    start_date: date
    end_date: date
class HomeAnalytics(BaseModel):
    student_count: int
    teacher_count: int
    tranx_total: Optional[int] = None
    expected_tranx: int
class Revenue(BaseModel):
    month: MonthEnum
    income: int
    expense: int
    refunds: int
    net: int