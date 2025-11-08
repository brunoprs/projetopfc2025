import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Scale } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { productService } from "@/services/api";

function RatingStars({ productId, user }) {
  const [selected, setSelected] = useState(0);
  const [average, setAverage] = useState(null);
  const token = localStorage.getItem("token");

  const loadAverage = async () => {
    try {
      const res = await fetch(`http://localhost:5000/products/${productId}/rating`);
      const data = await res.json();
      setAverage(data.average);
    } catch (err) {
      console.error("Erro ao carregar média:", err);
    }
  };

  useEffect(() => {
    loadAverage();
  }, [productId]);

  const handleRate = async (value) => {
    if (!user) {
      alert("Faça login para avaliar o produto");
      return;
    }
    setSelected(value);
    try {
      const res = await fetch(`http://localhost:5000/products/${productId}/rating`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ rating: value }),
      });
      const data = await res.json();
      if (!res.ok) {
        alert(data.error || "Erro ao registrar nota");
      } else {
        loadAverage();
      }
    } catch (err) {
      console.error(err);
      alert("Erro ao enviar nota");
    }
  };

  return (
    <div className="my-4">
      <h3 className="font-semibold mb-2">Avaliação</h3>
      <div>
        {[1, 2, 3, 4, 5].map((n) => (
          <span
            key={n}
            onClick={() => handleRate(n)}
            style={{
              cursor: "pointer",
              color: n <= selected ? "#FFD700" : "#ccc",
              fontSize: "28px",
            }}
          >
            ★
          </span>
        ))}
      </div>
      {average && (
        <p className="text-sm text-gray-500 mt-1">
          Média atual: {average.toFixed(1)} / 5
        </p>
      )}
    </div>
  );
}

