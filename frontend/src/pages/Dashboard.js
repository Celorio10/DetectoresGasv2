import { Link } from "react-router-dom";
import { Wrench, FileInput, ClipboardCheck, PackageOpen, BarChart3 } from "lucide-react";
import Layout from "../components/Layout";

export default function Dashboard() {
  const modules = [
    {
      id: 1,
      title: "Entrada de Equipos",
      description: "Registrar nuevos equipos en el taller",
      icon: FileInput,
      link: "/entrada",
      color: "from-blue-500 to-blue-600",
      testId: "entrada-card"
    },
    {
      id: 2,
      title: "Revisión de Equipos",
      description: "Calibrar y revisar equipos en taller",
      icon: ClipboardCheck,
      link: "/revision",
      color: "from-green-500 to-green-600",
      testId: "revision-card"
    },
    {
      id: 3,
      title: "Salida de Equipos",
      description: "Gestionar entregas de equipos",
      icon: PackageOpen,
      link: "/salida",
      color: "from-orange-500 to-orange-600",
      testId: "salida-card"
    },
    {
      id: 4,
      title: "Resumen de Equipos",
      description: "Consultar historial y estadísticas",
      icon: BarChart3,
      link: "/resumen",
      color: "from-purple-500 to-purple-600",
      testId: "resumen-card"
    }
  ];

  return (
    <Layout>
      <div className="max-w-7xl mx-auto" data-testid="dashboard">
        <div className="mb-12 text-center">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Wrench className="w-10 h-10 text-blue-600" />
            <h1 className="text-4xl sm:text-5xl font-bold text-gray-800" style={{ fontFamily: 'Space Grotesk' }}>
              Panel de Control
            </h1>
          </div>
          <p className="text-lg text-gray-600">Selecciona un módulo para comenzar</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {modules.map((module) => {
            const Icon = module.icon;
            return (
              <Link
                key={module.id}
                to={module.link}
                data-testid={module.testId}
                className="card-hover block"
              >
                <div className="bg-white rounded-2xl shadow-lg p-8 h-full border border-gray-100">
                  <div className={`bg-gradient-to-br ${module.color} p-4 rounded-xl inline-block mb-6`}>
                    <Icon className="w-10 h-10 text-white" />
                  </div>
                  <h2 className="text-2xl font-bold text-gray-800 mb-3" style={{ fontFamily: 'Space Grotesk' }}>
                    {module.title}
                  </h2>
                  <p className="text-gray-600 text-base">
                    {module.description}
                  </p>
                </div>
              </Link>
            );
          })}
        </div>
      </div>
    </Layout>
  );
}