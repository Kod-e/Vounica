# Memory Schema
from pydantic import BaseModel, Field
from datetime import datetime


class Memory(BaseModel):
    """
    The Memory schema by Pydantic.
    """
    
    id: int = Field(..., description="The ID of the memory.")
    content: str = Field(..., description="The content of the memory.")
    category: str = Field(..., description="The category of the memory.")
    priority: int = Field(..., description="The priority of the memory.")
    created_at: datetime = Field(..., description="The created time of the memory.")
    updated_at: datetime = Field(..., description="The updated time of the memory.")