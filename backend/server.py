from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
import jwt

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
SECRET_KEY = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
ALGORITHM = "HS256"

app = FastAPI()
api_router = APIRouter(prefix="/api")

# Models
class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    full_name: str
    hashed_password: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class UserRegister(BaseModel):
    username: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class Brand(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str

class Model(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str

class Client(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    cif: str
    departamento: str = ""

class Technician(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str

class EquipmentCatalog(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    serial_number: str
    brand: str
    model: str
    client_name: str
    client_cif: str
    client_departamento: str = ""
    last_entry_date: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class SensorCalibration(BaseModel):
    sensor: str
    pre_alarm: str
    alarm: str
    calibration_value: str
    valor_zero: str = ""
    valor_span: str = ""
    calibration_bottle: str
    approved: bool

class Equipment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    brand: str
    model: str
    client_name: str
    client_cif: str
    client_departamento: str = ""
    serial_number: str
    observations: str = ""
    entry_date: str
    status: str = "pending"  # pending, calibrated, delivered
    calibration_data: Optional[List[SensorCalibration]] = None
    spare_parts: Optional[str] = None
    calibration_date: Optional[str] = None
    technician: Optional[str] = None
    delivery_note: Optional[str] = None
    delivery_location: Optional[str] = None
    delivery_date: Optional[str] = None

class EquipmentCreate(BaseModel):
    brand: str
    model: str
    client_name: str
    client_cif: str
    client_departamento: str = ""
    serial_number: str
    observations: str = ""
    entry_date: str

class CalibrationUpdate(BaseModel):
    calibration_data: List[SensorCalibration]
    spare_parts: str = ""
    calibration_date: str
    technician: str

class DeliveryUpdate(BaseModel):
    serial_numbers: List[str]
    delivery_note: str
    delivery_location: str
    delivery_date: str

# Auth functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = await db.users.find_one({"username": username}, {"_id": 0})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Auth routes
@api_router.post("/auth/register", response_model=User)
async def register(user_data: UserRegister):
    existing_user = await db.users.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_password = get_password_hash(user_data.password)
    user = User(
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password
    )
    
    await db.users.insert_one(user.model_dump())
    return user

@api_router.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin):
    user = await db.users.find_one({"username": user_data.username}, {"_id": 0})
    if not user or not verify_password(user_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user["username"]})
    user_safe = {"username": user["username"], "full_name": user["full_name"]}
    
    return Token(access_token=access_token, user=user_safe)

@api_router.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {"username": current_user["username"], "full_name": current_user["full_name"]}

# Brand routes
@api_router.get("/brands", response_model=List[Brand])
async def get_brands(current_user: dict = Depends(get_current_user)):
    brands = await db.brands.find({}, {"_id": 0}).to_list(1000)
    return brands

@api_router.post("/brands", response_model=Brand)
async def create_brand(brand: Brand, current_user: dict = Depends(get_current_user)):
    existing = await db.brands.find_one({"name": brand.name})
    if existing:
        raise HTTPException(status_code=400, detail="Brand already exists")
    await db.brands.insert_one(brand.model_dump())
    return brand

# Model routes
@api_router.get("/models", response_model=List[Model])
async def get_models(current_user: dict = Depends(get_current_user)):
    models = await db.models.find({}, {"_id": 0}).to_list(1000)
    return models

@api_router.post("/models", response_model=Model)
async def create_model(model: Model, current_user: dict = Depends(get_current_user)):
    existing = await db.models.find_one({"name": model.name})
    if existing:
        raise HTTPException(status_code=400, detail="Model already exists")
    await db.models.insert_one(model.model_dump())
    return model

# Client routes
@api_router.get("/clients", response_model=List[Client])
async def get_clients(current_user: dict = Depends(get_current_user)):
    clients = await db.clients.find({}, {"_id": 0}).to_list(1000)
    return clients

@api_router.post("/clients", response_model=Client)
async def create_client(client: Client, current_user: dict = Depends(get_current_user)):
    existing = await db.clients.find_one({"cif": client.cif})
    if existing:
        raise HTTPException(status_code=400, detail="Client with this CIF already exists")
    await db.clients.insert_one(client.model_dump())
    return client

# Technician routes
@api_router.get("/technicians", response_model=List[Technician])
async def get_technicians(current_user: dict = Depends(get_current_user)):
    technicians = await db.technicians.find({}, {"_id": 0}).to_list(1000)
    return technicians

@api_router.post("/technicians", response_model=Technician)
async def create_technician(technician: Technician, current_user: dict = Depends(get_current_user)):
    existing = await db.technicians.find_one({"name": technician.name})
    if existing:
        raise HTTPException(status_code=400, detail="Technician already exists")
    await db.technicians.insert_one(technician.model_dump())
    return technician

# Equipment routes
@api_router.post("/equipment", response_model=Equipment)
async def create_equipment(equipment_data: EquipmentCreate, current_user: dict = Depends(get_current_user)):
    existing = await db.equipment.find_one({"serial_number": equipment_data.serial_number, "status": {"$ne": "delivered"}})
    if existing:
        raise HTTPException(status_code=400, detail="Equipment with this serial number already in workshop")
    
    equipment = Equipment(**equipment_data.model_dump())
    await db.equipment.insert_one(equipment.model_dump())
    return equipment

@api_router.get("/equipment/serial/{serial_number}", response_model=Equipment)
async def get_equipment_by_serial(serial_number: str, current_user: dict = Depends(get_current_user)):
    equipment = await db.equipment.find_one({"serial_number": serial_number, "status": {"$ne": "delivered"}}, {"_id": 0})
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment

@api_router.put("/equipment/{serial_number}/calibrate", response_model=Equipment)
async def calibrate_equipment(serial_number: str, calibration: CalibrationUpdate, current_user: dict = Depends(get_current_user)):
    equipment = await db.equipment.find_one({"serial_number": serial_number})
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    update_data = {
        "status": "calibrated",
        "calibration_data": [item.model_dump() for item in calibration.calibration_data],
        "spare_parts": calibration.spare_parts,
        "calibration_date": calibration.calibration_date,
        "technician": calibration.technician
    }
    
    await db.equipment.update_one({"serial_number": serial_number}, {"$set": update_data})
    updated = await db.equipment.find_one({"serial_number": serial_number}, {"_id": 0})
    return updated

@api_router.get("/equipment/pending", response_model=List[Equipment])
async def get_pending_equipment(current_user: dict = Depends(get_current_user)):
    equipment = await db.equipment.find({"status": "pending"}, {"_id": 0}).to_list(1000)
    return equipment

@api_router.get("/equipment/calibrated", response_model=List[Equipment])
async def get_calibrated_equipment(current_user: dict = Depends(get_current_user)):
    equipment = await db.equipment.find({"status": "calibrated"}, {"_id": 0}).to_list(1000)
    return equipment

@api_router.put("/equipment/deliver")
async def deliver_equipment(delivery: DeliveryUpdate, current_user: dict = Depends(get_current_user)):
    for serial in delivery.serial_numbers:
        await db.equipment.update_one(
            {"serial_number": serial},
            {"$set": {
                "status": "delivered",
                "delivery_note": delivery.delivery_note,
                "delivery_location": delivery.delivery_location,
                "delivery_date": delivery.delivery_date
            }}
        )
    return {"message": f"{len(delivery.serial_numbers)} equipment delivered"}

@api_router.get("/equipment/delivered", response_model=List[Equipment])
async def get_delivered_equipment(current_user: dict = Depends(get_current_user)):
    equipment = await db.equipment.find({"status": "delivered"}, {"_id": 0}).to_list(1000)
    return equipment

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()