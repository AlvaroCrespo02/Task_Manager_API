from pydantic import BaseModel, ConfigDict, Field
from datetime import date

# This is shared for creating and returning tasks
class TaskBase(BaseModel):
    task: str = Field(min_length=1, max_length=100)
    due: date
    done: bool


# The schema for creating tasks stays the same
class TaskCreate(TaskBase):
    pass

# The schema for returning tasks needs extra stuff
class TaskResponse(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created: date
