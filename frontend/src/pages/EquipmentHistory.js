import { useState } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import Layout from "../components/Layout";
import { History, Search, Download } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const getAuthHeaders = () => ({
  headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
});

export default function EquipmentHistory() {
  const [searchSerial, setSearchSerial] = useState("");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!searchSerial.trim()) {
      toast.error('Introduce un número de serie');
      return;
    }
    
    setLoading(true);
    try {
      const response = await axios.get(`${API}/equipment/${searchSerial}/history`, getAuthHeaders());
      if (response.data.length === 0) {
        toast.info('No se encontró historial para este equipo');
      } else {
        toast.success(`Se encontraron ${response.data.length} calibraciones`);
      }
      setHistory(response.data);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al buscar historial');
      setHistory([]);
    } finally {
      setLoading(false);
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
      
      // Crear un enlace temporal para descargar el PDF
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

        {/* Search Section */}
        <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100 mb-6">
          <Label htmlFor="search">Buscar Historial por Número de Serie</Label>
          <div className="flex gap-2 mt-2">
            <Input
              id="search"
              data-testid="search-serial-input"
              placeholder="Introduce el número de serie"
              value={searchSerial}
              onChange={(e) => setSearchSerial(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
            <Button onClick={handleSearch} disabled={loading} data-testid="search-button">
              <Search className="w-4 h-4 mr-2" />
              {loading ? 'Buscando...' : 'Buscar'}
            </Button>
          </div>
        </div>

        {/* History Table */}
        {history.length > 0 && (
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
            <h2 className="text-xl font-bold mb-4" style={{ fontFamily: 'Space Grotesk' }}>
              Historial de Calibraciones - {searchSerial}
            </h2>
            <p className="text-sm text-gray-600 mb-4">
              Total de calibraciones: {history.length}
            </p>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-gray-50">
                    <th className="text-left p-3 text-sm font-semibold">Fecha Calibración</th>
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
                    <tr 
                      key={item.id} 
                      className="border-b hover:bg-gray-50 transition-colors"
                      data-testid={`history-row-${item.id}`}
                    >
                      <td className="p-3" data-testid={`history-date-${item.id}`}>
                        {item.calibration_date}
                      </td>
                      <td className="p-3">{item.brand}</td>
                      <td className="p-3">{item.model}</td>
                      <td className="p-3">{item.client_name}</td>
                      <td className="p-3 text-sm">{item.client_departamento || 'N/A'}</td>
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
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {history.length === 0 && searchSerial && !loading && (
          <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100 text-center">
            <p className="text-gray-600" data-testid="no-history">
              No se encontró historial para este número de serie
            </p>
          </div>
        )}

        {!searchSerial && (
          <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100 text-center">
            <History className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-600">
              Introduce un número de serie para ver el historial de calibraciones
            </p>
          </div>
        )}
      </div>
    </Layout>
  );
}
