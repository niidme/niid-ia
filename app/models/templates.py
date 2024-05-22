# models/templates.py

from pydantic import BaseModel

class UserPrompt(BaseModel):
    user_input: str
    user_id: str