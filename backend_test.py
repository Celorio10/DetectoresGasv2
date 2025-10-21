import requests
import sys
import json
from datetime import datetime

class WorkshopAPITester:
    def __init__(self, base_url="https://service-monitor-8.preview.emergentagent.com/api"):
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

def main():
    print("🚀 Starting Workshop Management API Tests")
    print("=" * 50)
    
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
    
    client_success, client_data = tester.test_create_client()
    tester.test_get_clients()
    
    tech_success, tech_name = tester.test_create_technician()
    tester.test_get_technicians()
    
    # Test equipment workflow
    print("\n📋 EQUIPMENT WORKFLOW TESTS")
    print("-" * 30)
    
    if brand_success and model_success and client_success:
        equip_success, serial_number = tester.test_create_equipment(brand_name, model_name, client_data)
        
        if equip_success:
            get_success, equipment_data = tester.test_get_equipment_by_serial(serial_number)
            
            if get_success and tech_success:
                calib_success = tester.test_calibrate_equipment(serial_number, tech_name)
                
                if calib_success:
                    cal_list_success, calibrated_list = tester.test_get_calibrated_equipment()
                    
                    if cal_list_success:
                        deliver_success = tester.test_deliver_equipment([serial_number])
                        
                        if deliver_success:
                            tester.test_get_delivered_equipment()
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 FINAL RESULTS: {tester.tests_passed}/{tester.tests_run} tests passed")
    print("=" * 50)
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())