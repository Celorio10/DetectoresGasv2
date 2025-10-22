from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
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
from pdf_generator import generate_certificate_pdf

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
    departamentos: List[str] = Field(default_factory=list)

class Technician(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str

class SensorDefault(BaseModel):
    """Sensor predeterminado con valores de Pre-Alarma, Alarma y Calibración"""
    model_config = ConfigDict(extra="ignore")
    sensor: str
    pre_alarm: str = ""
    alarm: str = ""
    calibration_value: str = ""

class EquipmentMaster(BaseModel):
    """Catálogo maestro de equipos - Información permanente del equipo"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    serial_number: str  # Único e inmutable
    brand: str
    model: str
    current_client_name: str = ""
    current_client_cif: str = ""
    current_client_departamento: str = ""
    default_sensors: List[SensorDefault] = Field(default_factory=list)
    general_observations: str = ""
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_workshop_entry: Optional[str] = None

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
    last_calibration_data: Optional[List['SensorCalibration']] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class CalibrationHistory(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    serial_number: str
    brand: str
    model: str
    client_name: str
    client_cif: str
    client_departamento: str
    observations: str = ""
    entry_date: str
    calibration_data: List[dict]
    spare_parts: Optional[List[dict]] = None
    calibration_date: str
    technician: str
    internal_notes: str = ""  # Notas internas del técnico
    delivery_note: Optional[str] = None
    certificate_number: Optional[str] = None
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

class SparePart(BaseModel):
    descripcion: str
    referencia: str
    garantia: bool = False

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
    spare_parts: Optional[List[SparePart]] = None
    calibration_date: Optional[str] = None
    technician: Optional[str] = None
    delivery_note: Optional[str] = None
    delivery_location: Optional[str] = None
    delivery_date: Optional[str] = None
    certificate_number: Optional[str] = None

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
    spare_parts: List[SparePart] = []
    calibration_date: str
    technician: str
    internal_notes: str = ""  # Notas internas del técnico (no aparecen en PDF)

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
    except (jwt.DecodeError, jwt.InvalidTokenError, Exception):
        raise HTTPException(status_code=401, detail="Invalid token")

# Certificate number generation
async def generate_certificate_number():
    """
    Genera un número de certificado correlativo en formato YY-NNNNN
    donde YY son los dos últimos dígitos del año actual
    y NNNNN es un número correlativo de 5 dígitos (00001-99999)
    """
    current_year = datetime.now().year
    year_suffix = str(current_year)[-2:]  # Últimos 2 dígitos del año
    
    # Buscar el último certificado del año actual
    counter_doc = await db.certificate_counters.find_one({"year": current_year})
    
    if counter_doc:
        # Incrementar el contador existente
        new_counter = counter_doc['counter'] + 1
        if new_counter > 99999:
            raise HTTPException(status_code=500, detail="Se ha alcanzado el límite de certificados para este año")
        
        await db.certificate_counters.update_one(
            {"year": current_year},
            {"$set": {"counter": new_counter}}
        )
    else:
        # Crear nuevo contador para el año
        new_counter = 1
        await db.certificate_counters.insert_one({
            "year": current_year,
            "counter": new_counter
        })
    
    # Formatear el número: YY-NNNNN
    certificate_number = f"{year_suffix}-{new_counter:05d}"
    return certificate_number

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

# Equipment Master Catalog routes
@api_router.get("/equipment-master", response_model=List[EquipmentMaster])
async def get_all_equipment_master(current_user: dict = Depends(get_current_user)):
    """Obtener todos los equipos del catálogo maestro"""
    equipment = await db.equipment_master.find({}, {"_id": 0}).sort("serial_number", 1).to_list(10000)
    return equipment

@api_router.get("/equipment-master/search")
async def search_equipment_master(
    serial: str = None,
    marca: str = None,
    modelo: str = None,
    cliente: str = None,
    current_user: dict = Depends(get_current_user)
):
    """Buscar en el catálogo maestro con filtros"""
    query = {}
    if serial:
        query["serial_number"] = {"$regex": serial, "$options": "i"}
    if marca:
        query["brand"] = {"$regex": marca, "$options": "i"}
    if modelo:
        query["model"] = {"$regex": modelo, "$options": "i"}
    if cliente:
        query["current_client_name"] = {"$regex": cliente, "$options": "i"}
    
    equipment = await db.equipment_master.find(query, {"_id": 0}).sort("serial_number", 1).to_list(10000)
    return equipment

@api_router.get("/equipment-master/{serial_number}", response_model=Optional[EquipmentMaster])
async def get_equipment_master_by_serial(serial_number: str, current_user: dict = Depends(get_current_user)):
    """Obtener equipo del catálogo maestro por número de serie"""
    equipment = await db.equipment_master.find_one({"serial_number": serial_number}, {"_id": 0})
    if not equipment:
        return None
    return equipment

@api_router.post("/equipment-master", response_model=EquipmentMaster)
async def create_equipment_master(equipment: EquipmentMaster, current_user: dict = Depends(get_current_user)):
    """Crear nuevo equipo en catálogo maestro"""
    # Verificar que no exista
    existing = await db.equipment_master.find_one({"serial_number": equipment.serial_number})
    if existing:
        raise HTTPException(status_code=400, detail=f"Equipment with serial number '{equipment.serial_number}' already exists in master catalog")
    
    equipment_dict = equipment.model_dump()
    # Convertir objetos SensorDefault a dict
    equipment_dict['default_sensors'] = [sensor.model_dump() if hasattr(sensor, 'model_dump') else sensor for sensor in equipment.default_sensors]
    
    await db.equipment_master.insert_one(equipment_dict)
    return equipment

@api_router.put("/equipment-master/{serial_number}", response_model=EquipmentMaster)
async def update_equipment_master(serial_number: str, equipment: EquipmentMaster, current_user: dict = Depends(get_current_user)):
    """Actualizar equipo en catálogo maestro"""
    existing = await db.equipment_master.find_one({"serial_number": serial_number})
    if not existing:
        raise HTTPException(status_code=404, detail="Equipment not found in master catalog")
    
    equipment_dict = equipment.model_dump()
    # Convertir objetos SensorDefault a dict
    equipment_dict['default_sensors'] = [sensor.model_dump() if hasattr(sensor, 'model_dump') else sensor for sensor in equipment.default_sensors]
    equipment_dict['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    await db.equipment_master.update_one(
        {"serial_number": serial_number},
        {"$set": equipment_dict}
    )
    
    updated = await db.equipment_master.find_one({"serial_number": serial_number}, {"_id": 0})
    return updated

@api_router.delete("/equipment-master/{serial_number}")
async def delete_equipment_master(serial_number: str, current_user: dict = Depends(get_current_user)):
    """Eliminar equipo del catálogo maestro"""
    result = await db.equipment_master.delete_one({"serial_number": serial_number})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Equipment not found in master catalog")
    return {"message": "Equipment deleted from master catalog"}

# Equipment routes
@api_router.get("/equipment-catalog/serial/{serial_number}", response_model=Optional[EquipmentCatalog])
async def get_equipment_catalog_by_serial(serial_number: str, current_user: dict = Depends(get_current_user)):
    catalog_entry = await db.equipment_catalog.find_one({"serial_number": serial_number}, {"_id": 0})
    if not catalog_entry:
        return None
    return catalog_entry

@api_router.post("/equipment", response_model=Equipment)
async def create_equipment(equipment_data: EquipmentCreate, current_user: dict = Depends(get_current_user)):
    # Validación más estricta: buscar cualquier equipo con el mismo serial que no esté delivered
    existing = await db.equipment.find_one({
        "serial_number": equipment_data.serial_number, 
        "status": {"$in": ["pending", "calibrated"]}
    })
    if existing:
        status_msg = existing.get('status', 'unknown')
        raise HTTPException(
            status_code=400, 
            detail=f"Equipment with serial number '{equipment_data.serial_number}' already exists in workshop with status '{status_msg}'"
        )
    
    equipment = Equipment(**equipment_data.model_dump())
    await db.equipment.insert_one(equipment.model_dump())
    
    # Update or create equipment catalog entry
    catalog_entry = EquipmentCatalog(
        serial_number=equipment_data.serial_number,
        brand=equipment_data.brand,
        model=equipment_data.model,
        client_name=equipment_data.client_name,
        client_cif=equipment_data.client_cif,
        client_departamento=equipment_data.client_departamento,
        last_entry_date=equipment_data.entry_date
    )
    
    await db.equipment_catalog.update_one(
        {"serial_number": equipment_data.serial_number},
        {"$set": catalog_entry.model_dump()},
        upsert=True
    )
    
    return equipment

@api_router.get("/equipment/serial/{serial_number}", response_model=Equipment)
async def get_equipment_by_serial(serial_number: str, current_user: dict = Depends(get_current_user)):
    equipment = await db.equipment.find_one({"serial_number": serial_number, "status": {"$ne": "delivered"}}, {"_id": 0})
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment

@api_router.put("/equipment/{serial_number}/calibrate", response_model=Equipment)
async def calibrate_equipment(serial_number: str, calibration: CalibrationUpdate, current_user: dict = Depends(get_current_user)):
    # Buscar el equipo que NO está delivered (el que está actualmente en el taller)
    equipment = await db.equipment.find_one({
        "serial_number": serial_number,
        "status": {"$ne": "delivered"}
    })
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found or already delivered")
    
    update_data = {
        "status": "calibrated",
        "calibration_data": [item.model_dump() for item in calibration.calibration_data],
        "spare_parts": [item.model_dump() for item in calibration.spare_parts] if calibration.spare_parts else [],
        "calibration_date": calibration.calibration_date,
        "technician": calibration.technician,
        "internal_notes": calibration.internal_notes
    }
    
    # Actualizar usando el ID específico del equipo, no solo el serial_number
    await db.equipment.update_one({"id": equipment['id']}, {"$set": update_data})
    updated = await db.equipment.find_one({"id": equipment['id']}, {"_id": 0})
    
    # Guardar en historial de calibraciones
    history_entry = CalibrationHistory(
        serial_number=equipment['serial_number'],
        brand=equipment['brand'],
        model=equipment['model'],
        client_name=equipment['client_name'],
        client_cif=equipment['client_cif'],
        client_departamento=equipment.get('client_departamento', ''),
        observations=equipment.get('observations', ''),
        entry_date=equipment['entry_date'],
        calibration_data=[item.model_dump() for item in calibration.calibration_data],
        spare_parts=[item.model_dump() for item in calibration.spare_parts] if calibration.spare_parts else [],
        calibration_date=calibration.calibration_date,
        technician=calibration.technician
    )
    history_dict = history_entry.model_dump()
    await db.calibration_history.insert_one(history_dict)
    
    # Actualizar catálogo con última calibración
    await db.equipment_catalog.update_one(
        {"serial_number": serial_number},
        {"$set": {"last_calibration_data": [item.model_dump() for item in calibration.calibration_data]}},
        upsert=False
    )
    
    return updated

@api_router.get("/equipment/pending", response_model=List[Equipment])
async def get_pending_equipment(current_user: dict = Depends(get_current_user)):
    equipment = await db.equipment.find({"status": "pending"}, {"_id": 0}).to_list(1000)
    return equipment

@api_router.get("/equipment/{serial_number}/certificate")
async def download_certificate(serial_number: str, current_user: dict = Depends(get_current_user)):
    """Generar y descargar certificado PDF de calibración"""
    equipment = await db.equipment.find_one({"serial_number": serial_number}, {"_id": 0})
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    # Aceptar tanto equipos calibrados como entregados
    if equipment.get('status') not in ['calibrated', 'delivered']:
        raise HTTPException(status_code=400, detail="Equipment not calibrated yet")
    
    # Generar el PDF
    pdf_dir = Path(ROOT_DIR) / 'temp_pdfs'
    pdf_dir.mkdir(exist_ok=True)
    
    pdf_filename = f"certificado_{serial_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf_path = pdf_dir / pdf_filename
    
    try:
        generate_certificate_pdf(equipment, str(pdf_path))
        return FileResponse(
            path=str(pdf_path),
            media_type='application/pdf',
            filename=f"Certificado_Calibracion_{serial_number}.pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

@api_router.get("/calibration-history/all", response_model=List[CalibrationHistory])
async def get_all_calibration_history(current_user: dict = Depends(get_current_user)):
    """Obtener todo el historial de calibraciones"""
    history = await db.calibration_history.find(
        {}, 
        {"_id": 0}
    ).sort("calibration_date", -1).to_list(10000)
    return history

@api_router.get("/calibration-history/search")
async def search_calibration_history(
    cliente: str = None,
    modelo: str = None,
    serial: str = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Buscar historial de calibraciones con filtros opcionales.
    Agrupa calibraciones por serial_number y retorna información del equipo con todas sus calibraciones.
    """
    # Construir query de búsqueda
    query = {}
    if cliente:
        query["client_name"] = {"$regex": cliente, "$options": "i"}
    if modelo:
        query["model"] = {"$regex": modelo, "$options": "i"}
    if serial:
        query["serial_number"] = {"$regex": serial, "$options": "i"}
    
    # Obtener todas las calibraciones que coincidan
    all_calibrations = await db.calibration_history.find(
        query,
        {"_id": 0}
    ).sort("calibration_date", -1).to_list(10000)
    
    # Agrupar por serial_number
    equipments = {}
    for cal in all_calibrations:
        serial_num = cal.get('serial_number')
        if serial_num not in equipments:
            equipments[serial_num] = {
                "serial_number": serial_num,
                "brand": cal.get('brand'),
                "model": cal.get('model'),
                "client_name": cal.get('client_name'),
                "client_departamento": cal.get('client_departamento', ''),
                "last_calibration_date": cal.get('calibration_date'),
                "calibrations": []
            }
        
        equipments[serial_num]["calibrations"].append({
            "id": cal.get('id'),
            "calibration_date": cal.get('calibration_date'),
            "technician": cal.get('technician'),
            "calibration_data": cal.get('calibration_data', []),
            "spare_parts": cal.get('spare_parts', []),
            "observations": cal.get('observations', ''),
            "certificate_number": cal.get('certificate_number', '')
        })
    
    # Convertir a lista y ordenar por última fecha de calibración
    result = list(equipments.values())
    result.sort(key=lambda x: x['last_calibration_date'], reverse=True)
    
    return result

@api_router.get("/equipment/{serial_number}/history", response_model=List[CalibrationHistory])
async def get_equipment_history(serial_number: str, current_user: dict = Depends(get_current_user)):
    """Obtener historial de calibraciones de un equipo"""
    history = await db.calibration_history.find(
        {"serial_number": serial_number}, 
        {"_id": 0}
    ).sort("calibration_date", -1).to_list(1000)
    return history

@api_router.get("/equipment/history/{history_id}/certificate")
async def download_history_certificate(history_id: str, current_user: dict = Depends(get_current_user)):
    """Generar y descargar certificado PDF de una calibración histórica"""
    history_entry = await db.calibration_history.find_one({"id": history_id}, {"_id": 0})
    if not history_entry:
        raise HTTPException(status_code=404, detail="Calibration history not found")
    
    # Generar el PDF
    pdf_dir = Path(ROOT_DIR) / 'temp_pdfs'
    pdf_dir.mkdir(exist_ok=True)
    
    pdf_filename = f"certificado_{history_entry['serial_number']}_{history_entry['calibration_date']}.pdf"
    pdf_path = pdf_dir / pdf_filename
    
    try:
        generate_certificate_pdf(history_entry, str(pdf_path))
        return FileResponse(
            path=str(pdf_path),
            media_type='application/pdf',
            filename=f"Certificado_{history_entry['serial_number']}_{history_entry['calibration_date']}.pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

@api_router.get("/equipment/calibrated", response_model=List[Equipment])
async def get_calibrated_equipment(current_user: dict = Depends(get_current_user)):
    equipment = await db.equipment.find({"status": "calibrated"}, {"_id": 0}).to_list(1000)
    return equipment

@api_router.put("/equipment/deliver")
async def deliver_equipment(delivery: DeliveryUpdate, current_user: dict = Depends(get_current_user)):
    for serial in delivery.serial_numbers:
        # Buscar el equipo calibrado específico (no delivered)
        equipment = await db.equipment.find_one({
            "serial_number": serial,
            "status": "calibrated"
        })
        if not equipment:
            continue  # Skip if not found or not calibrated
            
        # Generar número de certificado único para cada equipo
        certificate_number = await generate_certificate_number()
        
        # Actualizar equipo con datos de entrega y certificado usando ID específico
        await db.equipment.update_one(
            {"id": equipment['id']},
            {"$set": {
                "status": "delivered",
                "delivery_note": delivery.delivery_note,
                "delivery_location": delivery.delivery_location,
                "delivery_date": delivery.delivery_date,
                "certificate_number": certificate_number
            }}
        )
        
        # Actualizar historial con número de certificado y albarán
        await db.calibration_history.update_many(
            {"serial_number": serial, "certificate_number": None},
            {"$set": {
                "delivery_note": delivery.delivery_note,
                "certificate_number": certificate_number
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