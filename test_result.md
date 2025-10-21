#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: |
  Sistema de gestión de equipos en taller con funcionalidades de entrada, revisión, salida y resumen.
  FASE 1: Agregar campo "Departamento" a clientes, campos "Valor de Zero" y "Valor de SPAN" a calibración de sensores, e implementar auto-completado de equipos.
  FASE 2: Generar certificado PDF con logo de empresa, tabla de sensores, datos de equipo/cliente y firmas digitales.

backend:
  - task: "Agregar campo departamento al modelo Client"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Campo 'departamento' agregado al modelo Client (línea 71)"
      - working: true
        agent: "testing"
        comment: "✅ TESTED: Campo departamento funciona correctamente. Cliente creado con departamento 'Mantenimiento' se guarda y persiste correctamente en la base de datos."

  - task: "Agregar campos valor_zero y valor_span al modelo SensorCalibration"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Campos 'valor_zero' y 'valor_span' agregados al modelo SensorCalibration (líneas 83-84)"
      - working: true
        agent: "testing"
        comment: "✅ TESTED: Campos valor_zero y valor_span funcionan correctamente. Calibración con valores '0' y '100' se guarda y persiste correctamente. Datos verificados en GET /api/equipment/serial/{serial}."

  - task: "Crear modelo EquipmentCatalog para persistencia de equipos"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Modelo EquipmentCatalog creado con serial_number, brand, model, client_name, client_cif, client_departamento (líneas 77-85)"
      - working: true
        agent: "testing"
        comment: "✅ TESTED: Modelo EquipmentCatalog funciona correctamente. Equipos se guardan automáticamente en catálogo con todos los campos requeridos incluyendo client_departamento."

  - task: "Endpoint para obtener equipo del catálogo por serial"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Endpoint GET /api/equipment-catalog/serial/{serial_number} creado para obtener datos históricos del equipo"
      - working: true
        agent: "testing"
        comment: "✅ TESTED: Endpoint GET /api/equipment-catalog/serial/{serial_number} funciona correctamente. Retorna todos los campos requeridos: serial_number, brand, model, client_name, client_cif, client_departamento. Probado con serial 'SN-TEST-001'."

  - task: "Actualizar endpoint de creación de equipos para guardar en catálogo"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "POST /api/equipment actualizado para guardar/actualizar entrada en equipment_catalog usando upsert"
      - working: true
        agent: "testing"
        comment: "✅ TESTED: POST /api/equipment funciona correctamente. Equipo se crea en colección equipment y automáticamente se guarda/actualiza en equipment_catalog usando upsert. Verificado que el catálogo contiene todos los datos del equipo."

frontend:
  - task: "Agregar campo Departamento al formulario de cliente en EquipmentEntry"
    implemented: true
    working: "NA"
    file: "/app/frontend/src/pages/EquipmentEntry.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Campo 'departamento' agregado al formulario de nuevo cliente y al estado del componente"

  - task: "Implementar auto-completado de equipos por número de serie"
    implemented: true
    working: "NA"
    file: "/app/frontend/src/pages/EquipmentEntry.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Función handleSerialNumberChange implementada para cargar datos del catálogo cuando se ingresa un número de serie existente"

  - task: "Agregar columnas Valor de Zero y Valor de SPAN en tabla de calibración"
    implemented: true
    working: "NA"
    file: "/app/frontend/src/pages/EquipmentReview.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Campos 'valor_zero' y 'valor_span' agregados a la tabla de calibración de sensores con sus respectivos inputs"

metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 0
  run_ui: false

test_plan:
  current_focus:
    - "Agregar campo departamento al modelo Client"
    - "Agregar campos valor_zero y valor_span al modelo SensorCalibration"
    - "Crear modelo EquipmentCatalog para persistencia de equipos"
    - "Endpoint para obtener equipo del catálogo por serial"
    - "Actualizar endpoint de creación de equipos para guardar en catálogo"
    - "Agregar campo Departamento al formulario de cliente en EquipmentEntry"
    - "Implementar auto-completado de equipos por número de serie"
    - "Agregar columnas Valor de Zero y Valor de SPAN en tabla de calibración"
  stuck_tasks: []
  test_all: true
  test_priority: "high_first"

agent_communication:
  - agent: "main"
    message: |
      FASE 1 implementada completamente:
      
      Backend:
      - Campo 'departamento' agregado al modelo Client
      - Campos 'valor_zero' y 'valor_span' agregados al modelo SensorCalibration
      - Modelo EquipmentCatalog creado para almacenar equipos permanentemente
      - Endpoint GET /api/equipment-catalog/serial/{serial_number} para obtener datos históricos
      - POST /api/equipment actualizado para guardar en catálogo con upsert
      
      Frontend:
      - Campo 'departamento' agregado al formulario de nuevo cliente en EquipmentEntry
      - Auto-completado implementado: al ingresar número de serie, se cargan datos del catálogo
      - Campos 'valor_zero' y 'valor_span' agregados a la tabla de calibración en EquipmentReview
      
      Necesito testing completo de:
      1. Agregar cliente con departamento
      2. Ingresar equipo nuevo (debe guardarse en catálogo)
      3. Ingresar mismo equipo nuevamente (debe auto-completar datos)
      4. Calibrar equipo con nuevos campos Zero y SPAN
      5. Verificar que todos los datos se guarden correctamente