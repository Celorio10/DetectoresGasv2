import requests
import sys
import json
from datetime import datetime

class WorkshopAPITester:
    def __init__(self, base_url="https://equipment-tracker-12.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            
            if success:
                self.log_test(name, True)
                try:
                    return True, response.json()
                except:
                    return True, response.text
            else:
                details = f"Expected {expected_status}, got {response.status_code}. Response: {response.text[:200]}"
                self.log_test(name, False, details)
                return False, {}

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return False, {}

    def test_auth_register(self):
        """Test user registration"""
        test_user = f"testuser_{datetime.now().strftime('%H%M%S')}"
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data={
                "username": test_user,
                "password": "TestPass123!",
                "full_name": "Test User"
            }
        )
        return success, test_user

    def test_auth_login(self, username):
        """Test user login"""
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data={
                "username": username,
                "password": "TestPass123!"
            }
        )
        if success and 'access_token' in response:
            self.token = response['access_token']
            return True
        return False

    def test_auth_me(self):
        """Test get current user"""
        success, _ = self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200
        )
        return success

    def test_create_brand(self):
        """Test creating a brand"""
        brand_name = f"TestBrand_{datetime.now().strftime('%H%M%S')}"
        success, response = self.run_test(
            "Create Brand",
            "POST",
            "brands",
            200,
            data={"name": brand_name}
        )
        return success, brand_name

    def test_get_brands(self):
        """Test getting brands"""
        success, _ = self.run_test(
            "Get Brands",
            "GET",
            "brands",
            200
        )
        return success

    def test_create_model(self):
        """Test creating a model"""
        model_name = f"TestModel_{datetime.now().strftime('%H%M%S')}"
        success, response = self.run_test(
            "Create Model",
            "POST",
            "models",
            200,
            data={"name": model_name}
        )
        return success, model_name

    def test_get_models(self):
        """Test getting models"""
        success, _ = self.run_test(
            "Get Models",
            "GET",
            "models",
            200
        )
        return success

    def test_create_client(self):
        """Test creating a client with departamento field"""
        client_data = {
            "name": f"Cliente Test {datetime.now().strftime('%H%M%S')}",
            "cif": f"A{datetime.now().strftime('%H%M%S')}",
            "departamento": "Mantenimiento"
        }
        success, response = self.run_test(
            "Create Client with Departamento",
            "POST",
            "clients",
            200,
            data=client_data
        )
        return success, client_data

    def test_get_clients(self):
        """Test getting clients"""
        success, _ = self.run_test(
            "Get Clients",
            "GET",
            "clients",
            200
        )
        return success

    def test_create_technician(self):
        """Test creating a technician"""
        tech_name = f"TestTech_{datetime.now().strftime('%H%M%S')}"
        success, response = self.run_test(
            "Create Technician",
            "POST",
            "technicians",
            200,
            data={"name": tech_name}
        )
        return success, tech_name

    def test_get_technicians(self):
        """Test getting technicians"""
        success, _ = self.run_test(
            "Get Technicians",
            "GET",
            "technicians",
            200
        )
        return success

    def test_create_equipment(self, brand, model, client):
        """Test creating equipment with departamento field"""
        serial_number = f"SN-TEST-{datetime.now().strftime('%H%M%S')}"
        equipment_data = {
            "brand": brand,
            "model": model,
            "client_name": client["name"],
            "client_cif": client["cif"],
            "client_departamento": client["departamento"],
            "serial_number": serial_number,
            "observations": "Equipo de prueba FASE 1",
            "entry_date": datetime.now().strftime('%Y-%m-%d')
        }
        success, response = self.run_test(
            "Create Equipment with Departamento",
            "POST",
            "equipment",
            200,
            data=equipment_data
        )
        return success, serial_number

    def test_get_equipment_by_serial(self, serial_number):
        """Test getting equipment by serial number"""
        success, response = self.run_test(
            "Get Equipment by Serial",
            "GET",
            f"equipment/serial/{serial_number}",
            200
        )
        return success, response

    def test_calibrate_equipment(self, serial_number, technician):
        """Test calibrating equipment with valor_zero and valor_span fields"""
        calibration_data = {
            "calibration_data": [
                {
                    "sensor": "CO",
                    "pre_alarm": "25",
                    "alarm": "50",
                    "calibration_value": "100",
                    "valor_zero": "0",
                    "valor_span": "100",
                    "calibration_bottle": "BOT-001",
                    "approved": True
                }
            ],
            "spare_parts": "Filtro reemplazado",
            "calibration_date": datetime.now().strftime('%Y-%m-%d'),
            "technician": technician
        }
        success, response = self.run_test(
            "Calibrate Equipment with Valor Zero/Span",
            "PUT",
            f"equipment/{serial_number}/calibrate",
            200,
            data=calibration_data
        )
        return success, response

    def test_get_calibrated_equipment(self):
        """Test getting calibrated equipment"""
        success, response = self.run_test(
            "Get Calibrated Equipment",
            "GET",
            "equipment/calibrated",
            200
        )
        return success, response

    def test_deliver_equipment(self, serial_numbers):
        """Test delivering equipment"""
        delivery_data = {
            "serial_numbers": serial_numbers,
            "delivery_note": f"DN{datetime.now().strftime('%H%M%S')}",
            "delivery_location": "Test Location",
            "delivery_date": datetime.now().strftime('%Y-%m-%d')
        }
        success, response = self.run_test(
            "Deliver Equipment",
            "PUT",
            "equipment/deliver",
            200,
            data=delivery_data
        )
        return success

    def test_get_delivered_equipment(self):
        """Test getting delivered equipment"""
        success, response = self.run_test(
            "Get Delivered Equipment",
            "GET",
            "equipment/delivered",
            200
        )
        return success

    def test_get_equipment_catalog_by_serial(self, serial_number):
        """Test getting equipment from catalog by serial number"""
        success, response = self.run_test(
            "Get Equipment Catalog by Serial",
            "GET",
            f"equipment-catalog/serial/{serial_number}",
            200
        )
        return success, response

    def test_download_certificate_pdf(self, serial_number):
        """Test downloading PDF certificate for calibrated equipment"""
        url = f"{self.base_url}/equipment/{serial_number}/certificate"
        test_headers = {}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'

        print(f"\n🔍 Testing PDF Certificate Download...")
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url, headers=test_headers, timeout=30)
            
            if response.status_code == 200:
                # Verify it's a PDF
                content_type = response.headers.get('content-type', '')
                if 'application/pdf' in content_type:
                    # Verify PDF content is not empty
                    if len(response.content) > 1000:  # PDF should be at least 1KB
                        self.log_test("PDF Certificate Download", True, f"PDF generated successfully, size: {len(response.content)} bytes")
                        return True, response.content
                    else:
                        self.log_test("PDF Certificate Download", False, "PDF file too small, likely corrupted")
                        return False, None
                else:
                    self.log_test("PDF Certificate Download", False, f"Wrong content type: {content_type}")
                    return False, None
            else:
                details = f"Expected 200, got {response.status_code}. Response: {response.text[:200]}"
                self.log_test("PDF Certificate Download", False, details)
                return False, None

        except Exception as e:
            self.log_test("PDF Certificate Download", False, f"Exception: {str(e)}")
            return False, None

