import { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { toast } from "sonner";
import Layout from "../components/Layout";
import { FileInput, Plus } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const getAuthHeaders = () => ({
  headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
});

export default function EquipmentEntry() {
  const [brands, setBrands] = useState([]);
  const [models, setModels] = useState([]);
  const [clients, setClients] = useState([]);
  const [formData, setFormData] = useState({
    brand: "",
    model: "",
    client_name: "",
    client_cif: "",
    client_departamento: "",
    serial_number: "",
    observations: "",
    entry_date: new Date().toISOString().split('T')[0]
  });
  const [newBrand, setNewBrand] = useState("");
  const [newModel, setNewModel] = useState("");
  const [newClient, setNewClient] = useState({ name: "", cif: "", departamento: "" });
  const [loading, setLoading] = useState(false);
  const [brandDialogOpen, setBrandDialogOpen] = useState(false);
  const [modelDialogOpen, setModelDialogOpen] = useState(false);
  const [clientDialogOpen, setClientDialogOpen] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [brandsRes, modelsRes, clientsRes] = await Promise.all([
        axios.get(`${API}/brands`, getAuthHeaders()),
        axios.get(`${API}/models`, getAuthHeaders()),
        axios.get(`${API}/clients`, getAuthHeaders())
      ]);
      setBrands(brandsRes.data);
      setModels(modelsRes.data);
      setClients(clientsRes.data);
    } catch (error) {
      toast.error('Error al cargar datos');
    }
  };

  const handleAddBrand = async () => {
    if (!newBrand.trim()) return;
    
    // Cerrar el modal primero
    setBrandDialogOpen(false);
    
    // Delay más largo para asegurar que el modal y overlay se cierran completamente
    setTimeout(async () => {
      try {
        await axios.post(`${API}/brands`, { name: newBrand }, getAuthHeaders());
        toast.success('Marca añadida');
        setNewBrand("");
        loadData();
      } catch (error) {
        toast.error(error.response?.data?.detail || 'Error al añadir marca');
      }
    }, 300);
  };

  const handleAddModel = async () => {
    if (!newModel.trim()) return;
    
    // Cerrar el modal primero
    setModelDialogOpen(false);
    
    // Delay más largo para asegurar que el modal y overlay se cierran completamente
    setTimeout(async () => {
      try {
        await axios.post(`${API}/models`, { name: newModel }, getAuthHeaders());
        toast.success('Modelo añadido');
        setNewModel("");
        loadData();
      } catch (error) {
        toast.error(error.response?.data?.detail || 'Error al añadir modelo');
      }
    }, 300);
  };

  const handleAddClient = async () => {
    if (!newClient.name.trim() || !newClient.cif.trim()) return;
    
    // Cerrar el modal primero
    setClientDialogOpen(false);
    
    // Delay más largo para asegurar que el modal y overlay se cierran completamente
    setTimeout(async () => {
      try {
        await axios.post(`${API}/clients`, newClient, getAuthHeaders());
        toast.success('Cliente añadido');
        setNewClient({ name: "", cif: "" });
        loadData();
      } catch (error) {
        toast.error(error.response?.data?.detail || 'Error al añadir cliente');
      }
    }, 300);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post(`${API}/equipment`, formData, getAuthHeaders());
      toast.success('Equipo registrado correctamente');
      setFormData({
        brand: "",
        model: "",
        client_name: "",
        client_cif: "",
        serial_number: "",
        observations: "",
        entry_date: new Date().toISOString().split('T')[0]
      });
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al registrar equipo');
    } finally {
      setLoading(false);
    }
  };

  const handleClientSelect = (clientId) => {
    const client = clients.find(c => c.id === clientId);
    if (client) {
      setFormData({
        ...formData,
        client_name: client.name,
        client_cif: client.cif
      });
    }
  };

  return (
    <Layout>
      <div className="max-w-4xl mx-auto" data-testid="equipment-entry-page">
        <div className="flex items-center gap-3 mb-8">
          <FileInput className="w-8 h-8 text-blue-600" />
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-800" style={{ fontFamily: 'Space Grotesk' }}>
            Entrada de Equipos en Taller
          </h1>
        </div>

        <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Brand */}
              <div>
                <Label htmlFor="brand">Marca del Equipo</Label>
                <div className="flex gap-2 mt-2">
                  <Select value={formData.brand} onValueChange={(value) => setFormData({...formData, brand: value})} required>
                    <SelectTrigger data-testid="brand-select">
                      <SelectValue placeholder="Seleccionar marca" />
                    </SelectTrigger>
                    <SelectContent>
                      {brands.map(b => (
                        <SelectItem key={b.id} value={b.name}>{b.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Dialog open={brandDialogOpen} onOpenChange={setBrandDialogOpen}>
                    <DialogTrigger asChild>
                      <Button type="button" variant="outline" size="icon" data-testid="add-brand-button">
                        <Plus className="w-4 h-4" />
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Añadir Nueva Marca</DialogTitle>
                      </DialogHeader>
                      <div className="space-y-4">
                        <Input
                          placeholder="Nombre de la marca"
                          value={newBrand}
                          onChange={(e) => setNewBrand(e.target.value)}
                          data-testid="new-brand-input"
                        />
                        <Button onClick={handleAddBrand} className="w-full" data-testid="save-brand-button">Guardar</Button>
                      </div>
                    </DialogContent>
                  </Dialog>
                </div>
              </div>

              {/* Model */}
              <div>
                <Label htmlFor="model">Modelo</Label>
                <div className="flex gap-2 mt-2">
                  <Select value={formData.model} onValueChange={(value) => setFormData({...formData, model: value})} required>
                    <SelectTrigger data-testid="model-select">
                      <SelectValue placeholder="Seleccionar modelo" />
                    </SelectTrigger>
                    <SelectContent>
                      {models.map(m => (
                        <SelectItem key={m.id} value={m.name}>{m.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Dialog open={modelDialogOpen} onOpenChange={setModelDialogOpen}>
                    <DialogTrigger asChild>
                      <Button type="button" variant="outline" size="icon" data-testid="add-model-button">
                        <Plus className="w-4 h-4" />
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Añadir Nuevo Modelo</DialogTitle>
                      </DialogHeader>
                      <div className="space-y-4">
                        <Input
                          placeholder="Nombre del modelo"
                          value={newModel}
                          onChange={(e) => setNewModel(e.target.value)}
                          data-testid="new-model-input"
                        />
                        <Button onClick={handleAddModel} className="w-full" data-testid="save-model-button">Guardar</Button>
                      </div>
                    </DialogContent>
                  </Dialog>
                </div>
              </div>
            </div>

            {/* Client */}
            <div>
              <Label htmlFor="client">Cliente</Label>
              <div className="flex gap-2 mt-2">
                <Select onValueChange={handleClientSelect} required>
                  <SelectTrigger data-testid="client-select">
                    <SelectValue placeholder="Seleccionar cliente" />
                  </SelectTrigger>
                  <SelectContent>
                    {clients.map(c => (
                      <SelectItem key={c.id} value={c.id}>{c.name} - {c.cif}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Dialog open={clientDialogOpen} onOpenChange={setClientDialogOpen}>
                  <DialogTrigger asChild>
                    <Button type="button" variant="outline" size="icon" data-testid="add-client-button">
                      <Plus className="w-4 h-4" />
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Añadir Nuevo Cliente</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4">
                      <Input
                        placeholder="Nombre del cliente"
                        value={newClient.name}
                        onChange={(e) => setNewClient({...newClient, name: e.target.value})}
                        data-testid="new-client-name-input"
                      />
                      <Input
                        placeholder="CIF"
                        value={newClient.cif}
                        onChange={(e) => setNewClient({...newClient, cif: e.target.value})}
                        data-testid="new-client-cif-input"
                      />
                      <Button onClick={handleAddClient} className="w-full" data-testid="save-client-button">Guardar</Button>
                    </div>
                  </DialogContent>
                </Dialog>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Serial Number */}
              <div>
                <Label htmlFor="serial_number">Número de Serie</Label>
                <Input
                  id="serial_number"
                  data-testid="serial-number-input"
                  value={formData.serial_number}
                  onChange={(e) => setFormData({...formData, serial_number: e.target.value})}
                  required
                  className="mt-2"
                />
              </div>

              {/* Entry Date */}
              <div>
                <Label htmlFor="entry_date">Fecha de Entrada</Label>
                <Input
                  id="entry_date"
                  data-testid="entry-date-input"
                  type="date"
                  value={formData.entry_date}
                  onChange={(e) => setFormData({...formData, entry_date: e.target.value})}
                  required
                  className="mt-2"
                />
              </div>
            </div>

            {/* Observations */}
            <div>
              <Label htmlFor="observations">Observaciones</Label>
              <Textarea
                id="observations"
                data-testid="observations-input"
                value={formData.observations}
                onChange={(e) => setFormData({...formData, observations: e.target.value})}
                rows={4}
                className="mt-2"
              />
            </div>

            <Button 
              type="submit" 
              disabled={loading}
              className="w-full py-6 text-lg font-semibold bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700"
              data-testid="submit-equipment-button"
            >
              {loading ? 'Guardando...' : 'Registrar Equipo'}
            </Button>
          </form>
        </div>
      </div>
    </Layout>
  );
}