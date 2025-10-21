import { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { toast } from "sonner";
import Layout from "../components/Layout";
import { PackageOpen, ChevronDown, ChevronUp } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const getAuthHeaders = () => ({
  headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
});

export default function EquipmentExit() {
  const [equipment, setEquipment] = useState([]);
  const [selectedEquipment, setSelectedEquipment] = useState([]);
  const [expandedEquipment, setExpandedEquipment] = useState(null);
  const [deliveryNote, setDeliveryNote] = useState("");
  const [deliveryLocation, setDeliveryLocation] = useState("");
  const [deliveryDate, setDeliveryDate] = useState(new Date().toISOString().split('T')[0]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadEquipment();
  }, []);

  const loadEquipment = async () => {
    try {
      const response = await axios.get(`${API}/equipment/calibrated`, getAuthHeaders());
      setEquipment(response.data);
    } catch (error) {
      toast.error('Error al cargar equipos');
    }
  };

  const handleToggleEquipment = (serialNumber) => {
    if (selectedEquipment.includes(serialNumber)) {
      setSelectedEquipment(selectedEquipment.filter(s => s !== serialNumber));
    } else {
      setSelectedEquipment([...selectedEquipment, serialNumber]);
    }
  };

  const handleToggleExpand = (serialNumber) => {
    if (expandedEquipment === serialNumber) {
      setExpandedEquipment(null);
    } else {
      setExpandedEquipment(serialNumber);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (selectedEquipment.length === 0) {
      toast.error('Selecciona al menos un equipo');
      return;
    }

    setLoading(true);
    try {
      await axios.put(
        `${API}/equipment/deliver`,
        {
          serial_numbers: selectedEquipment,
          delivery_note: deliveryNote,
          delivery_location: deliveryLocation,
          delivery_date: deliveryDate
        },
        getAuthHeaders()
      );
      toast.success('Equipos entregados correctamente');
      
      // Descargar certificados PDF para cada equipo entregado
      for (const serialNumber of selectedEquipment) {
        try {
          const response = await axios.get(
            `${API}/equipment/${serialNumber}/certificate`,
            {
              ...getAuthHeaders(),
              responseType: 'blob'
            }
          );
          
          // Crear un enlace temporal para descargar el PDF
          const url = window.URL.createObjectURL(new Blob([response.data]));
          const link = document.createElement('a');
          link.href = url;
          link.setAttribute('download', `Certificado_${serialNumber}_${deliveryNote}.pdf`);
          document.body.appendChild(link);
          link.click();
          link.remove();
          window.URL.revokeObjectURL(url);
          
          // Pequeña pausa entre descargas para evitar problemas del navegador
          await new Promise(resolve => setTimeout(resolve, 500));
        } catch (pdfError) {
          console.error(`Error descargando certificado para ${serialNumber}:`, pdfError);
          toast.error(`Error al descargar certificado de ${serialNumber}`);
        }
      }
      
      toast.success(`${selectedEquipment.length} certificado(s) descargado(s)`);
      
      setSelectedEquipment([]);
      setDeliveryNote("");
      setDeliveryLocation("");
      loadEquipment();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al entregar equipos');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="max-w-7xl mx-auto" data-testid="equipment-exit-page">
        <div className="flex items-center gap-3 mb-8">
          <PackageOpen className="w-8 h-8 text-orange-600" />
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-800" style={{ fontFamily: 'Space Grotesk' }}>
            Salida de Equipos de Taller
          </h1>
        </div>

        <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100 mb-6">
          <h2 className="text-xl font-bold mb-4" style={{ fontFamily: 'Space Grotesk' }}>Equipos Calibrados Pendientes de Entrega</h2>
          
          {equipment.length === 0 ? (
            <p className="text-gray-600 text-center py-8" data-testid="no-equipment-message">No hay equipos calibrados pendientes de entrega</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-gray-50">
                    <th className="text-left p-3 text-sm font-semibold">Seleccionar</th>
                    <th className="text-left p-3 text-sm font-semibold">Ver Detalles</th>
                    <th className="text-left p-3 text-sm font-semibold">Nº Serie</th>
                    <th className="text-left p-3 text-sm font-semibold">Marca</th>
                    <th className="text-left p-3 text-sm font-semibold">Modelo</th>
                    <th className="text-left p-3 text-sm font-semibold">Cliente</th>
                    <th className="text-left p-3 text-sm font-semibold">Departamento</th>
                    <th className="text-left p-3 text-sm font-semibold">Fecha Entrada</th>
                    <th className="text-left p-3 text-sm font-semibold">Técnico</th>
                  </tr>
                </thead>
                <tbody>
                  {equipment.map((item) => (
                    <>
                      <tr key={item.serial_number} className="border-b hover:bg-gray-50">
                        <td className="p-3">
                          <Checkbox
                            checked={selectedEquipment.includes(item.serial_number)}
                            onCheckedChange={() => handleToggleEquipment(item.serial_number)}
                            data-testid={`select-equipment-${item.serial_number}`}
                          />
                        </td>
                        <td className="p-3">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleToggleExpand(item.serial_number)}
                            data-testid={`expand-equipment-${item.serial_number}`}
                          >
                            {expandedEquipment === item.serial_number ? (
                              <ChevronUp className="w-4 h-4" />
                            ) : (
                              <ChevronDown className="w-4 h-4" />
                            )}
                          </Button>
                        </td>
                        <td className="p-3 font-semibold" data-testid={`serial-${item.serial_number}`}>{item.serial_number}</td>
                        <td className="p-3">{item.brand}</td>
                        <td className="p-3">{item.model}</td>
                        <td className="p-3">{item.client_name}</td>
                        <td className="p-3">{item.client_departamento || 'N/A'}</td>
                        <td className="p-3">{item.entry_date}</td>
                        <td className="p-3">{item.technician}</td>
                      </tr>
                      {expandedEquipment === item.serial_number && (
                        <tr className="bg-blue-50">
                          <td colSpan="9" className="p-4">
                            <div className="space-y-4">
                              {/* Tabla de Calibración */}
                              <div>
                                <h3 className="font-bold text-sm mb-2">Datos de Calibración</h3>
                                {item.calibration_data && item.calibration_data.length > 0 ? (
                                  <div className="overflow-x-auto">
                                    <table className="w-full text-sm border">
                                      <thead className="bg-gray-100">
                                        <tr>
                                          <th className="border p-2 text-left">Sensor</th>
                                          <th className="border p-2 text-left">Pre-Alarma</th>
                                          <th className="border p-2 text-left">Alarma</th>
                                          <th className="border p-2 text-left">Valor Cal.</th>
                                          <th className="border p-2 text-left">Zero</th>
                                          <th className="border p-2 text-left">SPAN</th>
                                          <th className="border p-2 text-left">Botella</th>
                                          <th className="border p-2 text-center">APTO</th>
                                        </tr>
                                      </thead>
                                      <tbody className="bg-white">
                                        {item.calibration_data.map((sensor, idx) => (
                                          <tr key={idx}>
                                            <td className="border p-2">{sensor.sensor}</td>
                                            <td className="border p-2">{sensor.pre_alarm}</td>
                                            <td className="border p-2">{sensor.alarm}</td>
                                            <td className="border p-2">{sensor.calibration_value}</td>
                                            <td className="border p-2">{sensor.valor_zero}</td>
                                            <td className="border p-2">{sensor.valor_span}</td>
                                            <td className="border p-2">{sensor.calibration_bottle}</td>
                                            <td className="border p-2 text-center">
                                              <span className={`px-2 py-1 rounded text-xs ${sensor.approved ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                                {sensor.approved ? 'SÍ' : 'NO'}
                                              </span>
                                            </td>
                                          </tr>
                                        ))}
                                      </tbody>
                                    </table>
                                  </div>
                                ) : (
                                  <p className="text-gray-500 text-sm">No hay datos de calibración</p>
                                )}
                              </div>

                              {/* Repuestos Utilizados */}
                              <div>
                                <h3 className="font-bold text-sm mb-2">Repuestos Utilizados</h3>
                                {item.spare_parts && item.spare_parts.length > 0 ? (
                                  <div className="overflow-x-auto">
                                    <table className="w-full text-sm border">
                                      <thead className="bg-gray-100">
                                        <tr>
                                          <th className="border p-2 text-left">Descripción</th>
                                          <th className="border p-2 text-left">Referencia</th>
                                          <th className="border p-2 text-center">Garantía</th>
                                        </tr>
                                      </thead>
                                      <tbody className="bg-white">
                                        {item.spare_parts.map((part, idx) => (
                                          <tr key={idx}>
                                            <td className="border p-2">{part.descripcion}</td>
                                            <td className="border p-2">{part.referencia}</td>
                                            <td className="border p-2 text-center">
                                              {part.garantia && (
                                                <span className="px-2 py-1 rounded text-xs bg-blue-100 text-blue-800">
                                                  GARANTÍA
                                                </span>
                                              )}
                                            </td>
                                          </tr>
                                        ))}
                                      </tbody>
                                    </table>
                                  </div>
                                ) : (
                                  <div className="bg-white border rounded p-3">
                                    <p className="text-sm text-gray-500">Ninguno</p>
                                  </div>
                                )}
                              </div>

                              {/* Observaciones */}
                              {item.observations && (
                                <div>
                                  <h3 className="font-bold text-sm mb-2">Observaciones</h3>
                                  <div className="bg-white border rounded p-3">
                                    <p className="text-sm">{item.observations}</p>
                                  </div>
                                </div>
                              )}
                            </div>
                          </td>
                        </tr>
                      )}
                    </>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {equipment.length > 0 && (
          <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
            <h2 className="text-xl font-bold mb-6" style={{ fontFamily: 'Space Grotesk' }}>Datos de Entrega</h2>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="delivery_note">Número de Albarán</Label>
                  <Input
                    id="delivery_note"
                    data-testid="delivery-note-input"
                    value={deliveryNote}
                    onChange={(e) => setDeliveryNote(e.target.value)}
                    required
                    className="mt-2"
                  />
                </div>

                <div>
                  <Label htmlFor="delivery_location">Lugar de Entrega</Label>
                  <Input
                    id="delivery_location"
                    data-testid="delivery-location-input"
                    value={deliveryLocation}
                    onChange={(e) => setDeliveryLocation(e.target.value)}
                    required
                    className="mt-2"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="delivery_date">Fecha de Entrega</Label>
                <Input
                  id="delivery_date"
                  data-testid="delivery-date-input"
                  type="date"
                  value={deliveryDate}
                  onChange={(e) => setDeliveryDate(e.target.value)}
                  required
                  className="mt-2"
                />
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-800">
                  <strong>Equipos seleccionados:</strong> {selectedEquipment.length}
                </p>
              </div>

              <Button
                type="submit"
                disabled={loading || selectedEquipment.length === 0}
                className="w-full py-6 text-lg font-semibold bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700"
                data-testid="deliver-equipment-button"
              >
                {loading ? 'Procesando...' : 'Registrar Entrega'}
              </Button>
            </form>
          </div>
        )}
      </div>
    </Layout>
  );
}