def test_logo_fix_critical():
    """Test CRITICAL LOGO FIX - Verify PDF generation without logo overflow error"""
    print("🚀 TESTING CRÍTICO: Verificar fix de tamaño de logo en generación de PDF")
    print("=" * 70)
    print("CONTEXTO: Usuario reportó error al registrar salida de equipo")
    print("ERROR: Logo demasiado grande (510x1778 points) causando page overflow")
    print("FIX: Logo ajustado a 7.15cm x 1.93cm en pdf_generator.py línea 44")
    print("=" * 70)
    
    tester = WorkshopAPITester()
    
    # Test authentication flow
    print("\n📋 AUTHENTICATION")
    print("-" * 20)
    
    reg_success, username = tester.test_auth_register()
    if not reg_success:
        print("❌ Registration failed, stopping tests")
        return 1
    
    login_success = tester.test_auth_login(username)
    if not login_success:
        print("❌ Login failed, stopping tests")
        return 1
    
    # WORKFLOW COMPLETO END-TO-END como especifica el usuario
    print("\n📋 WORKFLOW COMPLETO END-TO-END")
    print("-" * 35)
    
    # 1. Crear un nuevo cliente con departamento
    print("🔧 1. Crear nuevo cliente con departamento")
    client_data = {
        "name": "Empresa Test Logo Fix",
        "cif": "B12345678",
        "departamento": "Seguridad Industrial"
    }
    client_success, _ = tester.run_test(
        "Crear Cliente con Departamento",
        "POST",
        "clients",
        200,
        data=client_data
    )
    
    if not client_success:
        print("❌ Failed to create client, stopping test")
        return 1
    
    # Crear brand y model necesarios
    print("🔧 Crear brand Honeywell")
    tester.run_test("Create Honeywell Brand", "POST", "brands", 200, data={"name": "Honeywell"})
    
    print("🔧 Crear model XT-1000")
    tester.run_test("Create XT-1000 Model", "POST", "models", 200, data={"name": "XT-1000"})
    
    print("🔧 Crear technician")
    tester.run_test("Create Technician", "POST", "technicians", 200, data={"name": "Carlos Rodríguez"})
    
    # 2. Crear un nuevo equipo asociado a ese cliente
    print("🔧 2. Crear nuevo equipo asociado al cliente")
    serial_number = f"SN-LOGO-FIX-{datetime.now().strftime('%H%M%S')}"
    equipment_data = {
        "brand": "Honeywell",
        "model": "XT-1000",
        "client_name": client_data["name"],
        "client_cif": client_data["cif"],
        "client_departamento": client_data["departamento"],
        "serial_number": serial_number,
        "observations": "Equipo para test crítico de logo fix",
        "entry_date": datetime.now().strftime('%Y-%m-%d')
    }
    
    equip_success, _ = tester.run_test(
        "Crear Equipo para Test Logo Fix",
        "POST",
        "equipment",
        200,
        data=equipment_data
    )
    
    if not equip_success:
        print("❌ Failed to create equipment, stopping test")
        return 1
    
    # 3. Calibrar el equipo con al menos 2 sensores (CO, H2S) incluyendo valores Zero/SPAN
    print("🔧 3. Calibrar equipo con 2 sensores (CO, H2S) + valores Zero/SPAN")
    calibration_data = {
        "calibration_data": [
            {
                "sensor": "CO (Monóxido de Carbono)",
                "pre_alarm": "25 ppm",
                "alarm": "50 ppm", 
                "calibration_value": "100 ppm",
                "valor_zero": "0 ppm",
                "valor_span": "100 ppm",
                "calibration_bottle": "BOT-CO-001",
                "approved": True
            },
            {
                "sensor": "H2S (Sulfuro de Hidrógeno)",
                "pre_alarm": "5 ppm",
                "alarm": "10 ppm",
                "calibration_value": "25 ppm", 
                "valor_zero": "0 ppm",
                "valor_span": "25 ppm",
                "calibration_bottle": "BOT-H2S-002",
                "approved": True
            }
        ],
        # 4. Agregar al menos 1 repuesto utilizado con garantía
        "spare_parts": [
            {
                "descripcion": "Filtro de entrada",
                "referencia": "FLT-001",
                "garantia": True
            }
        ],
        "calibration_date": datetime.now().strftime('%Y-%m-%d'),
        "technician": "Carlos Rodríguez"
    }
    
    calib_success, _ = tester.run_test(
        "Calibrar Equipo con CO/H2S + Repuesto con Garantía",
        "PUT",
        f"equipment/{serial_number}/calibrate",
        200,
        data=calibration_data
    )
    
    if not calib_success:
        print("❌ Failed to calibrate equipment, stopping test")
        return 1
    
    # 5. Registrar salida del equipo (delivery note + ubicación)
    print("🔧 5. Registrar salida del equipo (delivery note + ubicación)")
    delivery_data = {
        "serial_numbers": [serial_number],
        "delivery_note": f"DN-LOGO-FIX-{datetime.now().strftime('%H%M%S')}",
        "delivery_location": "Planta Industrial Cliente",
        "delivery_date": datetime.now().strftime('%Y-%m-%d')
    }
    
    delivery_success, _ = tester.run_test(
        "Registrar Salida de Equipo",
        "PUT",
        "equipment/deliver",
        200,
        data=delivery_data
    )
    
    if not delivery_success:
        print("❌ Failed to deliver equipment, stopping test")
        return 1
    
    # 6. Generar certificado PDF mediante GET /api/equipment/{serial}/certificate
    print("🔧 6. Generar certificado PDF - TEST CRÍTICO DEL LOGO FIX")
    print("   Verificando que NO ocurra error: 'Logo demasiado grande (510x1778 points)'")
    
    pdf_success, pdf_content = tester.test_download_certificate_pdf(serial_number)
    
    if not pdf_success:
        print("❌ CRITICAL FAILURE: PDF generation failed - Logo fix did not work!")
        return 1
    
    # 7. Verificaciones específicas del fix
    print("\n🔍 VERIFICACIONES ESPECÍFICAS DEL FIX")
    print("-" * 40)
    
    # Verificar que PDF se genera sin errores de overflow
    if pdf_content and len(pdf_content) > 1000:
        tester.log_test("PDF sin errores de overflow", True, f"PDF generado exitosamente, tamaño: {len(pdf_content)} bytes")
    else:
        tester.log_test("PDF sin errores de overflow", False, "PDF demasiado pequeño o corrupto")
        return 1
    
    # Verificar que archivo PDF es válido y tiene header correcto
    try:
        pdf_header = pdf_content[:8]
        if pdf_header.startswith(b'%PDF-'):
            tester.log_test("PDF válido con header correcto", True, f"Header: {pdf_header.decode('ascii', errors='ignore')}")
        else:
            tester.log_test("PDF válido con header correcto", False, f"Header inválido: {pdf_header}")
            return 1
    except Exception as e:
        tester.log_test("PDF válido con header correcto", False, f"Error verificando header: {e}")
        return 1
    
    # Verificar que tamaño del archivo es razonable (no excesivamente grande)
    pdf_size_kb = len(pdf_content) / 1024
    if 50 <= pdf_size_kb <= 2000:  # Entre 50KB y 2MB es razonable
        tester.log_test("Tamaño de archivo razonable", True, f"Tamaño: {pdf_size_kb:.1f} KB")
    else:
        tester.log_test("Tamaño de archivo razonable", False, f"Tamaño anormal: {pdf_size_kb:.1f} KB")
    
    # Guardar PDF para inspección manual
    try:
        with open("/app/test_logo_fix_certificate.pdf", "wb") as f:
            f.write(pdf_content)
        print(f"   📁 PDF guardado como /app/test_logo_fix_certificate.pdf para inspección")
    except Exception as e:
        print(f"   ⚠️ No se pudo guardar PDF: {e}")
    
    # Print final results
    print("\n" + "=" * 70)
    print(f"📊 LOGO FIX TEST RESULTS: {tester.tests_passed}/{tester.tests_run} tests passed")
    print("=" * 70)
    
    # Print detailed results for failed tests
    failed_tests = [test for test in tester.test_results if not test['success']]
    if failed_tests:
        print("\n❌ FAILED TESTS:")
        for test in failed_tests:
            print(f"   • {test['test']}: {test['details']}")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 LOGO FIX SUCCESSFUL! PDF se genera sin error de overflow")
        print("✅ El fix resuelve el problema reportado por el usuario")
        return 0
    else:
        print(f"⚠️ LOGO FIX FAILED: {tester.tests_run - tester.tests_passed} tests failed")
        print("❌ El fix NO resuelve completamente el problema")
        return 1

