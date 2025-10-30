import React, { useState, useEffect } from 'react';
import Layout from '../Layout';
import { toast } from 'sonner';

const ClientManagement = () => {
  const [clients, setClients] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [currentClient, setCurrentClient] = useState({
    id: '',
    name: '',
    cif: '',
    departamentos: []
  });
  const [newDepartment, setNewDepartment] = useState('');
  const backendUrl = process.env.REACT_APP_BACKEND_URL || '';

  useEffect(() => {
    loadClients();
  }, []);

  const loadClients = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${backendUrl}/api/clients`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setClients(data);
      }
    } catch (error) {
      console.error('Error loading clients:', error);
      toast.error('Error al cargar clientes');
    }
  };

  const openCreateModal = () => {
    setCurrentClient({
      id: '',
      name: '',
      cif: '',
      departamentos: []
    });
    setIsEditing(false);
    setIsModalOpen(true);
  };

  const openEditModal = (client) => {
    setCurrentClient({...client});
    setIsEditing(true);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setCurrentClient({
      id: '',
      name: '',
      cif: '',
      departamentos: []
    });
    setNewDepartment('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!currentClient.name || !currentClient.cif) {
      toast.error('Por favor complete todos los campos obligatorios');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const url = isEditing 
        ? `${backendUrl}/api/clients/${currentClient.id}`
        : `${backendUrl}/api/clients`;
      
      const method = isEditing ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(currentClient)
      });

      if (response.ok) {
        toast.success(isEditing ? 'Cliente actualizado exitosamente' : 'Cliente creado exitosamente');
        loadClients();
        closeModal();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Error al guardar cliente');
      }
    } catch (error) {
      console.error('Error saving client:', error);
      toast.error('Error al guardar cliente');
    }
  };

  const handleDelete = async (clientId, clientName) => {
    if (!window.confirm(`¿Está seguro de eliminar el cliente "${clientName}"?`)) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${backendUrl}/api/clients/${clientId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        toast.success('Cliente eliminado exitosamente');
        loadClients();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Error al eliminar cliente');
      }
    } catch (error) {
      console.error('Error deleting client:', error);
      toast.error('Error al eliminar cliente');
    }
  };

  const addDepartment = () => {
    if (newDepartment.trim() === '') {
      toast.error('Por favor ingrese un nombre de departamento');
      return;
    }
    if (currentClient.departamentos.includes(newDepartment.trim())) {
      toast.error('Este departamento ya existe');
      return;
    }
    setCurrentClient({
      ...currentClient,
      departamentos: [...currentClient.departamentos, newDepartment.trim()]
    });
    setNewDepartment('');
  };

  const removeDepartment = (index) => {
    const newDepartamentos = [...currentClient.departamentos];
    newDepartamentos.splice(index, 1);
    setCurrentClient({
      ...currentClient,
      departamentos: newDepartamentos
    });
  };

  return (
    <Layout>
      <div className="container mx-auto p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">Gestión de Clientes</h1>
          <button
            onClick={openCreateModal}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium"
          >
            + Crear Nuevo Cliente
          </button>
        </div>

        {/* Tabla de clientes */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Cliente
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  CIF
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Departamentos
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {clients.map((client) => (
                <tr key={client.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{client.name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-500">{client.cif}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-500">
                      {client.departamentos && client.departamentos.length > 0 ? (
                        <div className="flex flex-wrap gap-1">
                          {client.departamentos.map((dept, idx) => (
                            <span key={idx} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                              {dept}
                            </span>
                          ))}
                        </div>
                      ) : (
                        <span className="text-gray-400">Sin departamentos</span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => openEditModal(client)}
                      className="text-blue-600 hover:text-blue-900 mr-4"
                    >
                      Editar
                    </button>
                    <button
                      onClick={() => handleDelete(client.id, client.name)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Eliminar
                    </button>
                  </td>
                </tr>
              ))}
              {clients.length === 0 && (
                <tr>
                  <td colSpan="4" className="px-6 py-4 text-center text-gray-500">
                    No hay clientes registrados
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Modal de crear/editar cliente */}
        {isModalOpen && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <h2 className="text-2xl font-bold mb-4">
                {isEditing ? 'Editar Cliente' : 'Crear Nuevo Cliente'}
              </h2>
              
              <form onSubmit={handleSubmit}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nombre del Cliente *
                  </label>
                  <input
                    type="text"
                    value={currentClient.name}
                    onChange={(e) => setCurrentClient({...currentClient, name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>

                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    CIF *
                  </label>
                  <input
                    type="text"
                    value={currentClient.cif}
                    onChange={(e) => setCurrentClient({...currentClient, cif: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>

                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Departamentos
                  </label>
                  
                  {/* Lista de departamentos actuales */}
                  {currentClient.departamentos.length > 0 && (
                    <div className="mb-3 flex flex-wrap gap-2">
                      {currentClient.departamentos.map((dept, index) => (
                        <div key={index} className="inline-flex items-center bg-blue-100 text-blue-800 px-3 py-1 rounded-full">
                          <span className="mr-2">{dept}</span>
                          <button
                            type="button"
                            onClick={() => removeDepartment(index)}
                            className="text-red-600 hover:text-red-800 font-bold"
                          >
                            ×
                          </button>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Agregar nuevo departamento */}
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={newDepartment}
                      onChange={(e) => setNewDepartment(e.target.value)}
                      placeholder="Nombre del departamento"
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault();
                          addDepartment();
                        }
                      }}
                    />
                    <button
                      type="button"
                      onClick={addDepartment}
                      className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md"
                    >
                      + Agregar
                    </button>
                  </div>
                </div>

                <div className="flex justify-end gap-3 mt-6">
                  <button
                    type="button"
                    onClick={closeModal}
                    className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                  >
                    {isEditing ? 'Guardar Cambios' : 'Crear Cliente'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default ClientManagement;
