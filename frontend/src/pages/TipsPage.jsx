import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Lightbulb } from 'lucide-react'
import { tipService } from '@/services/api'

export default function TipsPage({ user }) {
  const [tips, setTips] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [newTip, setNewTip] = useState({ title: '', content: '', category: '' })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadTips()
  }, [])

  const loadTips = async () => {
    try {
      setLoading(true)
      const response = await tipService.getAll()
      setTips(response.tips || [])
      setError('')
    } catch (err) {
      setError('Erro ao carregar dicas')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!user) {
      alert('Você precisa estar logado para criar dicas')
      return
    }

    if (!user.is_admin) {
      alert('Apenas administradores podem criar novas dicas.')
      return
    }

    try {
      await tipService.create(newTip.title, newTip.content, newTip.category)
      setNewTip({ title: '', content: '', category: '' })
      setShowForm(false)
      loadTips()
    } catch (err) {
      alert(err.message || 'Erro ao criar dica')
    }
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <p className="text-center">Carregando dicas...</p>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-bold text-foreground">Dicas e Orientações</h1>

        {/* 🔒 Botão visível apenas para administradores */}
        {user?.is_admin && (
          <Button onClick={() => setShowForm(!showForm)}>
            {showForm ? 'Cancelar' : 'Nova Dica'}
          </Button>
        )}
      </div>

      {error && (
        <div className="bg-destructive/10 text-destructive px-4 py-2 rounded-md mb-4">
          {error}
        </div>
      )}

      {/* 🔒 Formulário só aparece para administradores */}
      {showForm && user?.is_admin && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Compartilhe sua dica</CardTitle>
            <CardDescription>
              Ajude outros usuários com suas experiências (apenas administradores)
            </CardDescription>
          </CardHeader>
          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="title">Título</Label>
                <Input
                  id="title"
                  value={newTip.title}
                  onChange={(e) => setNewTip({ ...newTip, title: e.target.value })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="category">Categoria (opcional)</Label>
                <Input
                  id="category"
                  value={newTip.category}
                  onChange={(e) => setNewTip({ ...newTip, category: e.target.value })}
                  placeholder="Ex: Manutenção, Instalação, etc."
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="content">Conteúdo</Label>
                <Textarea
                  id="content"
                  rows={4}
                  value={newTip.content}
                  onChange={(e) => setNewTip({ ...newTip, content: e.target.value })}
                  required
                />
              </div>
              <Button type="submit" className="w-full">
                Publicar Dica
              </Button>
            </CardContent>
          </form>
        </Card>
      )}

      {tips.length === 0 ? (
        <p className="text-center text-muted-foreground">Nenhuma dica disponível.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {tips.map((tip) => (
            <Card key={tip.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start space-x-3">
                  <Lightbulb className="h-6 w-6 text-secondary flex-shrink-0 mt-1" />
                  <div className="flex-grow">
                    <CardTitle className="text-xl mb-2">{tip.title}</CardTitle>
                    {tip.category && (
                      <span className="text-xs text-muted-foreground bg-muted px-2 py-1 rounded mb-2 inline-block">
                        {tip.category}
                      </span>
                    )}
                    <CardDescription>{tip.content}</CardDescription>
                  </div>
                </div>
              </CardHeader>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
