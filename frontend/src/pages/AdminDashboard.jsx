import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Users, Package, MessageSquare, Star, HelpCircle, Share2 } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
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
  Legend
} from 'recharts'
import { dashboardService } from '@/services/api'

const monthNames = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"];

export default function AdminDashboard({ user }) {
  const navigate = useNavigate()

  const [stats, setStats] = useState({
    total_users: 0,
    total_products: 0,
    total_tips: 0,
    total_reviews: 0,
    total_faqs: 0,
    total_socialMedia: 0
  })

  const [pieData, setPieData] = useState([])
  const [barData, setBarData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true)
        const [statsRes, growthRes] = await Promise.all([
          dashboardService.getStats(),
          dashboardService.getUserGrowth()
        ])

        setStats({
          total_users: statsRes.total_users || 0,
          total_products: statsRes.total_products || 0,
          total_tips: statsRes.total_tips || 0,
          total_reviews: statsRes.total_reviews || 0,
          total_faqs: 0,
          total_socialMedia: 0
        });

        const contentData = [
          { name: 'Produtos', value: statsRes.total_products || 0 },
          { name: 'Dicas', value: statsRes.total_tips || 0 },
          { name: 'Reviews', value: statsRes.total_reviews || 0 }
        ]
        setPieData(contentData)

        const userGrowthData = growthRes.growth.map(item => ({
          month: monthNames[item.month - 1],
          users: item.total
        }))
        setBarData(userGrowthData)

      } catch (error) {
        console.error("Falha ao carregar dados do dashboard:", error)
      } finally {
        setLoading(false)
      }
    }

    if(user && user.isAdmin) {
        loadDashboardData()
    }

    loadDashboardData()
  }, [user, navigate])

  const COLORS = ['#3b82f6', '#22c55e', '#facc15']

  if (!user || !user.isAdmin) return null

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold mb-8 text-foreground">Painel Administrativo</h1>
        <p className="text-center text-lg">Carregando dados do dashboard...</p>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8 text-foreground">Painel Administrativo</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Usuários</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_users}</div>
            <p className="text-xs text-muted-foreground">Total de usuários cadastrados</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Produtos</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_products}</div>
            <p className="text-xs text-muted-foreground">Produtos no catálogo</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Dicas</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_tips}</div>
            <p className="text-xs text-muted-foreground">Dicas e artigos postados</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Reviews</CardTitle>
            <Star className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_reviews}</div>
            <p className="text-xs text-muted-foreground">Total de avaliações</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-10">
        <Card>
          <CardHeader>
            <CardTitle>Distribuição de Conteúdo</CardTitle>
            <CardDescription>Proporção entre produtos, dicas e reviews</CardDescription>
          </CardHeader>
          <CardContent className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              {pieData.length > 0 ? (
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    label
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              ) : (
                <div className="flex items-center justify-center h-full text-muted-foreground">
                  Sem dados para exibir
                </div>
              )}
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Crescimento de Usuários</CardTitle>
            <CardDescription>Evolução de usuários cadastrados por mês</CardDescription>
          </CardHeader>
          <CardContent className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              {barData.length > 0 ? (
                <BarChart data={barData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="users" fill="#3b82f6" />
                </BarChart>
              ) : (
                <div className="flex items-center justify-center h-full text-muted-foreground">
                  Sem dados para exibir
                </div>
              )}
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Abas de gerenciamento */}
      <Tabs defaultValue="users" className="space-y-4">
        <TabsList>
          <TabsTrigger value="users">Usuários</TabsTrigger>
          <TabsTrigger value="products">Produtos</TabsTrigger>
          <TabsTrigger value="faqs">FAQs</TabsTrigger>
          <TabsTrigger value="social">Redes Sociais</TabsTrigger>
        </TabsList>

        <TabsContent value="users" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Gerenciar Usuários</CardTitle>
              <CardDescription>Visualize, edite e exclua usuários</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground mb-4">
                Lista de usuários cadastrados no sistema
              </p>
              <Button>Ver Todos os Usuários</Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="products" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Gerenciar Produtos</CardTitle>
              <CardDescription>Crie, edite e exclua produtos do catálogo</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground mb-4">
                Gerencie o catálogo de produtos
              </p>
              <div className="flex gap-2">
                <Button>Novo Produto</Button>
                <Button variant="outline">Ver Produtos</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="faqs" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Gerenciar FAQs</CardTitle>
              <CardDescription>Crie e edite perguntas frequentes</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground mb-4">
                Mantenha as perguntas frequentes atualizadas
              </p>
              <div className="flex gap-2">
                <Button>Nova FAQ</Button>
                <Button variant="outline">Ver FAQs</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="social" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Gerenciar Redes Sociais</CardTitle>
              <CardDescription>Configure os links das redes sociais</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground mb-4">
                Adicione e edite links das redes sociais
              </p>
              <div className="flex gap-2">
                <Button>Nova Rede Social</Button>
                <Button variant="outline">Ver Links</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}