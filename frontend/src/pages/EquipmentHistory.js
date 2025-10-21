import { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import Layout from "../components/Layout";
import { History, Download, ChevronDown, ChevronUp } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const getAuthHeaders = () => ({
  headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
});

export default function EquipmentHistory() {
  const [history, setHistory] = useState([]);
  const [expandedHistory, setExpandedHistory] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadAllHistory();
  }, []);

  const loadAllHistory = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/calibration-history/all`, getAuthHeaders());
      setHistory(response.data);
      if (response.data.length === 0) {
        toast.info('No hay historial de calibraciones aún');
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al cargar historial');
      setHistory([]);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleExpand = (historyId) => {
    if (expandedHistory === historyId) {
      setExpandedHistory(null);
    } else {
      setExpandedHistory(historyId);
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

        {loading ? (
          <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100 text-center">
            <p className="text-gray-600">Cargando historial...</p>
          </div>
        ) : history.length > 0 ? (
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
            <h2 className="text-xl font-bold mb-4" style={{ fontFamily: 'Space Grotesk' }}>
              Todos los Equipos Revisados
            </h2>
            <p className="text-sm text-gray-600 mb-4">
              Total de calibraciones: {history.length}
            </p>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-gray-50">
                    <th className="text-left p-3 text-sm font-semibold">Ver Detalles</th>
                    <th className="text-left p-3 text-sm font-semibold">Fecha Calibración</th>
                    <th className="text-left p-3 text-sm font-semibold">Nº Serie</th>
                    <th className="text-left p-3 text-sm font-semibold">Marca</th>
                    <th className="text-left p-3 text-sm font-semibold">Modelo</th>
                    <th className="text-left p-3 text-sm font-semibold">Cliente</th>
                    <th className="text-left p-3 text-sm font-semibold">Departamento</th>
                    <th className="text-left p-3 text-sm font-semibold">Técnico</th>
                    <th className="text-center p-3 text-sm font-semibold">Estado</th>
                    <th className="text-center p-3 text-sm font-semibold">Certificado</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((item) => (
                    <>
                      <tr 
                        key={item.id} 
                        className="border-b hover:bg-gray-50 transition-colors"
                        data-testid={`history-row-${item.id}`}
                      >
                        <td className="p-3">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleToggleExpand(item.id)}
                            data-testid={`expand-history-${item.id}`}
                          >
                            {expandedHistory === item.id ? (
                              <ChevronUp className="w-4 h-4" />
                            ) : (
                              <ChevronDown className="w-4 h-4" />
                            )}
                          </Button>
                        </td>
                        <td className="p-3" data-testid={`history-date-${item.id}`}>
                          {item.calibration_date}
                        </td>
                        <td className="p-3 font-semibold">{item.serial_number}</td>
                        <td className="p-3">{item.brand}</td>
                        <td className="p-3">{item.model}</td>
                        <td className="p-3">{item.client_name}</td>
                        <td className="p-3">{item.client_departamento || 'N/A'}</td>
                        <td className="p-3">{item.technician}</td>
                        <td className="p-3 text-center">
                          <span 
                            className={`px-3 py-1 rounded-full text-xs font-semibold ${getEstadoColor(item.calibration_data)}`}
                            data-testid={`history-status-${item.id}`}
                          >
                            {getEstadoText(item.calibration_data)}
                          </span>
                        </td>
                        <td className="p-3 text-center">
                          <Button 
                            size="sm" 
                            onClick={() => handleDownloadCertificate(item.id, item.serial_number, item.calibration_date)}
                            data-testid={`download-certificate-${item.id}`}
                            className="bg-purple-600 hover:bg-purple-700"
                          >
                            <Download className="w-4 h-4 mr-1" />
                            Descargar
                          </Button>
                        </td>
                      </tr>
                      {expandedHistory === item.id && (
                        <tr className="bg-blue-50">
                          <td colSpan="10" className="p-4">
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