export default function ProductDetails({ user }) {
  const { id } = useParams();
  const [product, setProduct] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [comment, setComment] = useState("");
  const [meters, setMeters] = useState("");
  const navigate = useNavigate();

  const [cep, setCep] = useState("");
  const [cepLoading, setCepLoading] = useState(false);
  const [cepResult, setCepResult] = useState(null);

  const [allProducts, setAllProducts] = useState([]);
  const [isCompareModalOpen, setIsCompareModalOpen] = useState(false);
  const [compareLoading, setCompareLoading] = useState(false);
  const [selectedProductId, setSelectedProductId] = useState(null);
  const [productToCompare, setProductToCompare] = useState(null);

  const loadProductAndReviews = async () => {
    try {
      const productRes = await fetch(`http://localhost:5000/products/${id}`);
      const productData = await productRes.json();
      setProduct(productData);

      const reviewsRes = await fetch(`http://localhost:5000/products/${id}/reviews`);
      const reviewsData = await reviewsRes.json();
      setReviews(reviewsData);
    } catch (err) {
      console.error("Erro ao carregar produto e comentários:", err);
    }
  };

  useEffect(() => {
    loadProductAndReviews();
  }, [id]);

  const loadAllProducts = async () => {
    setCompareLoading(true);
    try {
      const data = await productService.getAll();
      const otherProducts = data.products.filter(p => p.id !== product.id);
      setAllProducts(otherProducts || []);
    } catch (err) {
      console.error("Erro ao carregar lista de produtos:", err);
    } finally {
      setCompareLoading(false);
    }
  };

  const handleOpenCompareModal = () => {
    if (allProducts.length === 0) {
      loadAllProducts();
    }
    setIsCompareModalOpen(true);
  };

  const handleSelectProductToCompare = () => {
    if (selectedProductId) {
      const foundProduct = allProducts.find(p => p.id === parseInt(selectedProductId));
      setProductToCompare(foundProduct);
    }
  };

  const handleCloseCompare = () => {
    setIsCompareModalOpen(false);
    setProductToCompare(null);
    setSelectedProductId(null);
  };

  const handleAddComment = async () => {
    if (!user) {
      navigate("/login");
      return;
    }
    if (!comment.trim()) return;

    try {
      const res = await fetch(`http://localhost:5000/products/${id}/reviews`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem("token")}`
        },
        body: JSON.stringify({ comment }),
      });

      if (res.ok) {
        setComment("");
        loadProductAndReviews();
      } else {
        const data = await res.json();
        alert(data.error || "Erro ao adicionar comentário");
      }
    } catch (err) {
      console.error(err);
      alert("Erro ao adicionar comentário");
    }
  };

  const handleDeleteComment = async (reviewId) => {
    if (!user) {
      navigate("/login");
      return;
    }

    try {
      const res = await fetch(`http://localhost:5000/products/${id}/reviews/${reviewId}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem("token")}`,
        },
      });

      if (res.ok) {
        setReviews(prev => prev.filter(r => r.id !== reviewId));
      } else {
        const data = await res.json();
        alert(data.error || "Erro ao deletar comentário");
      }
    } catch (err) {
      console.error(err);
      alert("Erro ao deletar comentário");
    }
  };

  const handleCepCheck = async () => {
    const numericCep = cep.replace(/\D/g, '');
    if (numericCep.length !== 8) {
      setCepResult({ type: 'error', message: 'CEP inválido. Deve conter 8 dígitos.' });
      return;
    }
    setCepLoading(true);
    setCepResult(null);
    await new Promise(resolve => setTimeout(resolve, 1000));

    const altoTietePrefixes = [
      '074',
      '075',
      '085',
      '086',
      '087',
      '088',
      '089'
    ];

    const cepPrefix = numericCep.substring(0, 3);
    const isAltoTiete = altoTietePrefixes.includes(cepPrefix);

    if (isAltoTiete) {
      setCepResult({
        type: 'success',
        message: 'Ótima notícia! Atendemos a sua região!.'
      });
    } else {
      setCepResult({
        type: 'error',
        message: 'Que pena! Atualmente, só atendemos a região do Alto Tietê.'
      });
    }

    setCepLoading(false);
  };

  const handleCepChange = (e) => {
    const value = e.target.value;
    let numericValue = value.replace(/\D/g, '');

    if (numericValue.length > 8) {
      numericValue = numericValue.substring(0, 8);
    }

    let formattedValue = numericValue;
    if (numericValue.length > 5) {
      formattedValue = numericValue.substring(0, 5) + '-' + numericValue.substring(5);
    }

    setCep(formattedValue);
  };

  const renderCompareModal = () => (
    <Dialog open={isCompareModalOpen} onOpenChange={setIsCompareModalOpen}>
      <DialogContent className="sm:max-w-[600px] md:max-w-[800px]">
        <DialogHeader>
          <DialogTitle>Comparar Produtos</DialogTitle>
        </DialogHeader>

        {!productToCompare ? (
          <div className="py-4">
            <h3 className="mb-2 text-sm font-medium">Selecione um produto para comparar com "{product.name}":</h3>
            {compareLoading ? (
              <p>Carregando produtos...</p>
            ) : (
              <Select onValueChange={setSelectedProductId}>
                <SelectTrigger>
                  <SelectValue placeholder="Escolha um produto..." />
                </SelectTrigger>
                <SelectContent>
                  {allProducts.map(p => (
                    <SelectItem key={p.id} value={p.id.toString()}>
                      {p.name} (R$ {p.price}/m²)
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
            <DialogFooter className="mt-4">
              <Button
                onClick={handleSelectProductToCompare}
                disabled={!selectedProductId || compareLoading}
                className="bg-blue-600 text-white"
              >
                Comparar
              </Button>
            </DialogFooter>
          </div>
        ) : (
          <div className="py-4">
            <div className="overflow-x-auto">
              <table className="w-full border-collapse text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="p-2 text-left font-semibold">Característica</th>
                    <th className="p-2 text-left font-semibold">{product.name} (Atual)</th>
                    <th className="p-2 text-left font-semibold">{productToCompare.name}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b">
                    <td className="p-2 font-medium">Imagem</td>
                    <td className="p-2"><img src={product.image_url || 'https://via.placeholder.com/100'} alt={product.name} className="w-24 h-24 object-cover rounded-md" /></td>
                    <td className="p-2"><img src={productToCompare.image_url || 'https://via.placeholder.com/100'} alt={productToCompare.name} className="w-24 h-24 object-cover rounded-md" /></td>
                  </tr>
                  <tr className="border-b bg-gray-50">
                    <td className="p-2 font-medium">Preço</td>
                    <td className="p-2 text-lg font-bold text-blue-600">R$ {Number(product.price).toFixed(2)}/m²</td>
                    <td className="p-2 text-lg font-bold text-blue-600">R$ {Number(productToCompare.price).toFixed(2)}/m²</td>
                  </tr>
                  <tr className="border-b">
                    <td className="p-2 font-medium">Tipo</td>
                    <td className="p-2">{product.type || 'N/A'}</td>
                    <td className="p-2">{productToCompare.type || 'N/A'}</td>
                  </tr>
                  <tr className="border-b">
                    <td className="p-2 font-medium">Descrição</td>
                    <td className="p-2 text-xs">{product.description}</td>
                    <td className="p-2 text-xs">{productToCompare.description}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <DialogFooter className="mt-4">
              <Button variant="outline" onClick={() => setProductToCompare(null)}>Voltar à seleção</Button>
              <DialogClose asChild>
                <Button type="button" onClick={handleCloseCompare}>Fechar</Button>
              </DialogClose>
            </DialogFooter>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );

  if (!product) return <p className="text-center">Carregando...</p>;

  const total =
    meters && product?.price
      ? (parseFloat(product.price) * parseFloat(meters)).toFixed(2)
      : null;

  return (
    <div className="max-w-3xl mx-auto p-6 bg-white shadow rounded-2xl">
      <h2 className="text-3xl font-bold mb-2">{product.name}</h2>
      <p className="text-gray-600 mb-4">{product.description}</p>
      {product.image_url && (
        <div className="mb-4">
          <img
            src={product.image_url}
            alt={product.name}
            className="w-full max-h-96 object-cover rounded-lg shadow-md"
          />
        </div>
      )}
      <p className="text-2xl font-semibold text-blue-600 mb-4">
        R$ {Number(product.price).toFixed(2)}/m²
      </p>

      <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 mb-6">
        <h3 className="font-semibold text-lg mb-2 text-gray-700">
          Calcule o preço pela metragem:
        </h3>
        <div className="flex items-center gap-3">
          <Input
            type="number"
            min="0"
            step="0.1"
            value={meters}
            onChange={(e) => setMeters(e.target.value >= 0 ? e.target.value : "")}
            className="w-32 focus:ring-blue-500"
            placeholder="m²"
          />
          <span className="text-gray-700">m²</span>
        </div>
        {total && (
          <p className="mt-3 text-gray-800 text-lg font-semibold">
            Total estimado:{" "}
            <span className="text-blue-600">R$ {total}</span>
          </p>
        )}
      </div>

      <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 mb-6">
        <h3 className="font-semibold text-lg mb-2 text-gray-700">
          Pifloor Atende?
        </h3>
        <p className="text-sm text-gray-600 mb-3">
          Digite seu CEP para verificar se entregamos e instalamos na sua região.
        </p>
        <div className="flex items-start gap-3">
          <Input
            type="text"
            value={cep}
            onChange={handleCepChange}
            maxLength={9}
            className="w-40 focus:ring-blue-500"
            placeholder="00000-000"
            disabled={cepLoading}
          />
          <Button
            onClick={handleCepCheck}
            disabled={cepLoading}
            className="bg-blue-600 text-white"
          >
            {cepLoading ? 'Verificando...' : 'Verificar'}
          </Button>
        </div>
        {cepResult && (
          <p className={`mt-3 text-sm font-semibold ${cepResult.type === 'success' ? 'text-green-600' : 'text-red-500'
            }`}>
            {cepResult.message}
          </p>
        )}
      </div>

      <div className="mb-6">
        <Button variant="outline" className="w-full" onClick={handleOpenCompareModal}>
          <Scale className="mr-2 h-4 w-4" />
          Comparar com outro produto
        </Button>
      </div>

      <RatingStars productId={id} user={user} />

      <div className="border-t pt-4">
        <h3 className="text-lg font-semibold mb-2">Deixe seu comentário</h3>
        <textarea
          className="w-full border rounded-lg p-2 mb-2"
          rows="3"
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="O que achou do produto?"
        />
        <Button onClick={handleAddComment} className="bg-blue-600 text-white">
          Enviar
        </Button>
      </div>
      <div className="mt-6">
        <h3 className="text-lg font-semibold mb-3">Comentários</h3>
        {reviews.length === 0 ? (
          <p className="text-gray-500">Nenhum comentário ainda.</p>
        ) : (
          reviews.map((r, i) => (
            <div key={i} className="border-b py-3 flex justify-between items-start">
              <div>
                <p className="font-semibold">{r.user_name}</p>
                <p className="text-gray-700">{r.comment}</p>
                <p className="text-sm text-gray-400">{r.created_at}</p>
              </div>
              {user?.is_admin && (
                <button
                  onClick={() => handleDeleteComment(r.id)}
                  className="text-red-600 hover:underline text-sm"
                >
                  Deletar
                </button>
              )}
            </div>
          ))
        )}
      </div>

      {renderCompareModal()}

    </div>
  );
}