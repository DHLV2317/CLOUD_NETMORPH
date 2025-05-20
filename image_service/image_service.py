from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import shutil
import os
import requests
from jose import JWTError, jwt

# Configuración
SECRET_KEY = "slice-secret-key"
ALGORITHM = "HS256"

DB_USER = "sliceuser"
DB_PASSWORD = "slicepass"
DB_HOST = "mariadb"
DB_NAME = "slicedb"

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
IMAGES_DIR = "./images"
os.makedirs(IMAGES_DIR, exist_ok=True)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Modelo SQLAlchemy
class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    path = Column(Text)
    filename = Column(String(255))
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    uploaded_at = Column(TIMESTAMP, default=datetime.utcnow)

# Pydantic
class ImageDownloadRequest(BaseModel):
    url: str

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Obtener usuario desde token JWT
def get_current_user(authorization: str = Depends(lambda: None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token no proporcionado")

    token = authorization[7:]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return {"id": user_id}
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

# Subida desde archivo
@app.post("/images/upload")
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    filename = file.filename
    filepath = os.path.join(IMAGES_DIR, filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    image = Image(name=filename.split('.')[0], filename=filename, path=filepath, owner_id=user["id"])
    db.add(image)
    db.commit()

    return {"message": "Imagen subida correctamente", "filename": filename}

# Subida desde URL
@app.post("/images/download")
def download_image(req: ImageDownloadRequest, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    filename = req.url.split("/")[-1]
    if not (filename.endswith(".qcow2") or filename.endswith(".img")):
        raise HTTPException(status_code=400, detail="Formato no soportado")

    filepath = os.path.join(IMAGES_DIR, filename)
    try:
        r = requests.get(req.url, stream=True, timeout=30)
        with open(filepath, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al descargar: {str(e)}")

    image = Image(name=filename.split('.')[0], filename=filename, path=filepath, owner_id=user["id"])
    db.add(image)
    db.commit()

    return {"message": "Imagen descargada correctamente", "filename": filename}
