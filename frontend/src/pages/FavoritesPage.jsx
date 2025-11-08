import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Heart } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { favoriteService, productService } from '@/services/api'

export default function FavoritesPage({ user }) {
  const navigate = useNavigate()
  const [favorites, setFavorites] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!user) {
      navigate('/login')
      return
    }

    loadFavorites()
  }, [user, navigate])

  const loadFavorites = async () => {
    try {
      setLoading(true)
      const [favoritesResponse, productsResponse] = await Promise.all([
        favoriteService.getAll(),
        productService.getAll()
      ])

      const favoriteProductIds = favoritesResponse.favorites.map(f => f.product_id)
      const favoriteProducts = productsResponse.products.filter(p => 
        favoriteProductIds.includes(p.id)
      )

      setFavorites(favoriteProducts)
      setError('')
    } catch (err) {
      setError('Erro ao carregar favoritos')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const removeFavorite = async (productId) => {
    try {
      await favoriteService.remove(productId)
      setFavorites(prev => prev.filter(p => p.id !== productId))
    } catch (err) {
      console.error('Erro ao remover favorito:', err)
      alert(err.message || 'Erro ao remover favorito')
    }
  }

  const getCategoryLabel = (type) => {
    const categories = {
      'laminado': 'Laminado',
      'vinilico': 'Vinílico',
      'porcelanato': 'Porcelanato',
      'madeira': 'Madeira'
    }
    return categories[type] || type
  }

  if (!user) return null

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <p className="text-center">Carregando favoritos...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-destructive/10 text-destructive px-4 py-2 rounded-md">
          {error}
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8 text-foreground">Meus Favoritos</h1>

      {favorites.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Heart className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
            <p className="text-xl text-muted-foreground mb-4">
              Você ainda não tem produtos favoritos
            </p>
            <Button onClick={() => navigate('/produtos')}>
              Ver Produtos
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {favorites.map((product) => (
            <Card key={product.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex justify-between items-start">
                  {product.image_url ? (
                    <img 
                      src={product.image_url} 
                      alt={product.name}
                      className="w-full h-48 object-cover rounded-md mb-4"
                    />
                  ) : (
                    <div className="w-full h-48 bg-muted rounded-md mb-4 flex items-center justify-center">
                      <span className="text-4xl">🏠</span>
                    </div>
                  )}
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => removeFavorite(product.id)}
                    className="text-red-500 absolute top-4 right-4"
                  >
                    <Heart className="h-5 w-5" fill="currentColor" />
                  </Button>
                </div>
                <div className="flex items-center justify-between">
                  <CardTitle>{product.name}</CardTitle>
                  {product.type && (
                    <Badge variant={product.type === 'laminado' ? 'default' : 'secondary'}>
                      {getCategoryLabel(product.type)}
                    </Badge>
                  )}
                </div>
                <CardDescription>{product.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold text-primary">
                  R$ {Number(product.price).toFixed(2)}/m²
                </p>
              </CardContent>
              <CardFooter>
                <Button className="w-full">Ver Detalhes</Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

