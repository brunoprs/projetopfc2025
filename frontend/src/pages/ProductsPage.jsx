import React, { useEffect, useState, useMemo } from 'react'
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
  CardDescription
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Heart, Search } from 'lucide-react'
import { FaWhatsapp } from 'react-icons/fa6'
import { useNavigate } from 'react-router-dom'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

export default function ProductsPage({ user }) {
  const [products, setProducts] = useState([])
  const [favorites, setFavorites] = useState([])
  const [filter, setFilter] = useState('all')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)

  const navigate = useNavigate()
  const whatsappNumber = '5511999924733'

  // CARREGAR FAVORITOS (quando tiver user)
  const loadFavorites = async () => {
    try {
      const token = localStorage.getItem('token')
      if (!token) return

      const res = await fetch(`${API_BASE_URL}/favorites`, {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        }
      })

      if (!res.ok) return

      const data = await res.json()
      const favoriteIds = (data.favorites || []).map(f => f.id || f.product_id)
      setFavorites(favoriteIds)
    } catch (err) {
      console.error('Erro ao carregar favoritos:', err)
    }
  }

  // CARREGAR PRODUTOS (com search + paginação)
  const loadProducts = async (searchText = '', pageNumber = 1) => {
    try {
      setLoading(true)

      const params = new URLSearchParams()
      if (searchText) params.append('search', searchText)
      params.append('page', pageNumber)
      params.append('per_page', 10)

      const url = `${API_BASE_URL}/products?${params.toString()}`
      const res = await fetch(url)

      if (!res.ok) {
        throw new Error(`Erro HTTP ${res.status}`)
      }

      const data = await res.json()
      const baseProducts = data.products || []

      // busca rating de cada produto
      const productsWithRatings = await Promise.all(
        baseProducts.map(async p => {
          try {
            const rRes = await fetch(
              `${API_BASE_URL}/products/${p.id}/rating`
            )
            const rData = await rRes.json()
            return { ...p, average_rating: rData.average }
          } catch {
            return { ...p, average_rating: null }
          }
        })
      )

      setProducts(productsWithRatings)
      setPage(data.page || pageNumber)
      setTotalPages(data.pages || 1)
      setError('')
    } catch (err) {
      console.error('Erro ao carregar produtos:', err)
      setError('Erro ao carregar produtos')
    } finally {
      setLoading(false)
    }
  }

  // MONTAGEM: carrega produtos (página 1) + favoritos
  useEffect(() => {
    loadProducts('', 1)
    if (user) {
      loadFavorites()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user])

  // DEBOUNCE DA BUSCA: quando search mudar, volta pra página 1
  useEffect(() => {
    const timer = setTimeout(() => {
      loadProducts(search, 1)
      setPage(1)
    }, 500)

    return () => clearTimeout(timer)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search])

  const toggleFavorite = async productId => {
    if (!user) {
      navigate('/login')
      return
    }

    try {
      const token = localStorage.getItem('token')
      if (!token) {
        navigate('/login')
        return
      }

      if (favorites.includes(productId)) {
        // remover
        await fetch(`${API_BASE_URL}/favorites/${productId}`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
          }
        })
        setFavorites(prev => prev.filter(id => id !== productId))
      } else {
        // adicionar
        await fetch(`${API_BASE_URL}/favorites`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
          },
          body: JSON.stringify({ product_id: productId })
        })
        setFavorites(prev => [...prev, productId])
      }
    } catch (err) {
      console.error('Erro ao atualizar favorito:', err)
      alert(err.message || 'Erro ao atualizar favorito')
    }
  }

  const getCategoryLabel = type => {
    const categories = {
      laminado: 'Laminado',
      vinilico: 'Vinílico',
      porcelanato: 'Porcelanato',
      madeira: 'Madeira'
    }
    return categories[type] || type
  }

  const handleWhatsappClick = productName => {
    const message = encodeURIComponent(
      `Olá! Gostaria de fazer uma cotação do produto ${productName}.`
    )
    const url = `https://wa.me/${whatsappNumber}?text=${message}`
    window.open(url, '_blank')
  }

  // PAGINAÇÃO: mudar de página
  const handlePageChange = newPage => {
    if (newPage < 1 || newPage > totalPages) return
    setPage(newPage)
    loadProducts(search, newPage)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  // FILTRO FINAL: CATEGORIA + FAVORITOS
  const filteredProducts = useMemo(() => {
    let filtered = products

    // Filtro por categoria
    if (filter !== 'all' && filter !== 'favorites') {
      filtered = filtered.filter(p => p.type === filter)
    }

    // Filtro por favoritos
    if (filter === 'favorites') {
      filtered = filtered.filter(p => favorites.includes(p.id))
    }

    return filtered
  }, [products, filter, favorites])

  if (loading && products.length === 0)
    return <p className="text-center">Carregando produtos...</p>

  if (error)
    return (
      <div className="bg-destructive/10 text-destructive px-4 py-2 rounded-md">
        {error}
      </div>
    )

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8 text-foreground">
        Nossos Produtos
      </h1>

      {/* CAMPO DE BUSCA + FILTROS */}
      <div className="flex flex-col md:flex-row gap-4 mb-8">
        {/* INPUT DE BUSCA */}
        <div className="relative flex-1 md:max-w-sm">
          <Search className="absolute left-3 top-3 h-5 w-5 text-muted-foreground" />
          <input
            type="text"
            placeholder="Buscar produto ou tipo..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        {/* BOTÕES DE FILTRO */}
        <div className="flex flex-wrap gap-2">
          <Button
            variant={filter === 'all' ? 'default' : 'outline'}
            onClick={() => setFilter('all')}
          >
            Todos
          </Button>
          <Button
            variant={filter === 'laminado' ? 'default' : 'outline'}
            onClick={() => setFilter('laminado')}
          >
            Laminados
          </Button>
          <Button
            variant={filter === 'vinilico' ? 'default' : 'outline'}
            onClick={() => setFilter('vinilico')}
          >
            Vinílicos
          </Button>
          <Button
            variant={filter === 'favorites' ? 'default' : 'outline'}
            onClick={() =>
              setFilter(filter === 'favorites' ? 'all' : 'favorites')
            }
          >
            {filter === 'favorites' ? 'Mostrar Todos' : 'Favoritos'}
          </Button>
        </div>
      </div>

      {/* GRID DE PRODUTOS */}
      {filteredProducts.length === 0 ? (
        <p className="text-center text-muted-foreground">
          Nenhum produto encontrado.
        </p>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredProducts.map(product => (
              <Card
                key={product.id}
                className="hover:shadow-lg transition-shadow"
              >
                <CardHeader className="relative">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <p className="text-yellow-500">
                        {'★'.repeat(Math.round(product.average_rating || 0))}
                        {'☆'.repeat(
                          5 - Math.round(product.average_rating || 0)
                        )}
                      </p>
                      <span className="text-sm text-gray-500">
                        {product.average_rating
                          ? `${product.average_rating.toFixed(1)}/5`
                          : 'Sem notas'}
                      </span>
                    </div>

                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => toggleFavorite(product.id)}
                      className={`transition-colors ${
                        favorites.includes(product.id)
                          ? 'text-red-500 hover:text-red-600'
                          : 'text-muted-foreground hover:text-red-500'
                      }`}
                    >
                      <Heart
                        className="h-6 w-6"
                        fill={
                          favorites.includes(product.id)
                            ? 'currentColor'
                            : 'none'
                        }
                      />
                    </Button>
                  </div>

                  {product.image_url ? (
                    <img
                      src={product.image_url}
                      alt={product.name}
                      className="w-full h-48 object-cover rounded-md mb-4"
                    />
                  ) : (
                    <div className="w-full h-48 bg-muted rounded-md mb-4 flex items-center justify-center">
                      <span className="text-4xl">Home</span>
                    </div>
                  )}

                  <div className="flex items-center justify-between mt-2">
                    <CardTitle>{product.name}</CardTitle>
                    {product.type && (
                      <Badge
                        variant={
                          product.type === 'laminado' ? 'default' : 'secondary'
                        }
                      >
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
                      <button
                        type="button"
                        onClick={() => handleWhatsappClick(product.name)}
                      >
                        <FaWhatsapp className="w-6 h-6 text-green-500" />
                      </button>
                    </div>
                  </div>
                </CardContent>

                <CardFooter>
                  <Button
                    className="w-full"
                    onClick={() => navigate(`/produtos/${product.id}`)}
                  >
                    Ver Detalhes
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>

          {/* PAGINAÇÃO */}
          <div className="flex items-center justify-center gap-4 mt-8">
            <Button
              variant="outline"
              disabled={page <= 1}
              onClick={() => handlePageChange(page - 1)}
            >
              Anterior
            </Button>
            <span className="text-sm text-muted-foreground">
              Página <strong>{page}</strong> de <strong>{totalPages}</strong>
            </span>
            <Button
              variant="outline"
              disabled={page >= totalPages}
              onClick={() => handlePageChange(page + 1)}
            >
              Próxima
            </Button>
          </div>
        </>
      )}
    </div>
  )
}
