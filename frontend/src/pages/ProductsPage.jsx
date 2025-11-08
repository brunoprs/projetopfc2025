import React, { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Heart } from 'lucide-react'
import { FaWhatsapp } from "react-icons/fa6";
import { useNavigate } from 'react-router-dom'
import { productService, favoriteService } from '@/services/api'

export default function ProductsPage({ user }) {
  const [products, setProducts] = useState([])
  const [favorites, setFavorites] = useState([])
  const [filter, setFilter] = useState('all')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const whatsappNumber = "5511998771144"

  useEffect(() => {
    loadProducts()
    if (user) loadFavorites()
  }, [user])

  const loadProducts = async () => {
    try {
      setLoading(true)
      const response = await productService.getAll()
      const baseProducts = response.products || []

      const productsWithRatings = await Promise.all(
        baseProducts.map(async (p) => {
          try {
            const res = await fetch(`http://localhost:5000/products/${p.id}/rating`)
            const data = await res.json()
            return { ...p, average_rating: data.average }
          } catch {
            return { ...p, average_rating: null }
          }
        })
      )

      setProducts(productsWithRatings)
      setError('')
    } catch (err) {
      setError('Erro ao carregar produtos')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const loadFavorites = async () => {
    try {
      const response = await favoriteService.getAll()
      const favoriteIds = response.favorites.map(f => f.id || f.product_id)
      setFavorites(favoriteIds)
    } catch (err) {
      console.error('Erro ao carregar favoritos:', err)
    }
  }

  const toggleFavorite = async (productId) => {
    if (!user) {
      navigate('/login')
      return
    }

    try {
      if (favorites.includes(productId)) {
        await favoriteService.remove(productId)
        setFavorites(prev => prev.filter(id => id !== productId))
      } else {
        await favoriteService.add(productId)
        setFavorites(prev => [...prev, productId])
      }
    } catch (err) {
      console.error('Erro ao atualizar favorito:', err)
      alert(err.message || 'Erro ao atualizar favorito')
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

  const handleWhatsappClick = (productName) => {
    const message = encodeURIComponent(
      `Olá! Gostaria de fazer uma cotação do produto ${productName}.`
    )
    const url = `https://wa.me/${whatsappNumber}?text=${message}`
    window.open(url, "_blank")
  }

  const filteredProducts = (() => {
    if (filter === 'all') return products
    if (filter === 'favorites') return products.filter(p => favorites.includes(p.id))
    return products.filter(p => p.type === filter)
  })()

  if (loading) return <p className="text-center">Carregando produtos...</p>
  if (error) return <div className="bg-destructive/10 text-destructive px-4 py-2 rounded-md">{error}</div>

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8 text-foreground">Nossos Produtos</h1>

      <div className="flex flex-wrap gap-4 mb-8">
        <Button variant={filter === 'all' ? 'default' : 'outline'} onClick={() => setFilter('all')}>Todos</Button>
        <Button variant={filter === 'laminado' ? 'default' : 'outline'} onClick={() => setFilter('laminado')}>Laminados</Button>
        <Button variant={filter === 'vinilico' ? 'default' : 'outline'} onClick={() => setFilter('vinilico')}>Vinílicos</Button>

        <Button variant={filter === 'favorites' ? 'default' : 'outline'} onClick={() => setFilter(filter === 'favorites' ? 'all' : 'favorites')}>
          {filter === 'favorites' ? 'Mostrar Todos' : 'Favoritos ❤️'}
        </Button>
      </div>

      {filteredProducts.length === 0 ? (
        <p className="text-center text-muted-foreground">Nenhum produto encontrado.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProducts.map(product => (
            <Card key={product.id} className="hover:shadow-lg transition-shadow">
              <CardHeader className="relative">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <p className="text-yellow-500">
                      {"★".repeat(Math.round(product.average_rating || 0))}
                      {"☆".repeat(5 - Math.round(product.average_rating || 0))}
                    </p>
                    <span className="text-sm text-gray-500">
                      {product.average_rating ? `${product.average_rating.toFixed(1)}/5` : "Sem notas"}
                    </span>
                  </div>

                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => toggleFavorite(product.id)}
                    className={`transition-colors ${favorites.includes(product.id)
                      ? 'text-red-500 hover:text-red-600'
                      : 'text-muted-foreground hover:text-red-500'
                      }`}
                  >
                    <Heart className="h-6 w-6" fill={favorites.includes(product.id) ? 'currentColor' : 'none'} />
                  </Button>
                </div>

                {product.image_url ? (
                  <img src={product.image_url} alt={product.name} className="w-full h-48 object-cover rounded-md mb-4" />
                ) : (
                  <div className="w-full h-48 bg-muted rounded-md mb-4 flex items-center justify-center">
                    <span className="text-4xl">🏠</span>
                  </div>
                )}

                <div className="flex items-center justify-between mt-2">
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
                <div className="flex items-center justify-between">
                  <p className="text-2xl font-bold text-primary">
                    R$ {Number(product.price).toFixed(2)}/m²
                  </p>
                  <div className="flex space-x-2">
                    <button onClick={() => handleWhatsappClick(product.name)}>
                      <FaWhatsapp className="w-6 h-6 text-green-500" />
                    </button>
                  </div>
                </div>
              </CardContent>

              <CardFooter>
                <Button className="w-full" onClick={() => navigate(`/produtos/${product.id}`)}>
                  Ver Detalhes
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}