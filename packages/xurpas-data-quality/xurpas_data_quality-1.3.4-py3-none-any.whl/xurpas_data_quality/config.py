from pydantic import BaseModel
from pydantic_settings import BaseSettings
from typing import List

class Colors(BaseModel):
    base_colors: List[str] = ['#17A2B8', "#28A745", "#0D6EFD", "#DC3545", "#FFC107"]

class Settings(BaseSettings):
    colors: Colors = Colors()
    