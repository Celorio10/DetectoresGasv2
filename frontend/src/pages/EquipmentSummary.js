import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import Layout from "../components/Layout";
import { BarChart3 } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const getAuthHeaders = () => ({
  headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
});

function calculateDaysInWorkshop(entryDate, exitDate) {
  const entry = new Date(entryDate);
  const exit = new Date(exitDate);
  const diffTime = Math.abs(exit - entry);
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return diffDays;
}

export default function EquipmentSummary() {
  const [equipment, setEquipment] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadEquipment();
  }, []);

  const loadEquipment = async () => {
    try {
      const response = await axios.get(`${API}/equipment/delivered`, getAuthHeaders());
      setEquipment(response.data);
    } catch (error) {
      toast.error('Error al cargar equipos');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex justify-center items-center min-h-screen">
          <p className="text-lg">Cargando...</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto" data-testid="equipment-summary-page">
        <div className="flex items-center gap-3 mb-8">
          <BarChart3 className="w-8 h-8 text-purple-600" />
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-800" style={{ fontFamily: 'Space Grotesk' }}>
            Resumen de Equipos Revisados
          </h1>
        </div>

        <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
          {equipment.length === 0 ? (
            <p className="text-gray-600 text-center py-8" data-testid="no-delivered-equipment">No hay equipos entregados aún</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-gray-50">
                    <th className="text-left p-3 text-sm font-semibold">Marca</th>
                    <th className="text-left p-3 text-sm font-semibold">Modelo</th>
                    <th className="text-left p-3 text-sm font-semibold">Nº Serie</th>
                    <th className="text-left p-3 text-sm font-semibold">Cliente</th>
                    <th className="text-left p-3 text-sm font-semibold">Fecha Entrada</th>
                    <th className="text-left p-3 text-sm font-semibold">Fecha Salida</th>
                    <th className="text-left p-3 text-sm font-semibold">Tiempo en Taller</th>
                    <th className="text-left p-3 text-sm font-semibold">Albarán</th>
                    <th className="text-left p-3 text-sm font-semibold">Lugar Entrega</th>
                  </tr>
                </thead>
                <tbody>
                  {equipment.map((item) => {
                    const daysInWorkshop = calculateDaysInWorkshop(item.entry_date, item.delivery_date);
                    return (
                      <tr key={item.serial_number} className="border-b hover:bg-gray-50">
                        <td className="p-3" data-testid={`brand-${item.serial_number}`}>{item.brand}</td>
                        <td className="p-3" data-testid={`model-${item.serial_number}`}>{item.model}</td>
                        <td className="p-3 font-semibold" data-testid={`serial-${item.serial_number}`}>{item.serial_number}</td>
                        <td className="p-3">{item.client_name}</td>
                        <td className="p-3">{item.entry_date}</td>
                        <td className="p-3">{item.delivery_date}</td>
                        <td className="p-3">
                          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold bg-purple-100 text-purple-800" data-testid={`days-${item.serial_number}`}>
                            {daysInWorkshop} días
                          </span>
                        </td>
                        <td className="p-3">{item.delivery_note}</td>
                        <td className="p-3">{item.delivery_location}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {equipment.length > 0 && (
          <div className="mt-6 bg-gradient-to-r from-purple-50 to-blue-50 rounded-2xl shadow-lg p-6 border border-purple-100">
            <h3 className="text-lg font-bold mb-2" style={{ fontFamily: 'Space Grotesk' }}>Estadísticas</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white rounded-lg p-4 shadow">
                <p className="text-sm text-gray-600">Total Equipos Entregados</p>
                <p className="text-2xl font-bold text-purple-600" data-testid="total-equipment">{equipment.length}</p>
              </div>
              <div className="bg-white rounded-lg p-4 shadow">
                <p className="text-sm text-gray-600">Tiempo Promedio</p>
                <p className="text-2xl font-bold text-blue-600" data-testid="average-days">
                  {Math.round(
                    equipment.reduce((acc, item) => 
                      acc + calculateDaysInWorkshop(item.entry_date, item.delivery_date), 0
                    ) / equipment.length
                  )} días
                </p>
              </div>
              <div className="bg-white rounded-lg p-4 shadow">
                <p className="text-sm text-gray-600">Clientes Atendidos</p>
                <p className="text-2xl font-bold text-green-600" data-testid="unique-clients">
                  {new Set(equipment.map(e => e.client_name)).size}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}