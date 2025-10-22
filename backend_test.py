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

            # Handle both single status code and list of acceptable status codes
            if isinstance(expected_status, list):
                success = response.status_code in expected_status
            else:
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

def test_equipment_filtering_bug():
    """
    DEBUGGING: Verificar filtrado de equipos pendientes después de calibración
    
    PROBLEMA REPORTADO:
    - Después de calibrar un equipo, este aparece en la pestaña "Salida" ✅
    - PERO el equipo sigue apareciendo en la pestaña "Revisión" ❌
    - Debería desaparecer de "Revisión" después de calibrarse
    
    TESTS A REALIZAR:
    1. Crear un equipo nuevo con status "pending"
    2. Verificar que aparece en GET /api/equipment/pending
    3. Calibrar el equipo (PUT /api/equipment/{serial}/calibrate)
    4. Verificar inmediatamente después que:
       - El equipo tiene status "calibrated" en la base de datos
       - El equipo NO aparece en GET /api/equipment/pending
       - El equipo SÍ aparece en GET /api/equipment/calibrated
    """
    print("🔍 DEBUGGING: Verificar filtrado de equipos pendientes después de calibración")
    print("=" * 80)
    print("PROBLEMA REPORTADO:")
    print("- Después de calibrar un equipo, este aparece en la pestaña 'Salida' ✅")
    print("- PERO el equipo sigue apareciendo en la pestaña 'Revisión' ❌")
    print("- Debería desaparecer de 'Revisión' después de calibrarse")
    print("=" * 80)
    
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
    
    # Setup test data
    print("\n📋 SETUP TEST DATA")
    print("-" * 20)
    
    # Create required master data (ignore if already exists)
    tester.run_test("Create Brand", "POST", "brands", [200, 400], data={"name": "Honeywell"})
    tester.run_test("Create Model", "POST", "models", [200, 400], data={"name": "XT-1000"})
    tester.run_test("Create Technician", "POST", "technicians", [200, 400], data={"name": "Juan Pérez"})
    
    client_data = {
        "name": f"Empresa Test Filtrado {datetime.now().strftime('%H%M%S')}",
        "cif": f"B{datetime.now().strftime('%H%M%S')}",
        "departamento": "Mantenimiento"
    }
    tester.run_test("Create Client", "POST", "clients", 200, data=client_data)
    
    # STEP 1: Crear un equipo nuevo con status "pending"
    print("\n🔧 STEP 1: Crear equipo nuevo con status 'pending'")
    serial_number = f"SN-FILTER-TEST-{datetime.now().strftime('%H%M%S')}"
    equipment_data = {
        "brand": "Honeywell",
        "model": "XT-1000",
        "client_name": client_data["name"],
        "client_cif": client_data["cif"],
        "client_departamento": client_data["departamento"],
        "serial_number": serial_number,
        "observations": "Equipo para test de filtrado después de calibración",
        "entry_date": datetime.now().strftime('%Y-%m-%d')
    }
    
    create_success, _ = tester.run_test(
        "Crear Equipo con Status Pending",
        "POST",
        "equipment",
        200,
        data=equipment_data
    )
    
    if not create_success:
        print("❌ Failed to create equipment, stopping test")
        return 1
    
    # STEP 2: Verificar que aparece en GET /api/equipment/pending
    print("\n🔧 STEP 2: Verificar que aparece en GET /api/equipment/pending")
    pending_success, pending_response = tester.run_test(
        "Get Pending Equipment (Before Calibration)",
        "GET",
        "equipment/pending",
        200
    )
    
    if pending_success:
        # Check if our equipment is in the pending list
        equipment_found_in_pending = False
        if isinstance(pending_response, list):
            for equipment in pending_response:
                if equipment.get('serial_number') == serial_number:
                    equipment_found_in_pending = True
                    break
        
        if equipment_found_in_pending:
            tester.log_test("Equipment Found in Pending List", True, f"Equipment {serial_number} correctly appears in pending list")
        else:
            tester.log_test("Equipment Found in Pending List", False, f"Equipment {serial_number} NOT found in pending list")
            print("❌ Equipment not found in pending list, stopping test")
            return 1
    else:
        print("❌ Failed to get pending equipment, stopping test")
        return 1
    
    # STEP 3: Calibrar el equipo (PUT /api/equipment/{serial}/calibrate)
    print("\n🔧 STEP 3: Calibrar el equipo")
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
            }
        ],
        "spare_parts": [
            {
                "descripcion": "Filtro de entrada",
                "referencia": "FLT-001",
                "garantia": True
            }
        ],
        "calibration_date": datetime.now().strftime('%Y-%m-%d'),
        "technician": "Juan Pérez"
    }
    
    calibrate_success, calibrate_response = tester.run_test(
        "Calibrar Equipo",
        "PUT",
        f"equipment/{serial_number}/calibrate",
        200,
        data=calibration_data
    )
    
    if not calibrate_success:
        print("❌ Failed to calibrate equipment, stopping test")
        return 1
    
    # STEP 4: Verificaciones inmediatas después de calibración
    print("\n🔧 STEP 4: Verificaciones después de calibración")
    print("-" * 50)
    
    # 4a: Verificar que el equipo tiene status "calibrated" en la base de datos
    print("🔍 4a: Verificar status 'calibrated' en base de datos")
    status_success, status_response = tester.run_test(
        "Get Equipment Status After Calibration",
        "GET",
        f"equipment/serial/{serial_number}",
        200
    )
    
    if status_success and status_response:
        equipment_status = status_response.get('status')
        if equipment_status == 'calibrated':
            tester.log_test("Equipment Status is Calibrated", True, f"Status correctly changed to 'calibrated'")
        else:
            tester.log_test("Equipment Status is Calibrated", False, f"Status is '{equipment_status}', expected 'calibrated'")
    else:
        tester.log_test("Equipment Status is Calibrated", False, "Could not retrieve equipment status")
    
    # 4b: Verificar que el equipo NO aparece en GET /api/equipment/pending
    print("🔍 4b: Verificar que NO aparece en GET /api/equipment/pending")
    pending_after_success, pending_after_response = tester.run_test(
        "Get Pending Equipment (After Calibration)",
        "GET",
        "equipment/pending",
        200
    )
    
    if pending_after_success:
        # Check if our equipment is still in the pending list (it should NOT be)
        equipment_still_in_pending = False
        if isinstance(pending_after_response, list):
            for equipment in pending_after_response:
                if equipment.get('serial_number') == serial_number:
                    equipment_still_in_pending = True
                    break
        
        if not equipment_still_in_pending:
            tester.log_test("Equipment NOT in Pending List After Calibration", True, f"Equipment {serial_number} correctly removed from pending list")
        else:
            tester.log_test("Equipment NOT in Pending List After Calibration", False, f"🚨 BUG CONFIRMED: Equipment {serial_number} still appears in pending list after calibration!")
    else:
        tester.log_test("Equipment NOT in Pending List After Calibration", False, "Could not retrieve pending equipment list")
    
    # 4c: Verificar que el equipo SÍ aparece en GET /api/equipment/calibrated
    print("🔍 4c: Verificar que SÍ aparece en GET /api/equipment/calibrated")
    calibrated_success, calibrated_response = tester.run_test(
        "Get Calibrated Equipment",
        "GET",
        "equipment/calibrated",
        200
    )
    
    if calibrated_success:
        # Check if our equipment is in the calibrated list
        equipment_found_in_calibrated = False
        if isinstance(calibrated_response, list):
            for equipment in calibrated_response:
                if equipment.get('serial_number') == serial_number:
                    equipment_found_in_calibrated = True
                    break
        
        if equipment_found_in_calibrated:
            tester.log_test("Equipment Found in Calibrated List", True, f"Equipment {serial_number} correctly appears in calibrated list")
        else:
            tester.log_test("Equipment Found in Calibrated List", False, f"Equipment {serial_number} NOT found in calibrated list")
    else:
        tester.log_test("Equipment Found in Calibrated List", False, "Could not retrieve calibrated equipment list")
    
    # Print detailed analysis
    print("\n" + "=" * 80)
    print("📊 ANÁLISIS DETALLADO DEL FILTRADO")
    print("=" * 80)
    
    # Count equipment in each list for debugging
    if pending_after_success and isinstance(pending_after_response, list):
        print(f"📋 Equipos en lista PENDING después de calibración: {len(pending_after_response)}")
        for eq in pending_after_response:
            status_indicator = "🚨" if eq.get('serial_number') == serial_number else "✅"
            print(f"   {status_indicator} {eq.get('serial_number', 'N/A')} - Status: {eq.get('status', 'N/A')}")
    
    if calibrated_success and isinstance(calibrated_response, list):
        print(f"📋 Equipos en lista CALIBRATED: {len(calibrated_response)}")
        for eq in calibrated_response:
            status_indicator = "✅" if eq.get('serial_number') == serial_number else "ℹ️"
            print(f"   {status_indicator} {eq.get('serial_number', 'N/A')} - Status: {eq.get('status', 'N/A')}")
    
    # Print final results
    print("\n" + "=" * 80)
    print(f"📊 FILTRADO TEST RESULTS: {tester.tests_passed}/{tester.tests_run} tests passed")
    print("=" * 80)
    
    # Print detailed results for failed tests
    failed_tests = [test for test in tester.test_results if not test['success']]
    if failed_tests:
        print("\n❌ FAILED TESTS:")
        for test in failed_tests:
            print(f"   • {test['test']}: {test['details']}")
    
    # Specific analysis for the reported bug
    bug_confirmed = False
    for test in tester.test_results:
        if test['test'] == "Equipment NOT in Pending List After Calibration" and not test['success']:
            if "still appears in pending list" in test['details']:
                bug_confirmed = True
                break
    
    if bug_confirmed:
        print("\n🚨 BUG CONFIRMADO:")
        print("   El equipo sigue apareciendo en la lista de pendientes después de calibrarse")
        print("   Esto explica por qué aparece en ambas pestañas (Revisión y Salida)")
        print("\n🔧 POSIBLES CAUSAS:")
        print("   1. El filtro en GET /api/equipment/pending no está funcionando correctamente")
        print("   2. El status del equipo no se está actualizando correctamente en la base de datos")
        print("   3. Hay un problema de caché o sincronización en la base de datos")
        return 1
    elif tester.tests_passed == tester.tests_run:
        print("\n✅ NO SE DETECTÓ EL BUG:")
        print("   El filtrado funciona correctamente en el backend")
        print("   El problema podría estar en el frontend o en la sincronización")
        return 0
    else:
        print(f"\n⚠️ TESTS INCOMPLETOS: {tester.tests_run - tester.tests_passed} tests failed")
        print("   No se pudo completar la verificación del bug")
        return 1

