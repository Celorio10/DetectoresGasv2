import { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Checkbox } from "@/components/ui/checkbox";
import { toast } from "sonner";
import Layout from "../components/Layout";
import { ClipboardCheck, Plus, Search, Trash2 } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const getAuthHeaders = () => ({
  headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
});

export default function EquipmentReview() {
  const [searchSerial, setSearchSerial] = useState("");
  const [equipment, setEquipment] = useState(null);
  const [technicians, setTechnicians] = useState([]);
  const [pendingEquipment, setPendingEquipment] = useState([]);
  const [selectedEquipmentId, setSelectedEquipmentId] = useState(null);
  const [calibrationData, setCalibrationData] = useState([{
    sensor: "",
    pre_alarm: "",
    alarm: "",
    calibration_value: "",
    valor_zero: "",
    valor_span: "",
    calibration_bottle: "",
    approved: false
  }]);
  const [spareParts, setSpareParts] = useState([]);
  const [newSparePart, setNewSparePart] = useState({ descripcion: "", referencia: "", garantia: false });
  const [calibrationDate, setCalibrationDate] = useState(new Date().toISOString().split('T')[0]);
  const [selectedTechnician, setSelectedTechnician] = useState("");
  const [newTechnician, setNewTechnician] = useState("");
  const [loading, setLoading] = useState(false);
  const [technicianDialogOpen, setTechnicianDialogOpen] = useState(false);

  useEffect(() => {
    loadTechnicians();
    loadPendingEquipment();
  }, []);

  const loadTechnicians = async () => {
    try {
      const response = await axios.get(`${API}/technicians`, getAuthHeaders());
      setTechnicians(response.data);
    } catch (error) {
      toast.error('Error al cargar técnicos');
    }
  };

  const loadPendingEquipment = async () => {
    try {
      const response = await axios.get(`${API}/equipment/pending`, getAuthHeaders());
      setPendingEquipment(response.data);
    } catch (error) {
      toast.error('Error al cargar equipos pendientes');
    }
  };

  const handleSearch = async () => {
    if (!searchSerial.trim()) {
      toast.error('Introduce un número de serie');
      return;
    }
    try {
      const response = await axios.get(`${API}/equipment/serial/${searchSerial}`, getAuthHeaders());
      setEquipment(response.data);
      setSelectedEquipmentId(response.data.id);
      
      // Cargar sensores de la última calibración desde el catálogo
      try {
        const catalogResponse = await axios.get(`${API}/equipment-catalog/serial/${searchSerial}`, getAuthHeaders());
        if (catalogResponse.data && catalogResponse.data.last_calibration_data && catalogResponse.data.last_calibration_data.length > 0) {
          // Solo cargar Sensor, Pre-Alarma y Alarma. SPAN, ZERO y Botella siempre vacíos
          const sensorsWithResetFields = catalogResponse.data.last_calibration_data.map(sensor => ({
            sensor: sensor.sensor || "",
            pre_alarm: sensor.pre_alarm || "",
            alarm: sensor.alarm || "",
            calibration_value: sensor.calibration_value || "",
            valor_zero: "",  // Siempre vacío
            valor_span: "",  // Siempre vacío
            calibration_bottle: "",  // Siempre vacío
            approved: false
          }));
          setCalibrationData(sensorsWithResetFields);
          toast.info('Sensores de última calibración cargados');
        }
      } catch (catalogError) {
        // Si no hay datos en catálogo, iniciar con tabla vacía
        setCalibrationData([{
          sensor: "",
          pre_alarm: "",
          alarm: "",
          calibration_value: "",
          valor_zero: "",
          valor_span: "",
          calibration_bottle: "",
          approved: false
        }]);
      }
      
      // Reset otros campos para nueva calibración
      setSpareParts([]);
      setCalibrationDate(new Date().toISOString().split('T')[0]);
      setSelectedTechnician("");
      
      toast.success('Equipo encontrado');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Equipo no encontrado');
      setEquipment(null);
    }
  };

  const handleSelectEquipment = async (selectedEquip) => {
    setEquipment(selectedEquip);
    setSelectedEquipmentId(selectedEquip.id);
    setSearchSerial(selectedEquip.serial_number);
    
    // Cargar sensores de la última calibración desde el catálogo
    try {
      const catalogResponse = await axios.get(`${API}/equipment-catalog/serial/${selectedEquip.serial_number}`, getAuthHeaders());
      if (catalogResponse.data && catalogResponse.data.last_calibration_data && catalogResponse.data.last_calibration_data.length > 0) {
        // Solo cargar Sensor, Pre-Alarma y Alarma. SPAN, ZERO y Botella siempre vacíos
        const sensorsWithResetFields = catalogResponse.data.last_calibration_data.map(sensor => ({
          sensor: sensor.sensor || "",
          pre_alarm: sensor.pre_alarm || "",
          alarm: sensor.alarm || "",
          calibration_value: sensor.calibration_value || "",
          valor_zero: "",  // Siempre vacío
          valor_span: "",  // Siempre vacío
          calibration_bottle: "",  // Siempre vacío
          approved: false
        }));
        setCalibrationData(sensorsWithResetFields);
        toast.info('Sensores de última calibración cargados');
      } else {
        // Reset calibration data para nuevo equipo
        setCalibrationData([{
          sensor: "",
          pre_alarm: "",
          alarm: "",
          calibration_value: "",
          valor_zero: "",
          valor_span: "",
          calibration_bottle: "",
          approved: false
        }]);
      }
    } catch (catalogError) {
      // Si no hay datos en catálogo, iniciar con tabla vacía
      setCalibrationData([{
        sensor: "",
        pre_alarm: "",
        alarm: "",
        calibration_value: "",
        valor_zero: "",
        valor_span: "",
        calibration_bottle: "",
        approved: false
      }]);
    }
    
    // Reset otros campos para nueva calibración
    setSpareParts([]);
    setCalibrationDate(new Date().toISOString().split('T')[0]);
    setSelectedTechnician("");
    
    toast.success('Equipo seleccionado');
  };

  const handleAddRow = () => {
    if (calibrationData.length < 6) {
      setCalibrationData([...calibrationData, {
        sensor: "",
        pre_alarm: "",
        alarm: "",
        calibration_value: "",
        valor_zero: "",
        valor_span: "",
        calibration_bottle: "",
        approved: false
      }]);
    }
  };

  const handleRemoveRow = (index) => {
    const newData = calibrationData.filter((_, i) => i !== index);
    setCalibrationData(newData);
  };

  const handleAddSparePart = () => {
    if (newSparePart.descripcion.trim() && newSparePart.referencia.trim()) {
      setSpareParts([...spareParts, { ...newSparePart }]);
      setNewSparePart({ descripcion: "", referencia: "", garantia: false });
    } else {
      toast.error('Completa descripción y referencia');
    }
  };

  const handleRemoveSparePart = (index) => {
    setSpareParts(spareParts.filter((_, i) => i !== index));
  };

  const handleToggleGarantia = (index) => {
    const newParts = [...spareParts];
    newParts[index].garantia = !newParts[index].garantia;
    setSpareParts(newParts);
  };

  const handleCalibrationChange = (index, field, value) => {
    const newData = [...calibrationData];
    newData[index][field] = value;
    setCalibrationData(newData);
  };

  const handleAddTechnician = async () => {
    if (!newTechnician.trim()) return;
    
    // Cerrar el modal primero
    setTechnicianDialogOpen(false);
    
    // Delay más largo para asegurar que el modal y overlay se cierran completamente
    setTimeout(async () => {
      try {
        await axios.post(`${API}/technicians`, { name: newTechnician }, getAuthHeaders());
        toast.success('Técnico añadido');
        setNewTechnician("");
        loadTechnicians();
      } catch (error) {
        toast.error(error.response?.data?.detail || 'Error al añadir técnico');
      }
    }, 300);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!equipment) return;
    
    setLoading(true);
    try {
      await axios.put(
        `${API}/equipment/${equipment.serial_number}/calibrate`,
        {
          calibration_data: calibrationData,
          spare_parts: spareParts,
          calibration_date: calibrationDate,
          technician: selectedTechnician
        },
        getAuthHeaders()
      );
      toast.success('Equipo calibrado correctamente');
      
      // Reset
      setEquipment(null);
      setSearchSerial("");
      setSelectedEquipmentId(null);
      setCalibrationData([{
        sensor: "",
        pre_alarm: "",
        alarm: "",
        calibration_value: "",
        valor_zero: "",
        valor_span: "",
        calibration_bottle: "",
        approved: false
      }]);
      setSpareParts([]);
      setSelectedTechnician("");
      // Recargar lista de equipos pendientes
      loadPendingEquipment();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al calibrar equipo');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="max-w-6xl mx-auto" data-testid="equipment-review-page">
        <div className="flex items-center gap-3 mb-8">
          <ClipboardCheck className="w-8 h-8 text-green-600" />
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-800" style={{ fontFamily: 'Space Grotesk' }}>
            Revisión de Equipos
          </h1>
        </div>

        {/* Search Section */}
        <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100 mb-6">
          <Label htmlFor="search">Buscar por Número de Serie</Label>
          <div className="flex gap-2 mt-2">
            <Input
              id="search"
              data-testid="search-serial-input"
              placeholder="Introduce el número de serie"
              value={searchSerial}
              onChange={(e) => setSearchSerial(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
            <Button onClick={handleSearch} data-testid="search-button">
              <Search className="w-4 h-4 mr-2" />
              Buscar
            </Button>
          </div>
        </div>

        {/* Pending Equipment Table */}
        {!equipment && pendingEquipment.length > 0 && (
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100 mb-6">
            <h2 className="text-xl font-bold mb-4" style={{ fontFamily: 'Space Grotesk' }}>
              Equipos Pendientes de Revisión ({pendingEquipment.length})
            </h2>
            <p className="text-sm text-gray-600 mb-4">
              Selecciona un equipo de la lista para comenzar la revisión
            </p>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-gray-50">
                    <th className="text-left p-3 text-sm font-semibold">Marca</th>
                    <th className="text-left p-3 text-sm font-semibold">Modelo</th>
                    <th className="text-left p-3 text-sm font-semibold">Cliente</th>
                    <th className="text-left p-3 text-sm font-semibold">Número de Serie</th>
                    <th className="text-left p-3 text-sm font-semibold">Fecha Entrada</th>
                    <th className="text-center p-3 text-sm font-semibold">Acción</th>
                  </tr>
                </thead>
                <tbody>
                  {pendingEquipment.map((item) => (
                    <tr 
                      key={item.id} 
                      className="border-b hover:bg-gray-50 transition-colors cursor-pointer"
                      onClick={() => handleSelectEquipment(item)}
                    >
                      <td className="p-3" data-testid={`pending-brand-${item.serial_number}`}>{item.brand}</td>
                      <td className="p-3">{item.model}</td>
                      <td className="p-3">{item.client_name}</td>
                      <td className="p-3 font-semibold text-blue-600" data-testid={`pending-serial-${item.serial_number}`}>
                        {item.serial_number}
                      </td>
                      <td className="p-3 text-sm text-gray-600">{item.entry_date}</td>
                      <td className="p-3 text-center">
                        <Button 
                          size="sm" 
                          onClick={(e) => {
                            e.stopPropagation();
                            handleSelectEquipment(item);
                          }}
                          data-testid={`select-equipment-${item.serial_number}`}
                          className="bg-green-600 hover:bg-green-700"
                        >
                          Seleccionar
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {!equipment && pendingEquipment.length === 0 && (
          <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100 mb-6 text-center">
            <p className="text-gray-600" data-testid="no-pending-equipment">
              No hay equipos pendientes de revisión
            </p>
          </div>
        )}

        {/* Equipment Info */}
        {equipment && (
          <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100 mb-6" data-testid="equipment-info">
            <h2 className="text-2xl font-bold mb-4" style={{ fontFamily: 'Space Grotesk' }}>Información del Equipo</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
              <div>
                <p className="text-gray-600">Marca:</p>
                <p className="font-semibold" data-testid="equipment-brand">{equipment.brand}</p>
              </div>
              <div>
                <p className="text-gray-600">Modelo:</p>
                <p className="font-semibold" data-testid="equipment-model">{equipment.model}</p>
              </div>
              <div>
                <p className="text-gray-600">Cliente:</p>
                <p className="font-semibold" data-testid="equipment-client">{equipment.client_name}</p>
              </div>
              <div>
                <p className="text-gray-600">CIF:</p>
                <p className="font-semibold">{equipment.client_cif}</p>
              </div>
              <div>
                <p className="text-gray-600">Fecha Entrada:</p>
                <p className="font-semibold">{equipment.entry_date}</p>
              </div>
              <div>
                <p className="text-gray-600">Observaciones:</p>
                <p className="font-semibold">{equipment.observations || 'N/A'}</p>
              </div>
            </div>
          </div>
        )}

        {/* Calibration Form */}
        {equipment && (
          <form onSubmit={handleSubmit}>
            <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100 mb-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold" style={{ fontFamily: 'Space Grotesk' }}>Tabla de Calibración</h2>
                <Button 
                  type="button" 
                  onClick={handleAddRow} 
                  disabled={calibrationData.length >= 6}
                  variant="outline"
                  data-testid="add-sensor-row-button"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Añadir Sensor
                </Button>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-2 text-sm font-semibold">Sensor</th>
                      <th className="text-left p-2 text-sm font-semibold">Pre-Alarma</th>
                      <th className="text-left p-2 text-sm font-semibold">Alarma</th>
                      <th className="text-left p-2 text-sm font-semibold">Valor Calibración</th>
                      <th className="text-left p-2 text-sm font-semibold">Valor de Zero</th>
                      <th className="text-left p-2 text-sm font-semibold">Valor de SPAN</th>
                      <th className="text-left p-2 text-sm font-semibold">Botella</th>
                      <th className="text-left p-2 text-sm font-semibold">APTO</th>
                      <th className="text-left p-2 text-sm font-semibold">Acción</th>
                    </tr>
                  </thead>
                  <tbody>
                    {calibrationData.map((row, index) => (
                      <tr key={index} className="border-b">
                        <td className="p-2">
                          <Input
                            value={row.sensor}
                            onChange={(e) => handleCalibrationChange(index, 'sensor', e.target.value)}
                            placeholder="Sensor"
                            data-testid={`sensor-input-${index}`}
                          />
                        </td>
                        <td className="p-2">
                          <Input
                            value={row.pre_alarm}
                            onChange={(e) => handleCalibrationChange(index, 'pre_alarm', e.target.value)}
                            placeholder="Pre-Alarma"
                            data-testid={`pre-alarm-input-${index}`}
                          />
                        </td>
                        <td className="p-2">
                          <Input
                            value={row.alarm}
                            onChange={(e) => handleCalibrationChange(index, 'alarm', e.target.value)}
                            placeholder="Alarma"
                            data-testid={`alarm-input-${index}`}
                          />
                        </td>
                        <td className="p-2">
                          <Input
                            value={row.calibration_value}
                            onChange={(e) => handleCalibrationChange(index, 'calibration_value', e.target.value)}
                            placeholder="Valor"
                            data-testid={`calibration-value-input-${index}`}
                          />
                        </td>
                        <td className="p-2">
                          <Input
                            value={row.valor_zero}
                            onChange={(e) => handleCalibrationChange(index, 'valor_zero', e.target.value)}
                            placeholder="Zero"
                            data-testid={`valor-zero-input-${index}`}
                          />
                        </td>
                        <td className="p-2">
                          <Input
                            value={row.valor_span}
                            onChange={(e) => handleCalibrationChange(index, 'valor_span', e.target.value)}
                            placeholder="SPAN"
                            data-testid={`valor-span-input-${index}`}
                          />
                        </td>
                        <td className="p-2">
                          <Input
                            value={row.calibration_bottle}
                            onChange={(e) => handleCalibrationChange(index, 'calibration_bottle', e.target.value)}
                            placeholder="Botella"
                            data-testid={`calibration-bottle-input-${index}`}
                          />
                        </td>
                        <td className="p-2">
                          <Checkbox
                            checked={row.approved}
                            onCheckedChange={(checked) => handleCalibrationChange(index, 'approved', checked)}
                            data-testid={`approved-checkbox-${index}`}
                          />
                        </td>
                        <td className="p-2">
                          <Button
                            type="button"
                            variant="ghost"
                            size="icon"
                            onClick={() => handleRemoveRow(index)}
                            data-testid={`remove-sensor-${index}`}
                          >
                            <Trash2 className="w-4 h-4 text-red-500" />
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100 space-y-6">
              <div>
                <Label htmlFor="spare_parts">Repuestos Utilizados</Label>
                <Textarea
                  id="spare_parts"
                  data-testid="spare-parts-input"
                  value={spareParts}
                  onChange={(e) => setSpareParts(e.target.value)}
                  rows={3}
                  className="mt-2"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="calibration_date">Fecha de Calibración</Label>
                  <Input
                    id="calibration_date"
                    data-testid="calibration-date-input"
                    type="date"
                    value={calibrationDate}
                    onChange={(e) => setCalibrationDate(e.target.value)}
                    required
                    className="mt-2"
                  />
                </div>

                <div>
                  <Label htmlFor="technician">Técnico</Label>
                  <div className="flex gap-2 mt-2">
                    <Select value={selectedTechnician} onValueChange={setSelectedTechnician} required>
                      <SelectTrigger data-testid="technician-select">
                        <SelectValue placeholder="Seleccionar técnico" />
                      </SelectTrigger>
                      <SelectContent>
                        {technicians.map(t => (
                          <SelectItem key={t.id} value={t.name}>{t.name}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Dialog open={technicianDialogOpen} onOpenChange={setTechnicianDialogOpen}>
                      <DialogTrigger asChild>
                        <Button type="button" variant="outline" size="icon" data-testid="add-technician-button">
                          <Plus className="w-4 h-4" />
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>Añadir Nuevo Técnico</DialogTitle>
                        </DialogHeader>
                        <div className="space-y-4">
                          <Input
                            placeholder="Nombre del técnico"
                            value={newTechnician}
                            onChange={(e) => setNewTechnician(e.target.value)}
                            data-testid="new-technician-input"
                          />
                          <Button onClick={handleAddTechnician} className="w-full" data-testid="save-technician-button">Guardar</Button>
                        </div>
                      </DialogContent>
                    </Dialog>
                  </div>
                </div>
              </div>

              <Button
                type="submit"
                disabled={loading}
                className="w-full py-6 text-lg font-semibold bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700"
                data-testid="calibrate-equipment-button"
              >
                {loading ? 'Guardando...' : 'Equipo Calibrado'}
              </Button>
            </div>
          </form>
        )}
      </div>
    </Layout>
  );
}