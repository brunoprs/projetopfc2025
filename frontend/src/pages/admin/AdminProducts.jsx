import React, { useState, useEffect } from "react";
import { productService } from "../../services/api";

export default function AdminProducts() {
  const [products, setProducts] = useState([]);

  const initialState = { name: "", price: "", description: "", image_url: "", type: "vinilico" };
  const [form, setForm] = useState(initialState);

  const [loading, setLoading] = useState(false);
  const [editingId, setEditingId] = useState(null);

  const loadProducts = async () => {
    setLoading(true);
    try {
      const data = await productService.getAll();
      setProducts(data.products || []);
    } catch (err) {
      alert("Erro ao carregar produtos: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProducts();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        await productService.update(editingId, form);
        alert("Produto atualizado com sucesso!");
      } else {
        await productService.create(form);
        alert("Produto criado com sucesso!");
      }
      setForm(initialState);
      setEditingId(null);
      loadProducts();
    } catch (err) {
      alert("Erro: " + err.message);
    }
  };

  const handleEdit = (product) => {
    setForm({
      name: product.name,
      price: product.price,
      description: product.description,
      image_url: product.image_url || "",
      type: product.type || "vinilico",
    });
    setEditingId(product.id);
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Deseja realmente excluir este produto?")) return;
    try {
      await productService.delete(id);
      loadProducts();
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
        🛒 {editingId ? "Editar Produto" : "Novo Produto"}
      </h2>

      <form onSubmit={handleSubmit} className="mb-6 space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Nome</label>
          <input
            placeholder="Nome do produto"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            className={inputStyle}
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Preço (R$)</label>
            <input
              placeholder="Preço por m²"
              type="number"
              step="0.01"
              value={form.price}
              onChange={(e) => setForm({ ...form, price: e.target.value })}
              className={inputStyle}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Tipo de Piso</label>
            <select
              value={form.type}
              onChange={(e) => setForm({ ...form, type: e.target.value })}
              className={inputStyle}
              required
            >
              <option value="vinilico">Vinílico</option>
              <option value="laminado">Laminado</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Descrição</label>
          <textarea
            placeholder="Descrição"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            className={inputStyle}
            rows="3"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">URL da Imagem</label>
          <input
            placeholder="https://exemplo.com/imagem.png"
            type="text"
            value={form.image_url}
            onChange={(e) => setForm({ ...form, image_url: e.target.value })}
            className={inputStyle}
          />
        </div>

        <div className="flex gap-2 pt-2">
          <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700">
            {editingId ? "Salvar Alterações" : "Criar Produto"}
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

      <h3 className="text-lg font-medium mb-2">Lista de Produtos</h3>

      {loading ? (
        <p>Carregando...</p>
      ) : (
        <ul className="space-y-2">
          {products.map((p) => (
            <li key={p.id} className="flex justify-between items-center p-3 border rounded-lg bg-white shadow-sm">
              <span className="flex items-center gap-3">
                <img
                  src={p.image_url || 'https://via.placeholder.com/40x40?text=Sem+Img'}
                  alt={p.name}
                  className="w-12 h-12 rounded-md object-cover"
                />
                <div>
                  <span className="font-semibold">{p.name}</span>
                  <span className="ml-2 bg-gray-200 text-gray-700 text-xs font-medium px-2 py-0.5 rounded-full">
                    {p.type}
                  </span>
                  <p className="text-sm text-gray-600">R$ {p.price} /m²</p>
                </div>
              </span>
              <div className="flex gap-2">
                <button
                  onClick={() => handleEdit(p)}
                  className="bg-yellow-400 text-black px-3 py-1 rounded-md text-sm"
                >
                  Editar
                </button>
                <button
                  onClick={() => handleDelete(p.id)}
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