def test_fase2_pdf_generation():
    """Test FASE 2 - PDF Certificate Generation as specified in review request"""
    print("🚀 Starting FASE 2 - PDF Certificate Generation Tests")
    print("=" * 60)
    
    tester = WorkshopAPITester()
    
    # Test authentication flow
    print("\n📋 AUTHENTICATION TESTS")
    print("-" * 30)
    
    reg_success, username = tester.test_auth_register()
    if not reg_success:
        print("❌ Registration failed, stopping tests")
        return 1
    
    login_success = tester.test_auth_login(username)
    if not login_success:
        print("❌ Login failed, stopping tests")
        return 1
    
    tester.test_auth_me()
    
    # FASE 2: Create test data as specified in review request
    print("\n📋 FASE 2 - CREATING TEST DATA FOR PDF GENERATION")
    print("-" * 50)
    
    # 1. Create brand Honeywell
    print("🔧 Creating brand: Honeywell")
    brand_success, _ = tester.run_test(
        "Create Honeywell Brand",
        "POST",
        "brands",
        200,
        data={"name": "Honeywell"}
    )
    
    # 2. Create model XT-2000
    print("🔧 Creating model: XT-2000")
    model_success, _ = tester.run_test(
        "Create XT-2000 Model",
        "POST",
        "models",
        200,
        data={"name": "XT-2000"}
    )
    
    # 3. Create client with departamento
    print("🔧 Creating client: Empresa Prueba PDF")
    client_data = {
        "name": "Empresa Prueba PDF",
        "cif": "B87654321",
        "departamento": "Seguridad Industrial"
    }
    client_success, _ = tester.run_test(
        "Create Client with Departamento",
        "POST",
        "clients",
        200,
        data=client_data
    )
    
    # 4. Create technician
    print("🔧 Creating technician: Carlos Rodríguez")
    tech_success, _ = tester.run_test(
        "Create Technician Carlos Rodriguez",
        "POST",
        "technicians",
        200,
        data={"name": "Carlos Rodríguez"}
    )
    
    # 5. Create equipment
    print("🔧 Creating equipment: SN-PDF-TEST-001")
    equipment_data = {
        "brand": "Honeywell",
        "model": "XT-2000",
        "client_name": "Empresa Prueba PDF",
        "client_cif": "B87654321",
        "client_departamento": "Seguridad Industrial",
        "serial_number": "SN-PDF-TEST-001",
        "observations": "Equipo para prueba de certificado PDF",
        "entry_date": "2025-01-20"
    }
    equip_success, _ = tester.run_test(
        "Create Equipment for PDF Test",
        "POST",
        "equipment",
        200,
        data=equipment_data
    )
    
    if not all([brand_success, model_success, client_success, tech_success, equip_success]):
        print("❌ Failed to create required test data, stopping PDF tests")
        return 1
    
    # 6. Calibrate equipment with multiple sensors
    print("🔧 Calibrating equipment with multiple sensors")
    calibration_data = {
        "calibration_data": [
            {
                "sensor": "CO (Monóxido de Carbono)",
                "pre_alarm": "25 ppm",
                "alarm": "50 ppm",
                "calibration_value": "100 ppm",
                "valor_zero": "0 ppm",
                "valor_span": "100 ppm",
                "calibration_bottle": "BOT-CO-001",
                "approved": True
            },
            {
                "sensor": "H2S (Sulfuro de Hidrógeno)",
                "pre_alarm": "5 ppm",
                "alarm": "10 ppm",
                "calibration_value": "25 ppm",
                "valor_zero": "0 ppm",
                "valor_span": "25 ppm",
                "calibration_bottle": "BOT-H2S-002",
                "approved": True
            },
            {
                "sensor": "O2 (Oxígeno)",
                "pre_alarm": "19.5%",
                "alarm": "23.5%",
                "calibration_value": "20.9%",
                "valor_zero": "0%",
                "valor_span": "20.9%",
                "calibration_bottle": "BOT-O2-003",
                "approved": True
            }
        ],
        "spare_parts": "Filtro de entrada reemplazado, Sensor de CO calibrado, Batería verificada",
        "calibration_date": "2025-01-20",
        "technician": "Carlos Rodríguez"
    }
    
    calib_success, calib_response = tester.run_test(
        "Calibrate Equipment with Multiple Sensors",
        "PUT",
        "equipment/SN-PDF-TEST-001/calibrate",
        200,
        data=calibration_data
    )
    
    if not calib_success:
        print("❌ Failed to calibrate equipment, stopping PDF tests")
        return 1
    
    print("✅ Equipment calibrated successfully")
    
    # 7. Test PDF certificate generation and download
    print("\n📋 FASE 2 - PDF CERTIFICATE GENERATION TEST")
    print("-" * 45)
    
    pdf_success, pdf_content = tester.test_download_certificate_pdf("SN-PDF-TEST-001")
    
    if pdf_success:
        print("✅ PDF certificate generated and downloaded successfully")
        print(f"   📄 PDF size: {len(pdf_content)} bytes")
        
        # Save PDF for manual inspection if needed
        try:
            with open("/app/test_certificate.pdf", "wb") as f:
                f.write(pdf_content)
            print("   📁 PDF saved as /app/test_certificate.pdf for inspection")
        except Exception as e:
            print(f"   ⚠️ Could not save PDF file: {e}")
    else:
        print("❌ PDF certificate generation failed")
    
    # 8. Verify equipment status is still calibrated
    print("\n🔍 Verifying equipment status after PDF generation")
    status_success, equipment_status = tester.run_test(
        "Verify Equipment Status After PDF",
        "GET",
        "equipment/serial/SN-PDF-TEST-001",
        200
    )
    
    if status_success and equipment_status:
        if equipment_status.get('status') == 'calibrated':
            tester.log_test("Equipment Status Verification", True, "Equipment remains calibrated after PDF generation")
        else:
            tester.log_test("Equipment Status Verification", False, f"Equipment status is {equipment_status.get('status')}, expected 'calibrated'")
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 FASE 2 PDF RESULTS: {tester.tests_passed}/{tester.tests_run} tests passed")
    print("=" * 60)
    
    # Print detailed results for failed tests
    failed_tests = [test for test in tester.test_results if not test['success']]
    if failed_tests:
        print("\n❌ FAILED TESTS:")
        for test in failed_tests:
            print(f"   • {test['test']}: {test['details']}")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All FASE 2 PDF tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

