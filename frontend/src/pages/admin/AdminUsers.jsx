import React, { useState, useEffect } from "react";
import { userService } from "../../services/api";

export default function AdminUsers() {
  const [users, setUsers] = useState([]);

  const initialState = {
    username: "",
    email: "",
    password: "",
    name: "",
  };
  const [form, setForm] = useState(initialState);
  const [loading, setLoading] = useState(false);
  // Estado para guardar o ID do usuário logado (opcional, mas recomendado)
  const [currentUserId, setCurrentUserId] = useState(null);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const data = await userService.getAll();
      setUsers(data.users || []);
    } catch (err) {
      alert("Erro ao carregar usuários: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
    // Tenta pegar o ID do usuário atual do localStorage
    try {
      const user = JSON.parse(localStorage.getItem('user'));
      if (user && user.id) {
        setCurrentUserId(user.id);
      }
    } catch (e) {
      // Ignora erro de parse
    }
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (form.password.length < 6) {
      alert("A senha deve ter pelo menos 6 caracteres.");
      return;
    }
    try {
      await userService.createAdmin(form.username, form.email, form.password, form.name);
      alert("Usuário admin criado com sucesso!");
      setForm(initialState);
      loadUsers();
    } catch (err) {
      alert("Erro: " + err.message);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Deseja realmente excluir este administrador?")) return;
    try {
      await userService.delete(id);
      loadUsers();
    } catch (err) {
      alert("Erro ao excluir: " + err.message);
    }
  };

  const inputStyle = "border p-2 rounded-md w-full";

  return (
    <div className="p-6">
      <h2 className="text-xl font-semibold mb-4">
        👤 Gerenciar Usuários
      </h2>

      <form onSubmit={handleCreate} className="mb-6 space-y-4">
        {/* ... (seu formulário continua igual) ... */}
        <div>
          <label className="block text-sm font-medium mb-1">Nome Completo</label>
          <input
            placeholder="Nome do usuário"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            className={inputStyle}
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Username</label>
            <input
              placeholder="Username"
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              className={inputStyle}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">E-mail</label>
            <input
              placeholder="E-mail"
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              className={inputStyle}
              required
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Senha Provisória</label>
          <input
            placeholder="Senha (mín. 6 caracteres)"
            type="password"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            className={inputStyle}
            required
          />
        </div>

        <div className="flex gap-2 pt-2">
          <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700">
            Criar Admin
          </button>
        </div>
      </form>

      <h3 className="text-lg font-medium mb-2">Lista de Usuários</h3>

      {loading ? (
        <p>Carregando...</p>
      ) : (
        <ul className="space-y-2">
          {users.map((u) => (
            <li key={u.id} className="flex justify-between items-center p-3 border rounded-lg bg-white shadow-sm">
              <span className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-gray-200 flex items-center justify-center font-semibold text-gray-600 text-lg">
                  {u.name ? u.name[0].toUpperCase() : (u.username ? u.username[0].toUpperCase() : '?')}
                </div>
                <div>
                  <span className="font-semibold">{u.name}</span>
                  <span className={`ml-2 text-xs font-medium px-2 py-0.5 rounded-full ${u.is_admin
                      ? "bg-blue-200 text-blue-800"
                      : "bg-gray-200 text-gray-700"
                    }`}>
                    {u.is_admin ? "Admin" : "Usuário"}
                  </span>
                  <p className="text-sm text-gray-600">{u.username} ({u.email})</p>
                </div>
              </span>
              <div className="flex gap-2">

                {u.is_admin && u.id !== currentUserId && (
                  <button
                    onClick={() => handleDelete(u.id)}
                    className="bg-red-600 text-white px-3 py-1 rounded-md text-sm hover:bg-red-700 transition-colors"
                  >
                    Excluir Admin
                  </button>
                )}

              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}