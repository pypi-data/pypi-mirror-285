"""Copyright 2024 Everlasting Systems and Solutions LLC (www.myeverlasting.net).
All Rights Reserved.

No part of this software or any of its contents may be reproduced, copied, modified or adapted, without the prior written consent of the author, unless otherwise indicated for stand-alone materials.

For permission requests, write to the publisher at the email address below:
office@myeverlasting.net

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
from pydantic import BaseModel,Field, AnyHttpUrl, model_validator,EmailStr
from typing import List, Optional
from typing_extensions import Self
from datetime import datetime
from espy_contact.util.enums import ResourceEnum, GradeLevel, Term
from espy_contact.util.enums import StatusEnum
from espy_contact.schema.schema import UserResponse


class Resource(BaseModel):
    """Type of resource can be Poll, Form Builder, Questionnaire, RichText, Video, Audio, File, Hyperlink."""

    id: Optional[int] = None
    title: str
    type: ResourceEnum
    lesson_id: int


class Lesson_note(BaseModel):
    id: Optional[int] = None
    title: str
    content: str
    lesson_id: Optional[int] = None


class Quiz(BaseModel):
    id: Optional[int] = None
    title: str
    question: str
    options: List[str]
    answer: str
    lesson_id: Optional[int] = None


class Lesson(BaseModel):  # defintion of biology, branches of biology
    id: Optional[int] = None
    title: str  # Intro to Biology
    quiz: Optional[Quiz] = None
    note: Optional[Lesson_note] = None
    assets: Optional[
        List[str]
    ] = []  # these are assets shared between users not same as resources
    resources: Optional[List[ResourceEnum]] = []
    topic_id: Optional[int] = None


class LessonDto(Lesson):
    class_id: Optional[int] = None


class TopicDto(BaseModel):  # Introduction to Biology
    id: Optional[int] = None
    title: str
    timestamp: Optional[datetime] = None
    subject_id: Optional[int] = None
    lessons: Optional[List[Lesson]] = []


class SubjectDto(BaseModel):
    id: Optional[int] = None
    title: str  # Biology
    class_id: Optional[int] = None  # Grade
    grade: Optional[GradeLevel] = None
    term: Term 
    topics: Optional[List[TopicDto]] = None
    lesson_count: Optional[int] = 0

    @model_validator(mode="after")
    def validate_subject_grade(self: 'SubjectDto') -> Self:
        if self.grade is None and self.class_id is None:
            raise ValueError("Either 'grade' or 'class_id' must be provided.")
        return self
    


class ClassroomDto(BaseModel):
    id: Optional[int] = None
    title: str
    subclasses: Optional[str] = None
    subjects: Optional[List[SubjectDto]] = None
    teacher: Optional[UserResponse] = None  # ManyToMany relationship with Teacher


class Makeschool(BaseModel):
    school_type: str
    classes: List[ClassroomDto]
    created_by: str


class ReviewDto(BaseModel):
    #to-do separate teacher review from subject review
    id: Optional[int] = None
    title: str
    review: str
    rating: float
    reviewer: str
    created_at: Optional[datetime] = None
    subject_id: int
    teacher_id: int
class ReviewResultDto(BaseModel):
    id: int
    name: str
    review_count: int
    average_rating: float

class Holiday(BaseModel):
    id: Optional[int] = None
    name: str
    remarks: Optional[str] = None
    start_date: datetime
    end_date: datetime
    created_at: Optional[datetime] = None
    created_by: str

class SchoolTerm(BaseModel):
    id: Optional[int] = None
    term: Term
    academic_year: int
    start_date: datetime
    end_date: datetime
    remarks: Optional[str] = None
    created_at: Optional[datetime] = None
    created_by: str

class SchoolProfile(BaseModel):
    id: Optional[int] = None
    school_id: int
    logo: Optional[str] = None
    mission: Optional[str] = None
    vision: Optional[str] = None
    motto: Optional[str] = None
    banner: Optional[str] = None
    contact: Optional[str] = None
    website: Optional[AnyHttpUrl] = None
    social_media: Optional[str] = Field(None, description='comma separated strings')
    established: Optional[int] = None
    school_type: Optional[str] = None
    affiliation: Optional[str] = None
    board: Optional[str] = None
    facilities: Optional[str] = Field(None, description='comma separated strings')
    created_at: Optional[datetime] = None

class Extracurricular(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    start_date: datetime
    end_date: datetime
    venue: Optional[str] = None
    created_by: str
    status: StatusEnum = StatusEnum.NEW
    coordinator: Optional[str] = None
    images: Optional[str] = Field(None, description='comma separated strings')
    created_at: Optional[datetime] = None

class Asset(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    worth: Optional[str] = None
    type: Optional[str] = None
    url: Optional[AnyHttpUrl] = None
    tags: Optional[str] = Field(None, description='comma separated strings')
    images: Optional[str] = Field(None, description='comma separated strings')
    created_by: str
    status: StatusEnum = StatusEnum.NEW
    created_at: Optional[datetime] = None



class Vacancy(BaseModel):
    id: Optional[int] = None
    title: str
    description: str = Field(description='detailed job description')
    requirements: Optional[str] = Field(None, description='comma separated strings')
    salary: Optional[str] = Field(None, description='amount with currency and duration e.g $48,000 per annum')
    location: Optional[str] = None
    deadline: datetime = Field(description='date you will stop accepting applications')
    created_by: str
    status: StatusEnum = StatusEnum.NEW
    created_at: Optional[datetime] = None

class Attendance(BaseModel):
    id: Optional[int] = None
    user_id: int
    subject_id: Optional[int] = None
    classroom_id: Optional[int] = None
    is_present: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: EmailStr
    remarks: Optional[str] = None
class Student_class(BaseModel):
    student_ids: list[int] 
    class_id: int
    teacher_id: Optional[int] = None 
    term: Optional[Term] = None
    year: Optional[int] = None
    