def main():
    print("🚀 Starting FASE 1 - Workshop Management API Tests")
    print("=" * 60)
    
    tester = WorkshopAPITester()
    
    # Test authentication flow
    print("\n📋 AUTHENTICATION TESTS")
    print("-" * 30)
    
    reg_success, username = tester.test_auth_register()
    if not reg_success:
        print("❌ Registration failed, stopping tests")
        return 1
    
    login_success = tester.test_auth_login(username)
    if not login_success:
        print("❌ Login failed, stopping tests")
        return 1
    
    tester.test_auth_me()
    
    # Test master data
    print("\n📋 MASTER DATA TESTS")
    print("-" * 30)
    
    brand_success, brand_name = tester.test_create_brand()
    tester.test_get_brands()
    
    model_success, model_name = tester.test_create_model()
    tester.test_get_models()
    
    # FASE 1: Test client with departamento field
    client_success, client_data = tester.test_create_client()
    tester.test_get_clients()
    
    tech_success, tech_name = tester.test_create_technician()
    tester.test_get_technicians()
    
    # FASE 1: Test equipment workflow with new features
    print("\n📋 FASE 1 - EQUIPMENT WORKFLOW TESTS")
    print("-" * 40)
    
    if brand_success and model_success and client_success:
        # Test equipment creation (should save to catalog)
        equip_success, serial_number = tester.test_create_equipment(brand_name, model_name, client_data)
        
        if equip_success:
            # Test getting equipment from catalog by serial
            catalog_success, catalog_data = tester.test_get_equipment_catalog_by_serial(serial_number)
            
            # Verify catalog data contains expected fields
            if catalog_success and catalog_data:
                print(f"   📋 Catalog data: {json.dumps(catalog_data, indent=2)}")
                required_fields = ['serial_number', 'brand', 'model', 'client_name', 'client_cif', 'client_departamento']
                missing_fields = [field for field in required_fields if field not in catalog_data]
                if missing_fields:
                    tester.log_test("Catalog Data Validation", False, f"Missing fields: {missing_fields}")
                else:
                    tester.log_test("Catalog Data Validation", True, "All required fields present")
            
            # Test getting equipment by serial
            get_success, equipment_data = tester.test_get_equipment_by_serial(serial_number)
            
            if get_success and tech_success:
                # FASE 1: Test calibration with valor_zero and valor_span
                calib_success, calib_response = tester.test_calibrate_equipment(serial_number, tech_name)
                
                if calib_success:
                    # Verify calibration data contains new fields
                    if calib_response and 'calibration_data' in calib_response:
                        calibration_data = calib_response['calibration_data'][0]
                        if 'valor_zero' in calibration_data and 'valor_span' in calibration_data:
                            tester.log_test("Calibration Data Validation", True, "valor_zero and valor_span fields present")
                            print(f"   📋 Calibration data: valor_zero={calibration_data['valor_zero']}, valor_span={calibration_data['valor_span']}")
                        else:
                            tester.log_test("Calibration Data Validation", False, "valor_zero or valor_span fields missing")
                    
                    cal_list_success, calibrated_list = tester.test_get_calibrated_equipment()
                    
                    if cal_list_success:
                        deliver_success = tester.test_deliver_equipment([serial_number])
                        
                        if deliver_success:
                            tester.test_get_delivered_equipment()
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 FASE 1 RESULTS: {tester.tests_passed}/{tester.tests_run} tests passed")
    print("=" * 60)
    
    # Print detailed results for failed tests
    failed_tests = [test for test in tester.test_results if not test['success']]
    if failed_tests:
        print("\n❌ FAILED TESTS:")
        for test in failed_tests:
            print(f"   • {test['test']}: {test['details']}")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All FASE 1 tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    # Check if we should run specific tests
    if len(sys.argv) > 1:
        if sys.argv[1] == "fase2":
            sys.exit(test_fase2_pdf_generation())
        elif sys.argv[1] == "logo_fix":
            sys.exit(test_logo_fix_critical())
    else:
        sys.exit(main())