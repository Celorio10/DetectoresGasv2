import { useState, useEffect } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import EquipmentMasterCatalog from "./pages/EquipmentMasterCatalog";
import ClientManagement from "./pages/ClientManagement";
import EquipmentEntry from "./pages/EquipmentEntry";
import EquipmentReview from "./pages/EquipmentReview";
import EquipmentExit from "./pages/EquipmentExit";
import EquipmentSummary from "./pages/EquipmentSummary";
import EquipmentHistory from "./pages/EquipmentHistory";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setIsAuthenticated(true);
    }
    setLoading(false);
  }, []);

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Cargando...</div>;
  }

  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route 
            path="/login" 
            element={isAuthenticated ? <Navigate to="/" /> : <Login setIsAuthenticated={setIsAuthenticated} />} 
          />
          <Route 
            path="/" 
            element={isAuthenticated ? <Dashboard /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/catalogo" 
            element={isAuthenticated ? <EquipmentMasterCatalog /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/clientes" 
            element={isAuthenticated ? <ClientManagement /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/entrada" 
            element={isAuthenticated ? <EquipmentEntry /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/revision" 
            element={isAuthenticated ? <EquipmentReview /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/salida" 
            element={isAuthenticated ? <EquipmentExit /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/resumen" 
            element={isAuthenticated ? <EquipmentSummary /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/historial" 
            element={isAuthenticated ? <EquipmentHistory /> : <Navigate to="/login" />} 
          />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;