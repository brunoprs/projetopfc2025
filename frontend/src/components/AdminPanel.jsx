import React from "react";
import { Link, Outlet } from "react-router-dom";

export default function AdminPanel() {
  return (
    <div style={{ padding: "20px", backgroundColor: "#f8f9fa", minHeight: "100vh" }}>
      <h2 style={{ color: "#1a3d2f" }}>Painel de Administração</h2>
      <p style={{ color: "#555" }}>
        Bem-vindo ao painel administrativo. Escolha uma das seções abaixo para gerenciar.
      </p>

      <nav
        style={{
          display: "flex",
          gap: "10px",
          flexWrap: "wrap",
          marginBottom: "30px",
          marginTop: "20px",
        }}
      >

        <Link
          to="/AdminPanel/dashboard"
          style={{
            background: "#1a3d2f",
            color: "white",
            padding: "10px 15px",
            borderRadius: "8px",
            textDecoration: "none",
          }}
        >
          📈 Dashboard
        </Link>

        <Link
          to="/AdminPanel/products"
          style={{
            background: "#1a3d2f",
            color: "white",
            padding: "10px 15px",
            borderRadius: "8px",
            textDecoration: "none",
          }}
        >
          🛒 Produtos
        </Link>

        <Link
          to="/AdminPanel/users"
          style={{
            background: "#1a3d2f",
            color: "white",
            padding: "10px 15px",
            borderRadius: "8px",
            textDecoration: "none",
          }}
        >
          👤 Usuários
        </Link>

        <Link
          to="/AdminPanel/tips"
          style={{
            background: "#1a3d2f",
            color: "white",
            padding: "10px 15px",
            borderRadius: "8px",
            textDecoration: "none",
          }}
        >
          💡 Dicas
        </Link>

        <Link
          to="/AdminPanel/faqs"
          style={{
            background: "#1a3d2f",
            color: "white",
            padding: "10px 15px",
            borderRadius: "8px",
            textDecoration: "none",
          }}
        >
          ❓ FAQs
        </Link>

      </nav>

      <div
        style={{
          background: "#ffffff",
          padding: "20px",
          borderRadius: "10px",
          boxShadow: "0 0 8px rgba(0,0,0,0.1)",
        }}
      >
        <Outlet />
      </div>
    </div>
  );
}