import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, Package, MessageSquare, Star, BarChart3, PieChartIcon } from "lucide-react";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Legend,
  LineChart,
  Line,
} from "recharts";
import api from "@/services/api";

const monthNames = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"];
const PIE_COLORS = ['#3b82f6', '#10b981', '#f97316'];
const RATING_COLORS = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6'];

export default function AdminPublicDashboard({ user }) {
  const navigate = useNavigate();

  const [stats, setStats] = useState({
    total_users: 0,
    total_products: 0,
    total_tips: 0,
    total_reviews: 0,
    total_favorites: 0
  });

  const [userGrowthData, setUserGrowthData] = useState([]);
  const [contentPieData, setContentPieData] = useState([]);
  const [productRatingData, setProductRatingData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!user || !user.is_admin) {
      setLoading(false);
      return;
    }

    const loadDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);

        const [statsRes, growthRes, ratingsRes] = await Promise.all([
          api.dashboardService.getStats(),
          api.dashboardService.getUserGrowth(),
          api.dashboardService.getProductRatings()
        ]);

        setStats(statsRes);

        const formattedGrowthData = growthRes.map(item => ({
          month: monthNames[item.month - 1],
          NovosUsuários: item.total,
        }));
        setUserGrowthData(formattedGrowthData);

        const pieData = [
          { name: 'Produtos', value: statsRes.total_products || 0 },
          { name: 'Dicas', value: statsRes.total_tips || 0 },
          { name: 'Reviews', value: statsRes.total_reviews || 0 },
        ];
        setContentPieData(pieData);

        const formattedRatingData = ratingsRes.map(item => ({
          name: `${item.rating} Estrela${item.rating > 1 ? 's' : ''}`,
          Produtos: item.count,
          color: RATING_COLORS[item.rating - 1] || '#8884d8'
        }));
        setProductRatingData(formattedRatingData);

      } catch (err) {
        console.error("Falha ao carregar dados do dashboard:", err);
        setError("Erro ao carregar dados. Verifique o console.");
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, [user]);

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <p className="text-lg">⏳ Carregando dados do dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <p className="text-lg text-destructive">{error}</p>
        <p className="text-muted-foreground">Isso pode ser um problema de token. Tente deslogar e logar novamente.</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">

      {/* Cards de estatísticas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Usuários Totais</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_users}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Produtos</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_products}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Dicas Criadas</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_tips}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Reviews (com nota)</CardTitle>
            <Star className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_reviews}</div>
          </CardContent>
        </Card>
      </div>

      {/* Linha de Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* GRÁFICO 1: Crescimento de Usuários */}
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" /> Crescimento de Usuários
            </CardTitle>
            <CardDescription>Novos usuários cadastrados por mês.</CardDescription>
          </CardHeader>
          <CardContent className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              {userGrowthData.length > 0 ? (
                <LineChart data={userGrowthData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="NovosUsuários" stroke="#3b82f6" strokeWidth={2} />
                </LineChart>
              ) : (
                <div className="flex items-center justify-center h-full text-muted-foreground">
                  Sem dados de crescimento
                </div>
              )}
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* GRÁFICO 2: Distribuição de Conteúdo */}
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PieChartIcon className="h-5 w-5" /> Distribuição de Conteúdo
            </CardTitle>
            <CardDescription>Proporção de produtos, dicas e reviews.</CardDescription>
          </CardHeader>
          <CardContent className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              {contentPieData.some(d => d.value > 0) ? (
                <PieChart>
                  <Pie data={contentPieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                    {contentPieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              ) : (
                <div className="flex items-center justify-center h-full text-muted-foreground">
                  Sem dados de conteúdo
                </div>
              )}
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* GRÁFICO 3: Produtos por Nota */}
      <div className="grid grid-cols-1">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Star className="h-5 w-5" /> Avaliação de Produtos
            </CardTitle>
            <CardDescription>Total de produtos por nota (1 a 5 estrelas)</CardDescription>
          </CardHeader>
          <CardContent className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              {productRatingData.length > 0 ? (
                <BarChart data={productRatingData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="Produtos">
                    {productRatingData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              ) : (
                <div className="flex items-center justify-center h-full text-muted-foreground">
                  (Endpoint /admin/product-ratings não encontrado ou sem dados)
                </div>
              )}
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

    </div>
  );
}