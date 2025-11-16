import React, { useState, useEffect, useMemo } from "react";
import { productService } from "../../services/api";

export default function AdminProducts() {
  const [products, setProducts] = useState([]);

  const initialState = {
    name: "",
    price: "",
    description: "",
    image_url: "",
    type: "vinilico",
  };
  const [form, setForm] = useState(initialState);

  const [loading, setLoading] = useState(false);
  const [editingId, setEditingId] = useState(null);

  // paginação local
  const [page, setPage] = useState(1);
  const itemsPerPage = 10;

  // busca
  const [search, setSearch] = useState("");

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

  // FILTRO DE PESQUISA
  const filteredProducts = useMemo(() => {
    const lower = search.toLowerCase();
    return products.filter(
      (p) =>
        p.name.toLowerCase().includes(lower) ||
        p.type.toLowerCase().includes(lower) ||
        (p.description && p.description.toLowerCase().includes(lower))
    );
  }, [products, search]);

  // total de páginas baseado na busca
  const totalPages = useMemo(() => {
    return Math.max(1, Math.ceil(filteredProducts.length / itemsPerPage));
  }, [filteredProducts.length]);

  // produtos da página atual
  const currentProducts = useMemo(() => {
    const start = (page - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    return filteredProducts.slice(start, end);
  }, [filteredProducts, page]);

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

  const handlePageChange = (newPage) => {
    if (newPage < 1 || newPage > totalPages) return;
    setPage(newPage);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const inputStyle = "border p-2 rounded-md w-full";

  return (
    <div className="p-6">
      <h2 className="text-xl font-semibold mb-4">
        🛒 {editingId ? "Editar Produto" : "Novo Produto"}
      </h2>

      {/* FORMULÁRIO */}
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
            onChange={(e) =>
              setForm({ ...form, description: e.target.value })
            }
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
          <button
            type="submit"
            className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
          >
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

      {/* CAMPO DE PESQUISA */}
      <div className="mb-4 flex justify-between items-center">
        <h3 className="text-lg font-medium">Lista de Produtos</h3>
        <input
          type="text"
          placeholder="Pesquisar produto..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
          className="border rounded-md p-2 w-64"
        />
      </div>

      {loading ? (
        <p>Carregando...</p>
      ) : (
        <>
          <ul className="space-y-2">
            {currentProducts.map((p) => (
              <li
                key={p.id}
                className="flex justify-between items-center p-3 border rounded-lg bg-white shadow-sm"
              >
                <span className="flex items-center gap-3">
                  <img
                    src={
                      p.image_url ||
                      "https://via.placeholder.com/40x40?text=Sem+Img"
                    }
                    alt={p.name}
                    className="w-12 h-12 rounded-md object-cover"
                  />
                  <div>
                    <span className="font-semibold">{p.name}</span>
                    <span className="ml-2 bg-gray-200 text-gray-700 text-xs font-medium px-2 py-0.5 rounded-full">
                      {p.type}
                    </span>
                    <p className="text-sm text-gray-600">
                      R$ {p.price} /m²
                    </p>
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
