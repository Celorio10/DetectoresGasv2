import { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { toast } from "sonner";
import Layout from "../components/Layout";
import { Database, Plus, Search, X, Edit, Trash2, Eye } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const getAuthHeaders = () => ({
  headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
});

export default function EquipmentMasterCatalog() {
  const [equipments, setEquipments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [currentEquipment, setCurrentEquipment] = useState(null);
  
  // Filtros de búsqueda
  const [filters, setFilters] = useState({
    serial: "",
    marca: "",
    modelo: "",
    cliente: ""
  });

  // Formulario de equipo
  const [formData, setFormData] = useState({
    serial_number: "",
    brand: "",
    model: "",
    current_client_name: "",
    current_client_cif: "",
    current_client_departamento: "",
    default_sensors: [],
    general_observations: ""
  });

  // Nuevo sensor
  const [newSensor, setNewSensor] = useState({
    sensor: "",
    pre_alarm: "",
    alarm: "",
    calibration_value: ""
  });

  useEffect(() => {
    loadEquipments();
  }, []);

  const loadEquipments = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/equipment-master`, getAuthHeaders());
      setEquipments(response.data);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al cargar catálogo');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.serial) params.append('serial', filters.serial);
      if (filters.marca) params.append('marca', filters.marca);
      if (filters.modelo) params.append('modelo', filters.modelo);
      if (filters.cliente) params.append('cliente', filters.cliente);
      
      const response = await axios.get(
        `${API}/equipment-master/search?${params.toString()}`,
        getAuthHeaders()
      );
      setEquipments(response.data);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al buscar');
    } finally {
      setLoading(false);
    }
  };

  const handleClearFilters = () => {
    setFilters({ serial: "", marca: "", modelo: "", cliente: "" });
    loadEquipments();
  };

  const handleOpenDialog = (equipment = null) => {
    if (equipment) {
      setEditMode(true);
      setCurrentEquipment(equipment);
      setFormData(equipment);
    } else {
      setEditMode(false);
      setCurrentEquipment(null);
      setFormData({
        serial_number: "",
        brand: "",
        model: "",
        current_client_name: "",
        current_client_cif: "",
        current_client_departamento: "",
        default_sensors: [],
        general_observations: ""
      });
    }
    setDialogOpen(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.serial_number || !formData.brand || !formData.model) {
      toast.error('Completa los campos obligatorios');
      return;
    }

    try {
      if (editMode) {
        await axios.put(
          `${API}/equipment-master/${currentEquipment.serial_number}`,
          formData,
          getAuthHeaders()
        );
        toast.success('Equipo actualizado');
      } else {
        await axios.post(`${API}/equipment-master`, formData, getAuthHeaders());
        toast.success('Equipo registrado en catálogo');
      }
      
      setDialogOpen(false);
      loadEquipments();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al guardar equipo');
    }
  };

  const handleDelete = async (serialNumber) => {
    if (!window.confirm('¿Eliminar este equipo del catálogo maestro?')) return;
    
    try {
      await axios.delete(`${API}/equipment-master/${serialNumber}`, getAuthHeaders());
      toast.success('Equipo eliminado');
      loadEquipments();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al eliminar');
    }
  };

  const handleAddSensor = () => {
    if (!newSensor.sensor) {
      toast.error('Introduce el nombre del sensor');
      return;
    }
    
    setFormData({
      ...formData,
      default_sensors: [...formData.default_sensors, { ...newSensor }]
    });
    
    setNewSensor({ sensor: "", pre_alarm: "", alarm: "", calibration_value: "" });
  };

  const handleRemoveSensor = (index) => {
    setFormData({
      ...formData,
      default_sensors: formData.default_sensors.filter((_, i) => i !== index)
    });
  };

  return (
    <Layout>
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <Database className="w-8 h-8 text-blue-600" />
            <h1 className="text-3xl sm:text-4xl font-bold text-gray-800" style={{ fontFamily: 'Space Grotesk' }}>
              Catálogo de Equipos
            </h1>
          </div>
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button 
                onClick={() => handleOpenDialog()}
                className="bg-blue-600 hover:bg-blue-700"
              >
                <Plus className="w-4 h-4 mr-2" />
                Nuevo Equipo
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>
                  {editMode ? 'Editar Equipo' : 'Registrar Nuevo Equipo'}
                </DialogTitle>
              </DialogHeader>
              
              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Datos básicos */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <Label>Número de Serie *</Label>
                    <Input
                      value={formData.serial_number}
                      onChange={(e) => setFormData({...formData, serial_number: e.target.value})}
                      disabled={editMode}
                      required
                    />
                  </div>
                  <div>
                    <Label>Marca *</Label>
                    <Input
                      value={formData.brand}
                      onChange={(e) => setFormData({...formData, brand: e.target.value})}
                      required
                    />
                  </div>
                  <div>
                    <Label>Modelo *</Label>
                    <Input
                      value={formData.model}
                      onChange={(e) => setFormData({...formData, model: e.target.value})}
                      required
                    />
                  </div>
                </div>

                {/* Cliente actual */}
                <div className="border-t pt-4">
                  <h3 className="font-bold mb-3">Cliente Actual</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <Label>Nombre Cliente</Label>
                      <Input
                        value={formData.current_client_name}
                        onChange={(e) => setFormData({...formData, current_client_name: e.target.value})}
                      />
                    </div>
                    <div>
                      <Label>CIF</Label>
                      <Input
                        value={formData.current_client_cif}
                        onChange={(e) => setFormData({...formData, current_client_cif: e.target.value})}
                      />
                    </div>
                    <div>
                      <Label>Departamento</Label>
                      <Input
                        value={formData.current_client_departamento}
                        onChange={(e) => setFormData({...formData, current_client_departamento: e.target.value})}
                      />
                    </div>
                  </div>
                </div>

                {/* Sensores predeterminados */}
                <div className="border-t pt-4">
                  <h3 className="font-bold mb-3">Sensores Predeterminados</h3>
                  
                  {/* Agregar sensor */}
                  <div className="grid grid-cols-5 gap-2 mb-3">
                    <Input
                      placeholder="Sensor"
                      value={newSensor.sensor}
                      onChange={(e) => setNewSensor({...newSensor, sensor: e.target.value})}
                    />
                    <Input
                      placeholder="Pre-Alarma"
                      value={newSensor.pre_alarm}
                      onChange={(e) => setNewSensor({...newSensor, pre_alarm: e.target.value})}
                    />
                    <Input
                      placeholder="Alarma"
                      value={newSensor.alarm}
                      onChange={(e) => setNewSensor({...newSensor, alarm: e.target.value})}
                    />
                    <Input
                      placeholder="Valor Cal."
                      value={newSensor.calibration_value}
                      onChange={(e) => setNewSensor({...newSensor, calibration_value: e.target.value})}
                    />
                    <Button type="button" onClick={handleAddSensor} size="sm">
                      <Plus className="w-4 h-4" />
                    </Button>
                  </div>

                  {/* Lista de sensores */}
                  {formData.default_sensors.length > 0 && (
                    <div className="border rounded p-2 max-h-40 overflow-y-auto">
                      {formData.default_sensors.map((sensor, idx) => (
                        <div key={idx} className="flex items-center justify-between bg-gray-50 p-2 mb-1 rounded text-sm">
                          <div className="flex gap-3">
                            <span className="font-semibold">{sensor.sensor}</span>
                            <span>Pre-A: {sensor.pre_alarm}</span>
                            <span>Alarma: {sensor.alarm}</span>
                            <span>Val.Cal: {sensor.calibration_value}</span>
                          </div>
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => handleRemoveSensor(idx)}
                          >
                            <Trash2 className="w-4 h-4 text-red-600" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Observaciones generales */}
                <div>
                  <Label>Observaciones Generales</Label>
                  <Textarea
                    value={formData.general_observations}
                    onChange={(e) => setFormData({...formData, general_observations: e.target.value})}
                    rows={3}
                  />
                </div>

                <div className="flex gap-2 justify-end">
                  <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                    Cancelar
                  </Button>
                  <Button type="submit" className="bg-blue-600 hover:bg-blue-700">
                    {editMode ? 'Actualizar' : 'Guardar'}
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {/* Buscador */}
        <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100 mb-6">
          <h2 className="text-xl font-bold mb-4" style={{ fontFamily: 'Space Grotesk' }}>
            🔍 Buscador
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
            <div>
              <Label>Nº Serie</Label>
              <Input
                placeholder="Buscar..."
                value={filters.serial}
                onChange={(e) => setFilters({...filters, serial: e.target.value})}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
            </div>
            <div>
              <Label>Marca</Label>
              <Input
                placeholder="Buscar..."
                value={filters.marca}
                onChange={(e) => setFilters({...filters, marca: e.target.value})}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
            </div>
            <div>
              <Label>Modelo</Label>
              <Input
                placeholder="Buscar..."
                value={filters.modelo}
                onChange={(e) => setFilters({...filters, modelo: e.target.value})}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
            </div>
            <div>
              <Label>Cliente</Label>
              <Input
                placeholder="Buscar..."
                value={filters.cliente}
                onChange={(e) => setFilters({...filters, cliente: e.target.value})}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
            </div>
          </div>
          <div className="flex gap-2">
            <Button onClick={handleSearch} className="bg-blue-600 hover:bg-blue-700">
              <Search className="w-4 h-4 mr-2" />
              Buscar
            </Button>
            <Button onClick={handleClearFilters} variant="outline">
              <X className="w-4 h-4 mr-2" />
              Limpiar
            </Button>
          </div>
        </div>

        {/* Tabla de equipos */}
        {loading ? (
          <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100 text-center">
            <p className="text-gray-600">Cargando catálogo...</p>
          </div>
        ) : equipments.length > 0 ? (
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
            <h2 className="text-xl font-bold mb-4" style={{ fontFamily: 'Space Grotesk' }}>
              Equipos Registrados ({equipments.length})
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-gray-50">
                    <th className="text-left p-3 text-sm font-semibold">Nº Serie</th>
                    <th className="text-left p-3 text-sm font-semibold">Marca</th>
                    <th className="text-left p-3 text-sm font-semibold">Modelo</th>
                    <th className="text-left p-3 text-sm font-semibold">Cliente Actual</th>
                    <th className="text-left p-3 text-sm font-semibold">Sensores</th>
                    <th className="text-center p-3 text-sm font-semibold">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {equipments.map((equipment) => (
                    <tr key={equipment.serial_number} className="border-b hover:bg-gray-50">
                      <td className="p-3 font-semibold text-blue-600">{equipment.serial_number}</td>
                      <td className="p-3">{equipment.brand}</td>
                      <td className="p-3">{equipment.model}</td>
                      <td className="p-3">{equipment.current_client_name || 'N/A'}</td>
                      <td className="p-3 text-sm text-gray-600">
                        {equipment.default_sensors?.length || 0} sensor(es)
                      </td>
                      <td className="p-3 text-center">
                        <div className="flex gap-2 justify-center">
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleOpenDialog(equipment)}
                          >
                            <Edit className="w-4 h-4 text-blue-600" />
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleDelete(equipment.serial_number)}
                          >
                            <Trash2 className="w-4 h-4 text-red-600" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100 text-center">
            <Database className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-600">No hay equipos registrados en el catálogo</p>
          </div>
        )}
      </div>
    </Layout>
  );
}
