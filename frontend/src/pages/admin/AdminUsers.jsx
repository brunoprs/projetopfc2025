import React, { useState, useEffect, useMemo } from "react";
import { userService } from "../../services/api";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000/api";

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

  // ID do usuário logado (pra não se auto-deletar / auto-inativar)
  const [currentUserId, setCurrentUserId] = useState(null);

  // busca + paginação
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const itemsPerPage = 10;

  const loadUsers = async () => {
    setLoading(true);
    try {
      const data = await userService.getAll(); // traz todos, filtramos no front
      setUsers(data.users || []);
    } catch (err) {
      alert("Erro ao carregar usuários: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
    // pega o usuário logado do localStorage
    try {
      const user = JSON.parse(localStorage.getItem("user"));
      if (user && user.id) {
        setCurrentUserId(user.id);
      }
    } catch (e) {
      // ignora erro de parse
    }
  }, []);

  // ------- FILTRO DE BUSCA --------
  const filteredUsers = useMemo(() => {
    const term = search.toLowerCase();
    if (!term) return users;

    return users.filter(
      (u) =>
        (u.name && u.name.toLowerCase().includes(term)) ||
        (u.username && u.username.toLowerCase().includes(term)) ||
        (u.email && u.email.toLowerCase().includes(term))
    );
  }, [users, search]);

  // ------- PAGINAÇÃO (10 por página) --------
  const totalPages = useMemo(() => {
    return Math.max(1, Math.ceil(filteredUsers.length / itemsPerPage));
  }, [filteredUsers.length]);

  const currentUsers = useMemo(() => {
    const start = (page - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    return filteredUsers.slice(start, end);
  }, [filteredUsers, page]);

  const handlePageChange = (newPage) => {
    if (newPage < 1 || newPage > totalPages) return;
    setPage(newPage);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    if (form.password.length < 6) {
      alert("A senha deve ter pelo menos 6 caracteres.");
      return;
    }
    try {
      await userService.createAdmin(
        form.username,
        form.email,
        form.password,
        form.name
      );
      alert("Usuário admin criado com sucesso!");
      setForm(initialState);
      setPage(1); // volta pra primeira página
      loadUsers();
    } catch (err) {
      alert("Erro: " + err.message);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Deseja realmente excluir este administrador?")) return;
    try {
      await userService.delete(id);
      // garante que a página não fique “vazia” depois da exclusão
      setPage(1);
      loadUsers();
    } catch (err) {
      alert("Erro ao excluir: " + err.message);
    }
  };

  // ---- ATIVAR / INATIVAR USUÁRIO ----
  const handleToggleStatus = async (user) => {
    if (user.id === currentUserId) {
      alert("Você não pode alterar o próprio status.");
      return;
    }

    const acao = user.is_active ? "inativar" : "reativar";
    if (!window.confirm(`Tem certeza que deseja ${acao} este usuário?`)) return;

    try {
      const token = localStorage.getItem("token");
      if (!token) {
        alert("Token não encontrado. Faça login novamente.");
        return;
      }

      const res = await fetch(`${API_BASE_URL}/admin/users/${user.id}/status`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ is_active: !user.is_active }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.error || "Erro ao atualizar status do usuário");
      }

      // Atualiza apenas o usuário alterado na lista
      setUsers((prev) =>
        prev.map((u) =>
          u.id === user.id ? { ...u, is_active: !user.is_active } : u
        )
      );
    } catch (err) {
      alert(err.message);
    }
  };

  const inputStyle = "border p-2 rounded-md w-full";

  return (
    <div className="p-6">
      <h2 className="text-xl font-semibold mb-4">👤 Gerenciar Usuários</h2>

      {/* FORMULÁRIO DE CRIAÇÃO */}
      <form onSubmit={handleCreate} className="mb-6 space-y-4">
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
          <button
            type="submit"
            className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
          >
            Criar Admin
          </button>
        </div>
      </form>

      {/* TÍTULO + CAMPO DE BUSCA */}
      <div className="mb-4 flex justify-between items-center">
        <h3 className="text-lg font-medium">Lista de Usuários</h3>
        <input
          type="text"
          placeholder="Buscar por nome, username ou e-mail..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1); // sempre volta pra página 1 ao filtrar
          }}
          className="border rounded-md p-2 w-72"
        />
      </div>

      {loading ? (
        <p>Carregando...</p>
      ) : (
        <>
          {/* LISTA DE USUÁRIOS (PAGINADA) */}
          <ul className="space-y-2">
            {currentUsers.map((u) => (
              <li
                key={u.id}
                className="flex justify-between items-center p-3 border rounded-lg bg-white shadow-sm"
              >
                <span className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-gray-200 flex items-center justify-center font-semibold text-gray-600 text-lg">
                    {u.name
                      ? u.name[0].toUpperCase()
                      : u.username
                      ? u.username[0].toUpperCase()
                      : "?"}
                  </div>
                  <div>
                    <span className="font-semibold">{u.name}</span>

                    {/* PAPEL (Admin / Usuário) */}
                    <span
                      className={`ml-2 text-xs font-medium px-2 py-0.5 rounded-full ${
                        u.is_admin
                          ? "bg-blue-200 text-blue-800"
                          : "bg-gray-200 text-gray-700"
                      }`}
                    >
                      {u.is_admin ? "Admin" : "Usuário"}
                    </span>

                    {/* STATUS (Ativo / Inativo) */}
                    <span
                      className={`ml-2 text-xs font-medium px-2 py-0.5 rounded-full ${
                        u.is_active
                          ? "bg-green-200 text-green-800"
                          : "bg-red-200 text-red-800"
                      }`}
                    >
                      {u.is_active ? "Ativo" : "Inativo"}
                    </span>

                    <p className="text-sm text-gray-600">
                      {u.username} ({u.email})
                    </p>
                  </div>
                </span>

                <div className="flex gap-2">
                  {/* Botão de ativar / inativar */}
                  {u.id !== currentUserId && (
                    <button
                      type="button"
                      onClick={() => handleToggleStatus(u)}
                      className={`px-3 py-1 rounded-md text-sm text-white ${
                        u.is_active
                          ? "bg-orange-500 hover:bg-orange-600"
                          : "bg-green-600 hover:bg-green-700"
                      }`}
                    >
                      {u.is_active ? "Inativar" : "Ativar"}
                    </button>
                  )}

                  {/* Botão de excluir admin (mantido como estava) */}
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

          {/* PAGINAÇÃO */}
          <div className="flex items-center justify-center gap-4 mt-6">
            <button
              type="button"
              disabled={page <= 1}
              onClick={() => handlePageChange(page - 1)}
              className={`px-3 py-1 border rounded-md text-sm ${
                page <= 1
                  ? "opacity-50 cursor-not-allowed"
                  : "hover:bg-gray-100"
              }`}
            >
              Anterior
            </button>

            <span className="text-sm text-gray-600">
              Página <strong>{page}</strong> de <strong>{totalPages}</strong>
            </span>

            <button
              type="button"
              disabled={page >= totalPages}
              onClick={() => handlePageChange(page + 1)}
              className={`px-3 py-1 border rounded-md text-sm ${
                page >= totalPages
                  ? "opacity-50 cursor-not-allowed"
                  : "hover:bg-gray-100"
              }`}
            >
              Próxima
            </button>
          </div>
        </>
      )}
    </div>
  );
}
