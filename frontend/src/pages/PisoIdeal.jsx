import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Link } from "react-router-dom";
import api from "@/services/api";

export default function PisoIdeal() {
  const questions = [
    {
      id: 1,
      question: "O piso é para qual tipo de área?",
      options: ["Residencial", "Comercial"],
    },
    {
      id: 2,
      question: "Qual o tipo de ambiente?",
      options: ["Casa", "Apartamento"],
    },
    {
      id: 3,
      question: "Onde o piso será instalado?",
      options: ["Sala", "Cozinha", "Banheiro", "Área externa", "Quarto", "Corredor"],
    },
    {
      id: 4,
      question: "O local tem contato com água ou umidade?",
      options: ["Sim", "Não"],
    },
    {
      id: 5,
      question: "Meu piso precisa ter... (pode escolher mais de uma opção)",
      options: [
        "Resistente à água",
        "Proteção antibacteriana",
        "Conforto térmico",
        "Conforto acústico",
        "Antiderrapante",
        "Fácil de limpar",
      ],
      multiple: true,
    },
    {
      id: 6,
      question: "O piso que eu prefiro é...",
      options: ["Piso Vinílico", "Piso Laminado"],
    },
  ];

  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [isFinished, setIsFinished] = useState(false);
  const [loadingResult, setLoadingResult] = useState(false);
  const [recommendations, setRecommendations] = useState([]);
  const [allProducts, setAllProducts] = useState([]);
  const [loadingProducts, setLoadingProducts] = useState(true);

  const progress = ((currentQuestion + 1) / questions.length) * 100;
  const current = questions[currentQuestion];

  useEffect(() => {
    const fetchAllProducts = async () => {
      try {
        setLoadingProducts(true);
        const data = await api.productService.getAll();
        setAllProducts(data.products || []);
      } catch (err) {
        console.error("Erro ao carregar lista de produtos:", err);
      } finally {
        setLoadingProducts(false);
      }
    };
    fetchAllProducts();
  }, []);

  function handleAnswer(option) {
    if (current.multiple) {
      const currentAnswers = answers[current.id] || [];
      const newSelection = currentAnswers.includes(option)
        ? currentAnswers.filter((o) => o !== option)
        : [...currentAnswers, option];
      setAnswers((prev) => ({ ...prev, [current.id]: newSelection }));
    } else {
      setAnswers((prev) => ({ ...prev, [current.id]: option }));
    }
  }

  function nextQuestion() {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion((prev) => prev + 1);
    } else {
      handleFinishQuiz();
    }
  }

  function previousQuestion() {
    if (currentQuestion > 0) {
      setCurrentQuestion((prev) => prev - 1);
    }
  }

  function handleFinishQuiz() {
    setIsFinished(true);
    setLoadingResult(true);

    setTimeout(() => {
      try {
        const pisos = getRecommendations(answers);
        setRecommendations(pisos);
      } catch (error) {
        console.error("Erro ao calcular recomendações:", error);
      } finally {
        setLoadingResult(false);
      }
    }, 1000);
  }

  function getRecommendations(answers) {
    const caracteristicas = answers[5] || [];
    const umidade = answers[4] === "Sim";
    const local = answers[3];
    const preferencia = answers[6];
    const tipoAmbiente = answers[2];

    const pontuacoes = allProducts.map((product) => {
      let score = 0;
      const desc = ((product.description || "") + (product.name || "")).toLowerCase();
      const type = (product.type || "").toLowerCase();

      // Filtro de Preferência (Penalidade Alta)
      if (preferencia === "Piso Vinílico" && type !== 'vinilico') {
        score -= 50;
      }
      if (preferencia === "Piso Laminado" && type !== 'laminado') {
        score -= 50;
      }

      // Filtro de Umidade (Penalidade Alta)
      const localUMIDO = (umidade || ['Cozinha', 'Banheiro', 'Área externa'].includes(local));

      if (localUMIDO && type === 'laminado') {
        score -= 50; // Penalidade alta para laminado em área úmida
      }
      if (localUMIDO && type === 'vinilico') {
        score += 5; // Bônus para vinílico em área úmida
      }

      // Pontuação de Características
      if (caracteristicas.includes("Conforto acústico") && (desc.includes('acústico') || type === 'vinilico')) {
        score += 3;
      }
      if (caracteristicas.includes("Conforto térmico") && (desc.includes('térmico') || type === 'laminado')) {
        score += 3;
      }
      if (caracteristicas.includes("Fácil de limpar") && (desc.includes('fácil de limpar') || desc.includes('limpeza'))) {
        score += 2;
      }
      if (caracteristicas.includes("Resistente à água") && (desc.includes('resistente à água') || desc.includes('umidade') || type === 'vinilico')) {
        score += 3;
      }

      // Pontuação de Ambiente
      if (tipoAmbiente === 'Apartamento' && (type === 'vinilico' || desc.includes('acústico'))) {
        score += 2;
      }

      return { ...product, score };
    });

    // Apenas ordena pela maior pontuação e pega os 3 primeiros.
    // Isso garante que sempre haverá 3 resultados.
    return pontuacoes
      .sort((a, b) => b.score - a.score)
      .slice(0, 3);
  }

  if (loadingProducts) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen p-6">
        <p className="text-lg text-gray-600 animate-pulse">
          Carregando produtos...
        </p>
      </div>
    )
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-gray-100 to-gray-200 p-6">
      <Card className="w-full max-w-2xl shadow-xl border-none">
        <CardContent className="p-8 space-y-8">
          <h1 className="text-3xl font-bold text-center text-gray-800">
            Encontre seu Piso Ideal 🏡
          </h1>

          {!isFinished ? (
            <>
              <Progress value={progress} className="h-3" />
              <p className="text-sm text-gray-500 text-right">
                Pergunta {currentQuestion + 1} de {questions.length}
              </p>
              <h2 className="text-xl font-semibold text-gray-800">
                {current.question}
              </h2>
              <div className="grid gap-3">
                {current.options.map((option) => {
                  const selected = current.multiple
                    ? answers[current.id]?.includes(option)
                    : answers[current.id] === option;
                  return (
                    <button
                      key={option}
                      onClick={() => handleAnswer(option)}
                      className={`p-3 border rounded-xl text-left transition ${selected
                        ? "border-blue-600 bg-blue-50 shadow-sm"
                        : "border-gray-200 hover:border-gray-400"
                        }`}
                    >
                      {option}
                    </button>
                  );
                })}
              </div>
              <div className="flex justify-between pt-4">
                <Button
                  variant="outline"
                  onClick={previousQuestion}
                  disabled={currentQuestion === 0}
                >
                  Voltar
                </Button>
                <Button
                  onClick={nextQuestion}
                  disabled={
                    current.multiple
                      ? (answers[current.id]?.length || 0) === 0
                      : !answers[current.id]
                  }
                >
                  {currentQuestion === questions.length - 1
                    ? "Ver Resultado"
                    : "Próxima"}
                </Button>
              </div>
            </>
          ) : (
            <>
              {loadingResult ? (
                <div className="text-center py-8">
                  <p className="text-lg text-gray-600 animate-pulse">
                    Calculando seu piso ideal...
                  </p>
                </div>
              ) : (
                <>
                  <h2 className="text-2xl font-bold text-center text-blue-600">
                    Pronto! Estas são as 3 melhores opções para você:
                  </h2>

                  {recommendations.length > 0 ? (
                    <div className="grid gap-4 mt-6">
                      {recommendations.map((piso, index) => (
                        <Card key={piso.id} className="border-gray-200 shadow-sm">
                          <CardContent className="p-4 flex items-center gap-4">
                            <img
                              src={piso.image_url || 'https://via.placeholder.com/100?text=Piso'}
                              alt={piso.name}
                              className="w-20 h-20 object-cover rounded-md"
                            />
                            <div className="flex-1">
                              <h3 className="text-lg font-semibold text-gray-800">
                                {index + 1}. {piso.name}
                              </h3>
                              <p className="text-gray-600 text-sm mt-1">
                                {(piso.description || "").substring(0, 100)}...
                              </p>
                              <Link to={`/produtos/${piso.id}`} className="text-sm text-blue-600 hover:underline font-medium mt-2 inline-block">
                                Ver detalhes do produto
                              </Link>
                            </div>
                            <div className="text-lg font-bold text-primary">
                              R$ {piso.price}
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  ) : (
                    <p className="text-center text-gray-700 mt-4">
                      Nenhum produto encontrado no catálogo.
                    </p>
                  )}

                  <div className="flex justify-center pt-6">
                    <Button onClick={() => window.location.reload()}>
                      Refazer Quiz
                    </Button>
                  </div>
                </>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}