def test_calibration_history_flow():
    """
    TESTING: Verificar flujo completo de calibración y aparición en Historial y Resumen
    
    PROBLEMA REPORTADO:
    - Usuario calibra un equipo en Revisión ✓
    - Certificado se genera correctamente ✓
    - Equipo NO aparece en Historial ✗
    - Equipo NO aparece en Resumen ✗
    
    TESTS A REALIZAR:
    1. Crear y calibrar equipo de prueba con serial "TEST-HISTORY-001"
    2. Verificar aparición en Historial (/api/calibration-history/search)
    3. Hacer salida del equipo (delivery)
    4. Verificar aparición en Resumen (/api/equipment/delivered)
    5. Diagnóstico de qué falla exactamente
    """
    print("🔍 TESTING: Verificar flujo completo de calibración y aparición en Historial y Resumen")
    print("=" * 90)
    print("PROBLEMA REPORTADO:")
    print("- Usuario calibra un equipo en Revisión ✓")
    print("- Certificado se genera correctamente ✓")
    print("- Equipo NO aparece en Historial ✗")
    print("- Equipo NO aparece en Resumen ✗")
    print("=" * 90)
    
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
    
    # Setup test data
    print("\n📋 SETUP TEST DATA")
    print("-" * 20)
    
    # Create required master data (ignore if already exists)
    tester.run_test("Create Brand", "POST", "brands", [200, 400], data={"name": "Honeywell"})
    tester.run_test("Create Model", "POST", "models", [200, 400], data={"name": "XT-1000"})
    tester.run_test("Create Technician", "POST", "technicians", [200, 400], data={"name": "Carlos Rodríguez"})
    
    client_data = {
        "name": f"Empresa Test Historial {datetime.now().strftime('%H%M%S')}",
        "cif": f"C{datetime.now().strftime('%H%M%S')}",
        "departamento": "Seguridad Industrial"
    }
    tester.run_test("Create Client", "POST", "clients", 200, data=client_data)
    
    # STEP 1: Crear y calibrar equipo de prueba con serial "TEST-HISTORY-001"
    print("\n🔧 STEP 1: Crear equipo de prueba con serial 'TEST-HISTORY-001'")
    serial_number = "TEST-HISTORY-001"
    equipment_data = {
        "brand": "Honeywell",
        "model": "XT-1000",
        "client_name": client_data["name"],
        "client_cif": client_data["cif"],
        "client_departamento": client_data["departamento"],
        "serial_number": serial_number,
        "observations": "Equipo para test de historial y resumen",
        "entry_date": datetime.now().strftime('%Y-%m-%d')
    }
    
    create_success, _ = tester.run_test(
        "Crear Equipo TEST-HISTORY-001",
        "POST",
        "equipment",
        200,
        data=equipment_data
    )
    
    if not create_success:
        print("❌ Failed to create equipment, stopping test")
        return 1
    
    # Calibrar el equipo con 2 sensores y notas internas
    print("\n🔧 STEP 1b: Calibrar equipo con 2 sensores y notas internas")
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
        "spare_parts": [
            {
                "descripcion": "Filtro de entrada",
                "referencia": "FLT-001",
                "garantia": True
            }
        ],
        "calibration_date": datetime.now().strftime('%Y-%m-%d'),
        "technician": "Carlos Rodríguez",
        "internal_notes": "Calibración realizada sin problemas. Sensores funcionando correctamente."
    }
    
    calibrate_success, calibrate_response = tester.run_test(
        "Calibrar Equipo TEST-HISTORY-001",
        "PUT",
        f"equipment/{serial_number}/calibrate",
        200,
        data=calibration_data
    )
    
    if not calibrate_success:
        print("❌ Failed to calibrate equipment, stopping test")
        return 1
    
    # Verificar que status cambia a "calibrated"
    print("\n🔍 Verificar que status cambia a 'calibrated'")
    status_success, status_response = tester.run_test(
        "Verificar Status Calibrated",
        "GET",
        f"equipment/serial/{serial_number}",
        200
    )
    
    if status_success and status_response:
        equipment_status = status_response.get('status')
        if equipment_status == 'calibrated':
            tester.log_test("Equipment Status Changed to Calibrated", True, f"Status correctly changed to 'calibrated'")
        else:
            tester.log_test("Equipment Status Changed to Calibrated", False, f"Status is '{equipment_status}', expected 'calibrated'")
    
    # STEP 2: Verificar aparición en Historial
    print("\n🔧 STEP 2: Verificar aparición en Historial")
    print("-" * 40)
    
    # Buscar en /api/calibration-history/search?serial=TEST-HISTORY-001
    print("🔍 2a: Buscar en /api/calibration-history/search?serial=TEST-HISTORY-001")
    history_search_success, history_search_response = tester.run_test(
        "Buscar en Historial por Serial",
        "GET",
        f"calibration-history/search?serial={serial_number}",
        200
    )
    
    calibration_found_in_history = False
    has_internal_notes = False
    
    if history_search_success and isinstance(history_search_response, list):
        print(f"   📋 Equipos encontrados en historial: {len(history_search_response)}")
        
        for equipment_group in history_search_response:
            if equipment_group.get('serial_number') == serial_number:
                calibration_found_in_history = True
                print(f"   ✅ Equipo {serial_number} encontrado en historial")
                print(f"   📋 Calibraciones: {len(equipment_group.get('calibrations', []))}")
                
                # Verificar que tiene internal_notes
                calibrations = equipment_group.get('calibrations', [])
                if calibrations:
                    # Check if we can find internal_notes in the calibration history
                    # Note: internal_notes might not be in the search response, need to check individual history
                    print(f"   📋 Primera calibración: {calibrations[0].get('calibration_date')}")
                break
        
        if calibration_found_in_history:
            tester.log_test("Equipment Found in Calibration History Search", True, f"Equipment {serial_number} found in history search")
        else:
            tester.log_test("Equipment Found in Calibration History Search", False, f"🚨 BUG: Equipment {serial_number} NOT found in history search")
    else:
        tester.log_test("Equipment Found in Calibration History Search", False, "Could not retrieve calibration history search results")
    
    # Verificar historial completo del equipo específico
    print("🔍 2b: Verificar historial completo del equipo")
    equipment_history_success, equipment_history_response = tester.run_test(
        "Get Equipment History",
        "GET",
        f"equipment/{serial_number}/history",
        200
    )
    
    if equipment_history_success and isinstance(equipment_history_response, list):
        print(f"   📋 Entradas en historial del equipo: {len(equipment_history_response)}")
        
        if len(equipment_history_response) > 0:
            latest_calibration = equipment_history_response[0]
            has_internal_notes = bool(latest_calibration.get('internal_notes'))
            
            if has_internal_notes:
                tester.log_test("Equipment History Has Internal Notes", True, f"Internal notes found: '{latest_calibration.get('internal_notes')}'")
            else:
                tester.log_test("Equipment History Has Internal Notes", False, "Internal notes missing in calibration history")
            
            tester.log_test("Equipment Individual History Found", True, f"Equipment history contains {len(equipment_history_response)} calibrations")
        else:
            tester.log_test("Equipment Individual History Found", False, f"🚨 BUG: No calibration history found for equipment {serial_number}")
    else:
        tester.log_test("Equipment Individual History Found", False, "Could not retrieve equipment individual history")
    
    # STEP 3: Hacer salida del equipo (delivery)
    print("\n🔧 STEP 3: Registrar salida del equipo")
    print("-" * 35)
    
    delivery_data = {
        "serial_numbers": [serial_number],
        "delivery_note": f"DN-HISTORY-TEST-{datetime.now().strftime('%H%M%S')}",
        "delivery_location": "Planta Industrial Cliente",
        "delivery_date": datetime.now().strftime('%Y-%m-%d')
    }
    
    delivery_success, _ = tester.run_test(
        "Registrar Salida del Equipo",
        "PUT",
        "equipment/deliver",
        200,
        data=delivery_data
    )
    
    if not delivery_success:
        print("❌ Failed to deliver equipment, stopping test")
        return 1
    
    # Verificar que status cambia a "delivered"
    print("🔍 Verificar que status cambia a 'delivered'")
    delivered_status_success, delivered_status_response = tester.run_test(
        "Verificar Status Delivered",
        "GET",
        f"equipment/serial/{serial_number}",
        [200, 404]  # 404 is acceptable since delivered equipment might not be in active equipment endpoint
    )
    
    # STEP 4: Verificar aparición en Resumen
    print("\n🔧 STEP 4: Verificar aparición en Resumen")
    print("-" * 35)
    
    # GET /api/equipment/delivered
    print("🔍 4a: Verificar en GET /api/equipment/delivered")
    delivered_list_success, delivered_list_response = tester.run_test(
        "Get Delivered Equipment List",
        "GET",
        "equipment/delivered",
        200
    )
    
    equipment_found_in_delivered = False
    
    if delivered_list_success and isinstance(delivered_list_response, list):
        print(f"   📋 Equipos entregados: {len(delivered_list_response)}")
        
        for equipment in delivered_list_response:
            if equipment.get('serial_number') == serial_number:
                equipment_found_in_delivered = True
                equipment_status = equipment.get('status')
                print(f"   ✅ Equipo {serial_number} encontrado en lista de entregados")
                print(f"   📋 Status: {equipment_status}")
                print(f"   📋 Delivery note: {equipment.get('delivery_note')}")
                print(f"   📋 Delivery date: {equipment.get('delivery_date')}")
                break
        
        if equipment_found_in_delivered:
            tester.log_test("Equipment Found in Delivered List", True, f"Equipment {serial_number} found in delivered equipment list with status 'delivered'")
        else:
            tester.log_test("Equipment Found in Delivered List", False, f"🚨 BUG: Equipment {serial_number} NOT found in delivered equipment list")
    else:
        tester.log_test("Equipment Found in Delivered List", False, "Could not retrieve delivered equipment list")
    
    # STEP 5: Diagnóstico detallado
    print("\n🔧 STEP 5: Diagnóstico detallado")
    print("-" * 30)
    
    print("\n📊 ANÁLISIS DE RESULTADOS:")
    print("=" * 50)
    
    # Análisis del problema en Historial
    if not calibration_found_in_history:
        print("🚨 PROBLEMA EN HISTORIAL:")
        print("   - La calibración NO se guarda en calibration_history")
        print("   - O el endpoint de búsqueda /api/calibration-history/search no funciona")
        print("   - Verificar que el endpoint PUT /equipment/{serial}/calibrate guarde en calibration_history")
    else:
        print("✅ HISTORIAL FUNCIONA:")
        print("   - La calibración se guarda correctamente en calibration_history")
        print("   - El endpoint de búsqueda funciona correctamente")
    
    # Análisis del problema en Resumen
    if not equipment_found_in_delivered:
        print("\n🚨 PROBLEMA EN RESUMEN:")
        print("   - El equipo NO aparece en la lista de equipos entregados")
        print("   - O el status no cambia correctamente a 'delivered'")
        print("   - Verificar que el endpoint PUT /equipment/deliver actualice el status")
    else:
        print("\n✅ RESUMEN FUNCIONA:")
        print("   - El equipo aparece correctamente en la lista de equipos entregados")
        print("   - El status se actualiza correctamente a 'delivered'")
    
    # Print final results
    print("\n" + "=" * 90)
    print(f"📊 CALIBRATION HISTORY FLOW RESULTS: {tester.tests_passed}/{tester.tests_run} tests passed")
    print("=" * 90)
    
    # Print detailed results for failed tests
    failed_tests = [test for test in tester.test_results if not test['success']]
    if failed_tests:
        print("\n❌ FAILED TESTS:")
        for test in failed_tests:
            print(f"   • {test['test']}: {test['details']}")
    
    # Specific diagnosis
    history_bug = not calibration_found_in_history
    summary_bug = not equipment_found_in_delivered
    
    if history_bug or summary_bug:
        print("\n🔧 RECOMENDACIONES PARA MAIN AGENT:")
        if history_bug:
            print("   1. Verificar que PUT /equipment/{serial}/calibrate guarde en calibration_history")
            print("   2. Verificar que el modelo CalibrationHistory se esté usando correctamente")
            print("   3. Verificar que el endpoint /api/calibration-history/search funcione")
        
        if summary_bug:
            print("   4. Verificar que PUT /equipment/deliver actualice el status a 'delivered'")
            print("   5. Verificar que GET /api/equipment/delivered filtre por status 'delivered'")
        
        return 1
    elif tester.tests_passed == tester.tests_run:
        print("\n✅ FLUJO COMPLETO FUNCIONA CORRECTAMENTE:")
        print("   - Calibración se guarda en historial ✓")
        print("   - Equipo aparece en resumen después de entrega ✓")
        print("   - No se detectaron bugs en el backend")
        return 0
    else:
        print(f"\n⚠️ TESTS INCOMPLETOS: {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    # Check if we should run specific tests
    if len(sys.argv) > 1:
        if sys.argv[1] == "fase2":
            sys.exit(test_fase2_pdf_generation())
        elif sys.argv[1] == "logo_fix":
            sys.exit(test_logo_fix_critical())
        elif sys.argv[1] == "filter_bug":
            sys.exit(test_equipment_filtering_bug())
        elif sys.argv[1] == "history_flow":
            sys.exit(test_calibration_history_flow())
    else:
        sys.exit(main())