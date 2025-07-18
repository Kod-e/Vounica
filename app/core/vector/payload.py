from pydantic import BaseModel
class VectorPayload(BaseModel):
    user_id: int
    created_at: int  # UNIX 时间戳