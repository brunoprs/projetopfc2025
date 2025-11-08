import { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import "./App.css";

// 🧭 Páginas principais
import HomePage from "./pages/HomePage";
import ProductsPage from "./pages/ProductsPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import ProfilePage from "./pages/ProfilePage";
import FavoritesPage from "./pages/FavoritesPage";
import TipsPage from "./pages/TipsPage";
import FAQPage from "./pages/FAQPage";
import MyAccount from "./pages/MyAccount";
import ProductDetails from "@/pages/ProductDetails";
import PisoIdeal from "./pages/PisoIdeal";

// 🧩 Componentes e páginas administrativas
import AdminPanel from "./components/AdminPanel";
import AdminLogin from "./pages/AdminLogin";
import AdminRoute from "./components/AdminRoute";
import AdminPublicDashboard from "./pages/AdminPublicDashboard";
import AdminProducts from "./pages/admin/AdminProducts";
import AdminFaqs from "./pages/admin/AdminFaqs";
import AdminSocials from "./pages/admin/AdminSocials";
import AdminTips from "./pages/admin/AdminTips";
import AdminUsers from "./pages/admin/AdminUsers";

// ⚙️ Componentes globais
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import ChatBot from "@/components/ChatBot";

function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    const token = localStorage.getItem("token");

    if (storedUser && token) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (err) {
        console.error("Erro ao carregar usuário:", err);
        localStorage.removeItem("user");
        localStorage.removeItem("token");
      }
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
  };

  return (
    <Router>
      <div className="min-h-screen flex flex-col">
        {/* 🔝 Navbar global */}
        <Navbar user={user} setUser={setUser} onLogout={handleLogout} />

        <main className="flex-grow">
          <Routes>
            {/* 🌍 Rotas públicas */}
            <Route path="/" element={<HomePage />} />
            <Route path="/produtos" element={<ProductsPage user={user} />} />
            <Route path="/login" element={<LoginPage setUser={setUser} />} />
            <Route path="/cadastro" element={<RegisterPage />} />
            <Route path="/perfil" element={<ProfilePage user={user} />} />
            <Route path="/favoritos" element={<FavoritesPage user={user} />} />
            <Route path="/dicas" element={<TipsPage user={user} />} />
            <Route path="/faq" element={<FAQPage />} />
            <Route path="/minha-conta" element={<MyAccount user={user} />} />
            <Route path="/produtos/:id" element={<ProductDetails user={user} />} />
            <Route path="/piso-ideal" element={<PisoIdeal />} />

            {/* 🔐 Login do Administrador */}
            <Route path="/admin-login" element={<AdminLogin />} />

            {/* 🧰 Rotas do Painel Admin (layout aninhado) */}
            <Route
              path="/AdminPanel"
              element={
                <AdminRoute>
                  <AdminPanel /> {/* Renderiza o Layout (com botões e <Outlet />) */}
                </AdminRoute>
              }
            >
              {/* Rotas "Filhas" que aparecem dentro do <Outlet /> */}
              <Route index element={<Navigate to="dashboard" replace />} /> {/* Redireciona /AdminPanel para /AdminPanel/dashboard */}
              <Route path="dashboard" element={<AdminPublicDashboard user={user} />} /> {/* O dashboard de gráficos */}
              <Route path="products" element={<AdminProducts />} />
              <Route path="users" element={<AdminUsers />} />
              <Route path="tips" element={<AdminTips />} />
              <Route path="faqs" element={<AdminFaqs />} />
              <Route path="socials" element={<AdminSocials />} />
            </Route>

          </Routes>
        </main>
        <Footer />
        <ChatBot />

      </div>
    </Router>
  );
}

export default App;