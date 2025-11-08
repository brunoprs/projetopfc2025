import React, { useState, useEffect } from "react";
import { faqService } from "../../services/api";

export default function AdminFaqs() {
  const [faqs, setFaqs] = useState([]);
  const initialState = { question: "", answer: "" };
  const [form, setForm] = useState(initialState);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState(null);

  const loadFaqs = async () => {
    setLoading(true);
    try {
      const data = await faqService.getAll();
      setFaqs(data.faqs || []);
    } catch (err) {
      alert("Erro ao carregar FAQs: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFaqs();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        await faqService.update(editingId, form);
        alert("FAQ atualizada com sucesso!");
      } else {
        await faqService.create(form.question, form.answer);
        alert("FAQ criada com sucesso!");
      }
      setForm(initialState);
      setEditingId(null);
      loadFaqs();
    } catch (err) {
      alert("Erro: " + err.message);
    }
  };

  const handleEdit = (faq) => {
    setForm({
      question: faq.question,
      answer: faq.answer,
    });
    setEditingId(faq.id);
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Deseja excluir esta FAQ?")) return;
    try {
      await faqService.delete(id);
      loadFaqs();
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
        ❓ {editingId ? "Editar FAQ" : "Nova FAQ"}
      </h2>

      <form onSubmit={handleSubmit} className="mb-6 space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Pergunta</label>
          <input
            placeholder="Digite a pergunta"
            value={form.question}
            onChange={(e) => setForm({ ...form, question: e.target.value })}
            className={inputStyle}
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Resposta</label>
          <textarea
            placeholder="Digite a resposta completa"
            value={form.answer}
            onChange={(e) => setForm({ ...form, answer: e.target.value })}
            className={inputStyle}
            rows="4"
            required
          />
        </div>

        <div className="flex gap-2 pt-2">
          <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700">
            {editingId ? "Salvar Alterações" : "Criar FAQ"}
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

      <h3 className="text-lg font-medium mb-2">Lista de FAQs</h3>

      {loading ? (
        <p>Carregando...</p>
      ) : (
        <ul className="space-y-2">
          {faqs.map((f) => (
            <li key={f.id} className="flex justify-between items-center p-3 border rounded-lg bg-white shadow-sm">
              <span className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-gray-200 flex items-center justify-center text-xl">
                  ❓
                </div>
                <div>
                  <span className="font-semibold">{f.question}</span>
                  <p className="text-sm text-gray-600">
                    {f.answer.substring(0, 70)}...
                  </p>
                </div>
              </span>
              <div className="flex gap-2">
                <button
                  onClick={() => handleEdit(f)}
                  className="bg-yellow-400 text-black px-3 py-1 rounded-md text-sm"
                >
                  Editar
                </button>
                <button
                  onClick={() => handleDelete(f.id)}
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