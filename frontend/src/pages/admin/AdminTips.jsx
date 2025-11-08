import React, { useState, useEffect } from "react";
import { tipService } from "../../services/api";

export default function AdminTips() {
  const [tips, setTips] = useState([]);

  const initialState = { title: "", content: "", category: "" };
  const [form, setForm] = useState(initialState);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState(null);

  const loadTips = async () => {
    setLoading(true);
    try {
      const data = await tipService.getAll();
      setTips(data.tips || []);
    } catch (err) {
      alert("Erro ao carregar dicas: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTips();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        await tipService.update(editingId, form);
        alert("Dica atualizada com sucesso!");
      } else {
        await tipService.create(form.title, form.content, form.category);
        alert("Dica criada com sucesso!");
      }
      setForm(initialState);
      setEditingId(null);
      loadTips();
    } catch (err) {
      alert("Erro: " + err.message);
    }
  };

  const handleEdit = (tip) => {
    setForm({
      title: tip.title,
      content: tip.content,
      category: tip.category || "",
    });
    setEditingId(tip.id);
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Deseja realmente excluir esta dica?")) return;
    try {
      await tipService.delete(id);
      loadTips();
    } catch (err) {
      alert("Erro ao excluir: " + err.message);
    }
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setForm(initialState);
  };

  const inputStyle = "border p-2 rounded-md w-full";

  return (
    <div className="p-6">
      <h2 className="text-xl font-semibold mb-4">
        💡 {editingId ? "Editar Dica" : "Nova Dica"}
      </h2>

      <form onSubmit={handleSubmit} className="mb-6 space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Título</label>
            <input
              placeholder="Título da dica"
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              className={inputStyle}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Categoria</label>
            <input
              placeholder="Ex: Laminado, Limpeza"
              value={form.category}
              onChange={(e) => setForm({ ...form, category: e.target.value })}
              className={inputStyle}
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Conteúdo</label>
          <textarea
            placeholder="Escreva a dica aqui..."
            value={form.content}
            onChange={(e) => setForm({ ...form, content: e.target.value })}
            className={inputStyle}
            rows="4"
            required
          />
        </div>

        <div className="flex gap-2 pt-2">
          <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700">
            {editingId ? "Salvar Alterações" : "Criar Dica"}
          </button>

          {editingId && (
            <button
              type="button"
              onClick={handleCancelEdit}
              className="bg-gray-400 text-white px-4 py-2 rounded-md hover:bg-gray-500"
            >
              Cancelar
            </button>
          )}
        </div>
      </form>

      <h3 className="text-lg font-medium mb-2">Lista de Dicas</h3>

      {loading ? (
        <p>Carregando...</p>
      ) : (
        <ul className="space-y-2">
          {tips.map((t) => (
            <li key={t.id} className="flex justify-between items-center p-3 border rounded-lg bg-white shadow-sm">
              <span className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-gray-200 flex items-center justify-center text-xl">
                  💡
                </div>
                <div>
                  <span className="font-semibold">{t.title}</span>
                  <span className="ml-2 bg-gray-200 text-gray-700 text-xs font-medium px-2 py-0.5 rounded-full">
                    {t.category || "Geral"}
                  </span>
                  <p className="text-sm text-gray-600">
                    {t.content.substring(0, 50)}...
                  </p>
                </div>
              </span>
              <div className="flex gap-2">
                <button
                  onClick={() => handleEdit(t)}
                  className="bg-yellow-400 text-black px-3 py-1 rounded-md text-sm"
                >
                  Editar
                </button>
                <button
                  onClick={() => handleDelete(t.id)}
                  className="bg-red-600 text-white px-3 py-1 rounded-md text-sm"
                >
                  Excluir
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}