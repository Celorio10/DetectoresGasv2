#!/usr/bin/env python3
"""
FASE 1 Specific Test Cases
Tests the exact scenarios mentioned in the review request
"""

import requests
import json
from datetime import datetime

class Fase1SpecificTester:
    def __init__(self, base_url="https://service-monitor-8.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.test_results = []

    def authenticate(self):
        """Authenticate and get token"""
        # Register user
        username = f"fase1_user_{datetime.now().strftime('%H%M%S')}"
        reg_data = {
            "username": username,
            "password": "TestPass123!",
            "full_name": "FASE 1 Test User"
        }
        
        response = requests.post(f"{self.base_url}/auth/register", json=reg_data)
        if response.status_code != 200:
            print(f"❌ Registration failed: {response.text}")
            return False
        
        # Login
        login_data = {"username": username, "password": "TestPass123!"}
        response = requests.post(f"{self.base_url}/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.text}")
            return False
        
        self.token = response.json()["access_token"]
        print("✅ Authentication successful")
        return True

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }

    def test_scenario_1_create_client_with_departamento(self):
        """Test 1: Crear cliente con departamento"""
        print("\n🔍 Test 1: Crear cliente con departamento")
        
        client_data = {
            "name": "Cliente Test",
            "cif": "A12345678",
            "departamento": "Mantenimiento"
        }
        
        response = requests.post(
            f"{self.base_url}/clients",
            json=client_data,
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Cliente creado exitosamente")
            print(f"   Nombre: {result['name']}")
            print(f"   CIF: {result['cif']}")
            print(f"   Departamento: {result['departamento']}")
            return True, client_data
        else:
            print(f"❌ Error creando cliente: {response.text}")
            return False, None

    def test_scenario_2_create_equipment_saves_to_catalog(self):
        """Test 2: Crear equipo nuevo (debe guardarse en catálogo)"""
        print("\n🔍 Test 2: Crear equipo nuevo (debe guardarse en catálogo)")
        
        equipment_data = {
            "brand": "Honeywell",
            "model": "XT-1000",
            "client_name": "Cliente Test",
            "client_cif": "A12345678",
            "client_departamento": "Mantenimiento",
            "serial_number": "SN-TEST-001",
            "observations": "Equipo de prueba",
            "entry_date": "2025-01-20"
        }
        
        response = requests.post(
            f"{self.base_url}/equipment",
            json=equipment_data,
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Equipo creado exitosamente")
            print(f"   Serial: {result['serial_number']}")
            print(f"   Marca: {result['brand']}")
            print(f"   Modelo: {result['model']}")
            print(f"   Cliente: {result['client_name']}")
            print(f"   Departamento: {result['client_departamento']}")
            return True, equipment_data["serial_number"]
        else:
            print(f"❌ Error creando equipo: {response.text}")
            return False, None

    def test_scenario_3_get_equipment_from_catalog(self, serial_number):
        """Test 3: Obtener equipo del catálogo por serial"""
        print(f"\n🔍 Test 3: Obtener equipo del catálogo por serial: {serial_number}")
        
        response = requests.get(
            f"{self.base_url}/equipment-catalog/serial/{serial_number}",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Equipo encontrado en catálogo")
            print(f"   Serial: {result['serial_number']}")
            print(f"   Marca: {result['brand']}")
            print(f"   Modelo: {result['model']}")
            print(f"   Cliente: {result['client_name']}")
            print(f"   CIF: {result['client_cif']}")
            print(f"   Departamento: {result['client_departamento']}")
            
            # Verify required fields
            required_fields = ['serial_number', 'brand', 'model', 'client_name', 'client_cif', 'client_departamento']
            missing_fields = [field for field in required_fields if field not in result]
            
            if missing_fields:
                print(f"❌ Campos faltantes en catálogo: {missing_fields}")
                return False
            else:
                print("✅ Todos los campos requeridos están presentes")
                return True
        else:
            print(f"❌ Error obteniendo equipo del catálogo: {response.text}")
            return False

    def test_scenario_4_calibrate_with_new_fields(self, serial_number):
        """Test 4: Calibrar equipo con nuevos campos valor_zero y valor_span"""
        print(f"\n🔍 Test 4: Calibrar equipo con campos valor_zero y valor_span")
        
        calibration_data = {
            "calibration_data": [{
                "sensor": "CO",
                "pre_alarm": "25",
                "alarm": "50",
                "calibration_value": "100",
                "valor_zero": "0",
                "valor_span": "100",
                "calibration_bottle": "BOT-001",
                "approved": True
            }],
            "spare_parts": "Filtro reemplazado",
            "calibration_date": "2025-01-20",
            "technician": "Juan Pérez"
        }
        
        response = requests.put(
            f"{self.base_url}/equipment/{serial_number}/calibrate",
            json=calibration_data,
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Equipo calibrado exitosamente")
            print(f"   Estado: {result['status']}")
            print(f"   Técnico: {result['technician']}")
            
            # Verify calibration data contains new fields
            if result['calibration_data']:
                sensor_data = result['calibration_data'][0]
                if 'valor_zero' in sensor_data and 'valor_span' in sensor_data:
                    print(f"✅ Campos valor_zero y valor_span presentes")
                    print(f"   Valor Zero: {sensor_data['valor_zero']}")
                    print(f"   Valor Span: {sensor_data['valor_span']}")
                    return True
                else:
                    print(f"❌ Campos valor_zero o valor_span faltantes")
                    return False
            else:
                print(f"❌ No hay datos de calibración")
                return False
        else:
            print(f"❌ Error calibrando equipo: {response.text}")
            return False

    def test_scenario_5_verify_calibrated_equipment(self, serial_number):
        """Test 5: Verificar equipo calibrado"""
        print(f"\n🔍 Test 5: Verificar equipo calibrado con nuevos campos")
        
        response = requests.get(
            f"{self.base_url}/equipment/serial/{serial_number}",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Equipo verificado exitosamente")
            print(f"   Estado: {result['status']}")
            
            # Verify calibration data persisted correctly
            if result['calibration_data']:
                sensor_data = result['calibration_data'][0]
                if 'valor_zero' in sensor_data and 'valor_span' in sensor_data:
                    print(f"✅ Datos de calibración persistidos correctamente")
                    print(f"   Sensor: {sensor_data['sensor']}")
                    print(f"   Valor Zero: {sensor_data['valor_zero']}")
                    print(f"   Valor Span: {sensor_data['valor_span']}")
                    print(f"   Valor Calibración: {sensor_data['calibration_value']}")
                    return True
                else:
                    print(f"❌ Campos valor_zero o valor_span no persistieron")
                    return False
            else:
                print(f"❌ No hay datos de calibración persistidos")
                return False
        else:
            print(f"❌ Error verificando equipo: {response.text}")
            return False

    def run_all_tests(self):
        """Run all FASE 1 specific tests"""
        print("🚀 Iniciando pruebas específicas de FASE 1")
        print("=" * 60)
        
        if not self.authenticate():
            return False
        
        # Test 1: Create client with departamento
        client_success, client_data = self.test_scenario_1_create_client_with_departamento()
        if not client_success:
            return False
        
        # Test 2: Create equipment (saves to catalog)
        equipment_success, serial_number = self.test_scenario_2_create_equipment_saves_to_catalog()
        if not equipment_success:
            return False
        
        # Test 3: Get equipment from catalog
        catalog_success = self.test_scenario_3_get_equipment_from_catalog(serial_number)
        if not catalog_success:
            return False
        
        # Test 4: Calibrate with new fields
        calibration_success = self.test_scenario_4_calibrate_with_new_fields(serial_number)
        if not calibration_success:
            return False
        
        # Test 5: Verify calibrated equipment
        verification_success = self.test_scenario_5_verify_calibrated_equipment(serial_number)
        if not verification_success:
            return False
        
        print("\n" + "=" * 60)
        print("🎉 Todas las pruebas de FASE 1 completadas exitosamente!")
        print("=" * 60)
        
        return True

if __name__ == "__main__":
    tester = Fase1SpecificTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)