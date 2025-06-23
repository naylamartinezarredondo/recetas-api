from typing import Optional
from pydantic import BaseModel


class RecetaOut(BaseModel):
    id: int
    titulo: str
    ingredientes: str
    pasos: str
    imagen: Optional[str] = None

    class Config:
        orm_mode = True
