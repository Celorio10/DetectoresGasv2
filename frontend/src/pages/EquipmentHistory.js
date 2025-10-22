import { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import Layout from "../components/Layout";
import { History, Download, ChevronDown, ChevronUp, Search, X } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const getAuthHeaders = () => ({
  headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
});

export default function EquipmentHistory() {
  const [equipments, setEquipments] = useState([]);
  const [expandedEquipment, setExpandedEquipment] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // Filtros de búsqueda
  const [filters, setFilters] = useState({
    cliente: "",
    modelo: "",
    serial: ""
  });

  useEffect(() => {
    handleSearch();
  }, []);

  const handleSearch = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.cliente) params.append('cliente', filters.cliente);
      if (filters.modelo) params.append('modelo', filters.modelo);
      if (filters.serial) params.append('serial', filters.serial);
      
      const response = await axios.get(
        `${API}/calibration-history/search?${params.toString()}`,
        getAuthHeaders()
      );
      
      setEquipments(response.data);
      if (response.data.length === 0) {
        toast.info('No se encontraron equipos con los filtros especificados');
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al buscar historial');
      setEquipments([]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearFilters = () => {
    setFilters({ cliente: "", modelo: "", serial: "" });
    // Recargar todo después de limpiar
    setTimeout(() => {
      handleSearch();
    }, 100);
  };

  const handleToggleExpand = (serialNumber) => {
    if (expandedEquipment === serialNumber) {
      setExpandedEquipment(null);
    } else {
      setExpandedEquipment(serialNumber);
    }
  };

  const handleDownloadCertificate = async (historyId, serialNumber, calibrationDate) => {
    try {
      const response = await axios.get(
        `${API}/equipment/history/${historyId}/certificate`,
        {
          ...getAuthHeaders(),
          responseType: 'blob'
        }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Certificado_${serialNumber}_${calibrationDate}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success('Certificado descargado');
    } catch (error) {
      console.error('Error descargando certificado:', error);
      toast.error('Error al descargar el certificado');
    }
  };

  const getEstadoColor = (calibrationData) => {
    if (!calibrationData || calibrationData.length === 0) return 'bg-gray-100 text-gray-800';
    const allApproved = calibrationData.every(sensor => sensor.approved);
    return allApproved ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800';
  };

  const getEstadoText = (calibrationData) => {
    if (!calibrationData || calibrationData.length === 0) return 'N/A';
    const allApproved = calibrationData.every(sensor => sensor.approved);
    return allApproved ? 'APTO' : 'REVISIÓN';
  };

  return (
    <Layout>
      <div className="max-w-7xl mx-auto" data-testid="equipment-history-page">
        <div className="flex items-center gap-3 mb-8">
          <History className="w-8 h-8 text-purple-600" />
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-800" style={{ fontFamily: 'Space Grotesk' }}>
            Historial de Equipos
          </h1>
        </div>

        {/* Buscador */}
        <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100 mb-6">
          <h2 className="text-xl font-bold mb-4" style={{ fontFamily: 'Space Grotesk' }}>
            🔍 Buscador de Equipos
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div>
              <Label>Cliente</Label>
              <Input
                placeholder="Buscar por cliente..."
                value={filters.cliente}
                onChange={(e) => setFilters({...filters, cliente: e.target.value})}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
            </div>
            <div>
              <Label>Modelo</Label>
              <Input
                placeholder="Buscar por modelo..."
                value={filters.modelo}
                onChange={(e) => setFilters({...filters, modelo: e.target.value})}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
            </div>
            <div>
              <Label>Nº de Serie</Label>
              <Input
                placeholder="Buscar por número de serie..."
                value={filters.serial}
                onChange={(e) => setFilters({...filters, serial: e.target.value})}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
            </div>
          </div>
          <div className="flex gap-2">
            <Button onClick={handleSearch} className="bg-purple-600 hover:bg-purple-700">
              <Search className="w-4 h-4 mr-2" />
              Buscar
            </Button>
            <Button onClick={handleClearFilters} variant="outline">
              <X className="w-4 h-4 mr-2" />
              Limpiar
            </Button>
          </div>
        </div>

        {loading ? (
          <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100 text-center">
            <p className="text-gray-600">Buscando equipos...</p>
          </div>
        ) : equipments.length > 0 ? (
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
            <h2 className="text-xl font-bold mb-4" style={{ fontFamily: 'Space Grotesk' }}>
              Resultados de Búsqueda
            </h2>
            <p className="text-sm text-gray-600 mb-4">
              Total de equipos encontrados: {equipments.length}
            </p>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-gray-50">
                    <th className="text-left p-3 text-sm font-semibold w-16"></th>
                    <th className="text-left p-3 text-sm font-semibold">Nº Serie</th>
                    <th className="text-left p-3 text-sm font-semibold">Marca</th>
                    <th className="text-left p-3 text-sm font-semibold">Modelo</th>
                    <th className="text-left p-3 text-sm font-semibold">Cliente</th>
                    <th className="text-left p-3 text-sm font-semibold">Departamento</th>
                  </tr>
                </thead>
                <tbody>
                  {equipments.map((equipment) => (
                    <>
                      {/* Fila principal del equipo */}
                      <tr 
                        key={equipment.serial_number} 
                        className="border-b hover:bg-gray-50 transition-colors cursor-pointer"
                        onClick={() => handleToggleExpand(equipment.serial_number)}
                      >
                        <td className="p-3">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleToggleExpand(equipment.serial_number);
                            }}
                          >
                            {expandedEquipment === equipment.serial_number ? (
                              <ChevronUp className="w-4 h-4" />
                            ) : (
                              <ChevronDown className="w-4 h-4" />
                            )}
                          </Button>
                        </td>
                        <td className="p-3 font-semibold text-blue-600">{equipment.serial_number}</td>
                        <td className="p-3">{equipment.brand}</td>
                        <td className="p-3">{equipment.model}</td>
                        <td className="p-3">{equipment.client_name}</td>
                        <td className="p-3">{equipment.client_departamento || 'N/A'}</td>
                      </tr>
                      
                      {/* Fila con fecha de última calibración */}
                      <tr className="border-b bg-gray-50">
                        <td></td>
                        <td colSpan="5" className="p-2 text-sm text-gray-600">
                          📅 Última calibración: <span className="font-semibold">{equipment.last_calibration_date}</span>
                          <span className="ml-4">
                            ({equipment.calibrations.length} calibración{equipment.calibrations.length !== 1 ? 'es' : ''} registrada{equipment.calibrations.length !== 1 ? 's' : ''})
                          </span>
                        </td>
                      </tr>

                      {/* Historial de calibraciones expandido */}
                      {expandedEquipment === equipment.serial_number && (
                        <tr className="bg-blue-50">
                          <td></td>
                          <td colSpan="5" className="p-4">
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
                                              {part.garantia ? (
                                                <span className="px-2 py-1 rounded text-xs bg-blue-100 text-blue-800">
                                                  SÍ
                                                </span>
                                              ) : (
                                                <span className="text-gray-500">NO</span>
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
          </div>
        ) : (
          <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100 text-center">
            <History className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-600" data-testid="no-history">
              No hay historial de calibraciones aún
            </p>
          </div>
        )}
      </div>
    </Layout>
  );
}
