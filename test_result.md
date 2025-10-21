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

  - task: "Implementar descarga automática de certificado PDF después de calibración"
    implemented: true
    working: "NA"
    file: "/app/frontend/src/pages/EquipmentReview.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Descarga automática de PDF implementada en handleSubmit después de calibrar equipo exitosamente"

pdf:
  - task: "Crear módulo de generación de PDF con ReportLab"
    implemented: true
    working: "NA"
    file: "/app/backend/pdf_generator.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Módulo pdf_generator.py creado con función generate_certificate_pdf que incluye logo, texto legal, tabla de sensores, datos del equipo/cliente y firmas"

  - task: "Endpoint para generar y descargar certificado PDF"
    implemented: true
    working: "NA"
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Endpoint GET /api/equipment/{serial_number}/certificate creado para generar y descargar PDF de certificado de calibración"

  - task: "Guardar logo de empresa ASCONSA"
    implemented: true
    working: "NA"
    file: "/app/backend/static/logo_asconsa.png"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Logo descargado y guardado en /app/backend/static/logo_asconsa.png con fondo transparente"

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
    - "Implementar descarga automática de certificado PDF después de calibración"
    - "Crear módulo de generación de PDF con ReportLab"
    - "Endpoint para generar y descargar certificado PDF"
    - "Guardar logo de empresa ASCONSA"
  stuck_tasks: []
  test_all: true
  test_priority: "high_first"

agent_communication:
  - agent: "main"
    message: |
      FASE 1 Y FASE 2 implementadas completamente:
      
      FASE 1 - Base de Datos y Formularios (✅ TESTEADO):
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
      
      FASE 2 - Certificado PDF (PENDIENTE DE TESTING):
      Backend:
      - Librería ReportLab instalada
      - Logo ASCONSA guardado en /app/backend/static/logo_asconsa.png
      - Módulo pdf_generator.py creado con:
        * Logo en parte superior izquierda (6cm x 3cm)
        * Texto legal de certificación
        * Tabla completa de datos del equipo y cliente (incluyendo Departamento)
        * Tabla de sensores con todos los campos (incluyendo Zero y SPAN)
        * Repuestos utilizados
        * Observaciones
        * Espacio para firmas digitales (Técnico y Supervisor)
        * Pie de página con fecha de emisión
      - Endpoint GET /api/equipment/{serial_number}/certificate para generar y descargar PDF
      
      Frontend:
      - Descarga automática de PDF implementada después de calibrar equipo
      - Usuario recibe notificación de descarga exitosa
      
      Necesito testing completo de:
      FASE 1 (ya testeado por backend_testing_agent - ✅ PASSED)
      
      FASE 2 - Testing necesario:
      1. Crear y calibrar un equipo nuevo
      2. Verificar que el PDF se genere correctamente
      3. Verificar que el PDF contenga todos los elementos:
         - Logo de ASCONSA
         - Texto legal
         - Datos del equipo y cliente (con departamento)
         - Tabla de sensores (con Zero y SPAN)
         - Repuestos utilizados
         - Firmas
      4. Verificar descarga automática en frontend
  - agent: "testing"
    message: |
      🎉 FASE 1 TESTING COMPLETADO EXITOSAMENTE - TODOS LOS BACKEND TESTS PASARON
      
      ✅ RESULTADOS DE TESTING BACKEND:
      1. ✅ Campo departamento en Cliente: Funciona correctamente, se guarda y persiste
      2. ✅ Campos valor_zero y valor_span en Calibración: Funcionan correctamente, se guardan y persisten
      3. ✅ Modelo EquipmentCatalog: Funciona correctamente, equipos se guardan automáticamente
      4. ✅ Endpoint GET /api/equipment-catalog/serial/{serial}: Funciona correctamente, retorna todos los campos
      5. ✅ POST /api/equipment con catálogo: Funciona correctamente, usa upsert para actualizar catálogo
      
      📋 TESTS EJECUTADOS:
      - 20/20 tests generales pasaron
      - 5/5 tests específicos de FASE 1 pasaron
      - Todos los endpoints funcionan correctamente
      - Persistencia de datos verificada
      - No hay errores críticos en backend logs
      
      🔍 VERIFICACIONES ESPECÍFICAS COMPLETADAS:
      ✅ Cliente con departamento "Mantenimiento" creado exitosamente
      ✅ Equipo Honeywell XT-1000 creado y guardado en catálogo automáticamente
      ✅ Catálogo retorna datos correctos para serial SN-TEST-001
      ✅ Calibración con valor_zero=0 y valor_span=100 guardada correctamente
      ✅ Datos persisten correctamente en base de datos MongoDB