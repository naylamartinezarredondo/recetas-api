from sqlalchemy import Column, Integer, String, Text
from database import Base

class Receta(Base):
    __tablename__ = "recetas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    ingredientes = Column(Text)
    pasos = Column(Text)
    imagen = Column(String, nullable=True)