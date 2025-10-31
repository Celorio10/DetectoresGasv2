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
  
  // Estado para búsqueda de equipo en catálogo maestro
  const [searchSerial, setSearchSerial] = useState("");
  const [equipmentFromCatalog, setEquipmentFromCatalog] = useState(null);
  const [equipmentNotFound, setEquipmentNotFound] = useState(false);
  const [showFullForm, setShowFullForm] = useState(false);
  
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
  const [newClient, setNewClient] = useState({ name: "", cif: "", departamentos: [] });
  const [newDepartamento, setNewDepartamento] = useState("");
  const [selectedClientDepartamentos, setSelectedClientDepartamentos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [brandDialogOpen, setBrandDialogOpen] = useState(false);
  const [modelDialogOpen, setModelDialogOpen] = useState(false);
  const [clientDialogOpen, setClientDialogOpen] = useState(false);
  const [catalogDialogOpen, setCatalogDialogOpen] = useState(false);

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
    if (!newClient.name.trim() || !newClient.cif.trim() || newClient.departamentos.length === 0) {
      toast.error('Debes agregar al menos un departamento');
      return;
    }
    
    // Cerrar el modal primero
    setClientDialogOpen(false);
    
    // Delay más largo para asegurar que el modal y overlay se cierran completamente
    setTimeout(async () => {
      try {
        await axios.post(`${API}/clients`, newClient, getAuthHeaders());
        toast.success('Cliente añadido');
        setNewClient({ name: "", cif: "", departamentos: [] });
        setNewDepartamento("");
        loadData();
      } catch (error) {
        toast.error(error.response?.data?.detail || 'Error al añadir cliente');
      }
    }, 300);
  };

  const handleAddDepartamentoToNewClient = () => {
    if (newDepartamento.trim()) {
      setNewClient({
        ...newClient,
        departamentos: [...newClient.departamentos, newDepartamento.trim()]
      });
      setNewDepartamento("");
    }
  };

  const handleRemoveDepartamentoFromNewClient = (index) => {
    setNewClient({
      ...newClient,
      departamentos: newClient.departamentos.filter((_, i) => i !== index)
    });
  };

  const handleSearchEquipment = async () => {
    if (!searchSerial.trim()) {
      toast.error('Introduce un número de serie');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.get(
        `${API}/equipment-master/${searchSerial}`,
        getAuthHeaders()
      );
      
      if (response.data) {
        // Equipo encontrado en catálogo maestro
        setEquipmentFromCatalog(response.data);
        setEquipmentNotFound(false);
        setFormData({
          ...formData,
          serial_number: response.data.serial_number,
          brand: response.data.brand,
          model: response.data.model,
          client_name: response.data.current_client_name,
          client_cif: response.data.current_client_cif,
          client_departamento: response.data.current_client_departamento || "",
          entry_date: new Date().toISOString().split('T')[0]
        });
        toast.success('Equipo encontrado en catálogo');
      } else {
        // Equipo no encontrado
        setEquipmentFromCatalog(null);
        setEquipmentNotFound(true);
        setFormData({
          ...formData,
          serial_number: searchSerial,
          entry_date: new Date().toISOString().split('T')[0]
        });
      }
    } catch (error) {
      // Equipo no encontrado
      setEquipmentFromCatalog(null);
      setEquipmentNotFound(true);
      setFormData({
        ...formData,
        serial_number: searchSerial,
        entry_date: new Date().toISOString().split('T')[0]
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRegisterNewEquipment = () => {
    setShowFullForm(true);
    setCatalogDialogOpen(true);
  };

  const handleResetSearch = () => {
    setSearchSerial("");
    setEquipmentFromCatalog(null);
    setEquipmentNotFound(false);
    setShowFullForm(false);
    setFormData({
      brand: "",
      model: "",
      client_name: "",
      client_cif: "",
      client_departamento: "",
      serial_number: "",
      observations: "",
      entry_date: new Date().toISOString().split('T')[0]
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.serial_number || !formData.brand || !formData.model) {
      toast.error('Completa los campos obligatorios');
      return;
    }

    setLoading(true);
    try {
      // Si el equipo NO está en el catálogo maestro, primero lo registramos allí
      if (equipmentNotFound || showFullForm) {
        try {
          await axios.post(`${API}/equipment-master`, {
            serial_number: formData.serial_number,
            brand: formData.brand,
            model: formData.model,
            current_client_name: formData.client_name,
            current_client_cif: formData.client_cif,
            current_client_departamento: formData.client_departamento,
            default_sensors: [],
            general_observations: ""
          }, getAuthHeaders());
          toast.success('Equipo registrado en catálogo maestro');
        } catch (error) {
          // Si ya existe, continuamos (puede haber sido creado entre la búsqueda y el submit)
          if (!error.response?.data?.detail?.includes('already exists')) {
            throw error;
          }
        }
      }

      // Registrar entrada al taller
      await axios.post(`${API}/equipment`, formData, getAuthHeaders());
      toast.success('Entrada al taller registrada correctamente');
      
      // Reset
      handleResetSearch();
      
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al registrar entrada');
    } finally {
      setLoading(false);
    }
  };

  const handleClientSelect = (clientId) => {
    const client = clients.find(c => c.id === clientId);
    if (client) {
      setSelectedClientDepartamentos(client.departamentos || []);
      setFormData({
        ...formData,
        client_name: client.name,
        client_cif: client.cif,
        client_departamento: "" // Reset department, user will select from dropdown
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

        {/* Buscador de equipo */}
        {!equipmentFromCatalog && !equipmentNotFound && !showFullForm && (
          <div className="bg-white rounded-2xl shadow-lg p-6 sm:p-8 border border-gray-100 mb-6">
            <h2 className="text-xl font-bold mb-4" style={{ fontFamily: 'Space Grotesk' }}>
              🔍 Buscar Equipo por Número de Serie
            </h2>
            <p className="text-sm text-gray-600 mb-4">
              Introduce el número de serie del equipo. Si está registrado en el catálogo, se cargarán automáticamente sus datos.
            </p>
            <div className="flex gap-3">
              <Input
                placeholder="Número de Serie..."
                value={searchSerial}
                onChange={(e) => setSearchSerial(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleSearchEquipment())}
                className="flex-1"
              />
              <Button 
                onClick={handleSearchEquipment} 
                disabled={loading}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {loading ? 'Buscando...' : 'Buscar'}
              </Button>
            </div>
          </div>
        )}

        {/* Equipo encontrado - Formulario simplificado */}
        {equipmentFromCatalog && (
          <div className="bg-white rounded-2xl shadow-lg p-6 sm:p-8 border border-gray-100">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-green-600" style={{ fontFamily: 'Space Grotesk' }}>
                ✅ Equipo Encontrado en Catálogo
              </h2>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={handleResetSearch}
              >
                Buscar Otro
              </Button>
            </div>

            {/* Datos del equipo (solo lectura) */}
            <div className="bg-blue-50 rounded-lg p-4 mb-6 border border-blue-200">
              <h3 className="font-bold mb-3">Datos del Equipo</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                <div>
                  <span className="font-semibold">Número de Serie:</span> {equipmentFromCatalog.serial_number}
                </div>
                <div>
                  <span className="font-semibold">Marca:</span> {equipmentFromCatalog.brand}
                </div>
                <div>
                  <span className="font-semibold">Modelo:</span> {equipmentFromCatalog.model}
                </div>
                <div>
                  <span className="font-semibold">Cliente:</span> {equipmentFromCatalog.current_client_name}
                </div>
                <div>
                  <span className="font-semibold">Departamento:</span> {equipmentFromCatalog.current_client_departamento || 'N/A'}
                </div>
                <div>
                  <span className="font-semibold">Sensores predefinidos:</span> {equipmentFromCatalog.default_sensors?.length || 0}
                </div>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Solo campos editables */}
              <div>
                <Label>Fecha de Entrada *</Label>
                <Input
                  type="date"
                  value={formData.entry_date}
                  onChange={(e) => setFormData({...formData, entry_date: e.target.value})}
                  required
                />
              </div>

              <div>
                <Label>Observaciones de esta Entrada</Label>
                <Textarea
                  value={formData.observations}
                  onChange={(e) => setFormData({...formData, observations: e.target.value})}
                  rows={3}
                  placeholder="Observaciones específicas para esta entrada al taller..."
                />
              </div>

              <div className="flex gap-3">
                <Button 
                  type="submit" 
                  disabled={loading}
                  className="flex-1 bg-blue-600 hover:bg-blue-700"
                >
                  {loading ? 'Registrando...' : 'Registrar Entrada al Taller'}
                </Button>
                <Button 
                  type="button" 
                  variant="outline"
                  onClick={() => window.location.href = '/catalogo'}
                >
                  Editar en Catálogo
                </Button>
              </div>
            </form>
          </div>
        )}

        {/* Equipo NO encontrado */}
        {equipmentNotFound && !showFullForm && (
          <div className="bg-white rounded-2xl shadow-lg p-6 sm:p-8 border border-gray-100">
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">⚠️</span>
              </div>
              <h2 className="text-xl font-bold mb-2">Equipo No Encontrado</h2>
              <p className="text-gray-600 mb-4">
                El equipo con número de serie <strong>{searchSerial}</strong> no está registrado en el catálogo maestro.
              </p>
              <div className="flex gap-3 justify-center">
                <Button 
                  onClick={handleRegisterNewEquipment}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Registrar Nuevo Equipo
                </Button>
                <Button variant="outline" onClick={handleResetSearch}>
                  Buscar Otro
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Formulario completo para equipo nuevo */}
        {showFullForm && (
          <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-lg p-6 sm:p-8 border border-gray-100">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold" style={{ fontFamily: 'Space Grotesk' }}>
                Registrar Nuevo Equipo
              </h2>
              <Button 
                type="button"
                variant="outline" 
                size="sm" 
                onClick={handleResetSearch}
              >
                Cancelar
              </Button>
            </div>
            <div className="space-y-6">
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
                      {brands.filter(b => b.name && b.name.trim() !== "").map(b => (
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
                      {models.filter(m => m.name && m.name.trim() !== "").map(m => (
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
                      <div>
                        <Label>Departamentos</Label>
                        <div className="flex gap-2 mt-2">
                          <Input
                            placeholder="Agregar departamento"
                            value={newDepartamento}
                            onChange={(e) => setNewDepartamento(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddDepartamentoToNewClient())}
                            data-testid="new-departamento-input"
                          />
                          <Button type="button" onClick={handleAddDepartamentoToNewClient} size="icon" variant="outline">
                            <Plus className="w-4 h-4" />
                          </Button>
                        </div>
                        {newClient.departamentos.length > 0 && (
                          <div className="mt-2 space-y-1">
                            {newClient.departamentos.map((dep, index) => (
                              <div key={index} className="flex items-center justify-between bg-gray-100 px-3 py-2 rounded">
                                <span className="text-sm">{dep}</span>
                                <Button 
                                  type="button" 
                                  size="sm" 
                                  variant="ghost" 
                                  onClick={() => handleRemoveDepartamentoFromNewClient(index)}
                                  className="h-6 px-2"
                                >
                                  ×
                                </Button>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                      <Button onClick={handleAddClient} className="w-full" data-testid="save-client-button">Guardar</Button>
                    </div>
                  </DialogContent>
                </Dialog>
              </div>
            </div>

            {/* Department */}
            {selectedClientDepartamentos.length > 0 && (
              <div>
                <Label htmlFor="departamento">Departamento</Label>
                <div className="mt-2">
                  <Select 
                    value={formData.client_departamento} 
                    onValueChange={(value) => setFormData({...formData, client_departamento: value})} 
                    required
                  >
                    <SelectTrigger data-testid="department-select">
                      <SelectValue placeholder="Seleccionar departamento" />
                    </SelectTrigger>
                    <SelectContent>
                      {selectedClientDepartamentos.map((dep, index) => (
                        <SelectItem key={index} value={dep}>{dep}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            )}

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
                  placeholder="Ingrese número de serie"
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
            </div>
          </form>
        )}
      </div>
    </Layout>
  );
}