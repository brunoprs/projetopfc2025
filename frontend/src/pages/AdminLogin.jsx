import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authService } from "../services/api";

export default function AdminLogin() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const data = await authService.login(username, password);
      if (!data.user?.is_admin) {
        setError("Acesso negado: este usuário não é administrador.");
        return;
      }

      localStorage.setItem("token", data.token);
      localStorage.setItem("user", JSON.stringify(data.user));

      navigate("/AdminPanel/dashboard");
    } catch (err) {
      setError(err.message || "Falha no login.");
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen">
      <h2 className="text-2xl font-semibold mb-4">Login do Administrador</h2>
      <form onSubmit={handleLogin} className="flex flex-col w-80 space-y-3">
        <input
          type="text"
          placeholder="Usuário"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="border rounded p-2"
        />
        <input
          type="password"
          placeholder="Senha"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="border rounded p-2"
        />
        <button
          type="submit"
          className="bg-green-900 text-white py-2 rounded hover:bg-green-800"
        >
          Entrar
        </button>
        {error && <p className="text-red-600 text-sm mt-2">{error}</p>}
      </form>
    </div>
  );
  navigate("/AdminPanel/dashboard");
}
