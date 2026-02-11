from pydantic import BaseModel, ConfigDict, Field, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)

class UserCreate(UserBase):
    password:str = Field(min_length=8)

class UserPublic(BaseModel): 
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    image_file: str | None
    image_path: str #This is not a db column, it's a property defined in the model

class UserPrivate(UserPublic):
    email: EmailStr

class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=120)
    image_file: str | None = Field(default=None, min_length=1, max_length=200)

class Token(BaseModel):
    access_token: str
    token_type: str

# This is shared for creating and returning tasks
class TaskBase(BaseModel):
    task: str = Field(min_length=1, max_length=100)
    due: datetime
    done: bool


# The schema for creating tasks stays the same
class TaskCreate(TaskBase):
    user_id : int #Temporary for testing

class TaskUpdate(BaseModel):
    task: str | None = Field(default=None, min_length=1, max_length=100)
    due: datetime | None = Field(default=None)
    done: bool | None = Field(default=None)


# The schema for returning tasks needs extra stuff
class TaskResponse(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created: datetime
    author: UserPublic
