from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, Receta
from pydantic import BaseModel
from typing import List
from auth import verificar_admin
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import shutil
import os



Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


# Dependencia para obtener sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Esquemas Pydantic
class RecetaCreate(BaseModel):
    titulo: str
    ingredientes: str
    pasos: str

class RecetaOut(RecetaCreate):
    id: int
    class Config:
        orm_mode = True

# Ruta para ver recetas
@app.get("/recetas", response_model=List[RecetaOut])
def leer_recetas(db: Session = Depends(get_db)):
    return db.query(Receta).all()

# # Ruta para agregar receta (solo para admin en el futuro) sin auth
# @app.post("/recetas", response_model=RecetaOut)
# def crear_receta(receta: RecetaCreate, db: Session = Depends(get_db)):
#     db_receta = Receta(**receta.dict())
#     db.add(db_receta)
#     db.commit()
#     db.refresh(db_receta)
#     return db_receta

# @app.post("/recetas", response_model=RecetaOut)
# def crear_receta(
#     receta: RecetaCreate,
#     db: Session = Depends(get_db),
#     usuario: str = Depends(verificar_admin)  # ← Aquí se verifica el admin
# ):
#     db_receta = Receta(**receta.dict())
#     db.add(db_receta)
#     db.commit()
#     db.refresh(db_receta)
#     return 

@app.post("/recetas", response_model=RecetaOut)
def crear_receta_con_imagen(
    titulo: str = Form(...),
    ingredientes: str = Form(...),
    pasos: str = Form(...),
    imagen: UploadFile = File(None),
    db: Session = Depends(get_db),
    usuario: str = Depends(verificar_admin)
):
    imagen_url = None
    if imagen:
        ext = imagen.filename.split('.')[-1]
        nombre_archivo = f"{titulo.replace(' ', '_')}.{ext}"
        ruta_archivo = f"static/{nombre_archivo}"

        with open(ruta_archivo, "wb") as buffer:
            shutil.copyfileobj(imagen.file, buffer)

        imagen_url = f"/static/{nombre_archivo}"

    nueva_receta = Receta(titulo=titulo, ingredientes=ingredientes, pasos=pasos, imagen=imagen_url)
    db.add(nueva_receta)
    db.commit()
    db.refresh(nueva_receta)
    return nueva_receta


# Actualizar receta
# @app.put("/recetas/{receta_id}", response_model=RecetaOut)
# def actualizar_receta(
#     receta_id: int,
#     receta_actualizada: RecetaCreate,
#     db: Session = Depends(get_db),
#     usuario: str = Depends(verificar_admin)
# ):
#     receta = db.query(Receta).filter(Receta.id == receta_id).first()
#     if not receta:
#         raise HTTPException(status_code=404, detail="Receta no encontrada")

#     receta.titulo = receta_actualizada.titulo
#     receta.ingredientes = receta_actualizada.ingredientes
#     receta.pasos = receta_actualizada.pasos

#     db.commit()
#     db.refresh(receta)
#     return receta

#   Actualizar Receta con Imagen
@app.put("/recetas/{receta_id}", response_model=RecetaOut)
def actualizar_receta_con_imagen(
    receta_id: int,
    titulo: str = Form(...),
    ingredientes: str = Form(...),
    pasos: str = Form(...),
    imagen: UploadFile = File(None),
    db: Session = Depends(get_db),
    usuario: str = Depends(verificar_admin)
):
    receta = db.query(Receta).filter(Receta.id == receta_id).first()
    if not receta:
        raise HTTPException(status_code=404, detail="Receta no encontrada")

    receta.titulo = titulo
    receta.ingredientes = ingredientes
    receta.pasos = pasos

    # Si se manda una nueva imagen, se guarda
    if imagen:
        ext = imagen.filename.split('.')[-1]
        nombre_archivo = f"{titulo.replace(' ', '_')}_{receta_id}.{ext}"
        ruta_archivo = f"static/{nombre_archivo}"

        with open(ruta_archivo, "wb") as buffer:
            shutil.copyfileobj(imagen.file, buffer)

        receta.imagen = f"/static/{nombre_archivo}"

    db.commit()
    db.refresh(receta)
    return receta


# Eliminar receta
@app.delete("/recetas/{receta_id}")
def eliminar_receta(
    receta_id: int,
    db: Session = Depends(get_db),
    usuario: str = Depends(verificar_admin)
):
    receta = db.query(Receta).filter(Receta.id == receta_id).first()
    if not receta:
        raise HTTPException(status_code=404, detail="Receta no encontrada")

    db.delete(receta)
    db.commit()
    return {"mensaje": f"Receta con ID {receta_id} eliminada correctamente"}


