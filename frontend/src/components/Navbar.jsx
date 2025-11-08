import { Link, useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Menu, X, User, ChevronDown } from 'lucide-react'
import { useState } from 'react'
import { authService } from '@/services/api'
import logo from '../assets/logo.png'

export default function Navbar({ user, setUser }) {
  const [isOpen, setIsOpen] = useState(false)
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const navigate = useNavigate()

  const handleLogout = async () => {
    try {
      await authService.logout()
    } catch (err) {
      console.error('Erro ao fazer logout:', err)
    } finally {
      setUser(null)
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      navigate('/')
    }
  }

  const handleMyAccount = () => {
    navigate('/minha-conta')
    setUserMenuOpen(false)
  }

  return (
    <nav className="bg-primary text-primary-foreground shadow-lg sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">

          <div className="flex items-center space-x-8">
            <Link to="/" className="flex items-center space-x-3">
              <img src={logo} alt="PiFloor Logo" className="h-12 w-12" />
              <span className="text-xl font-bold">PiFloor Pisos</span>
            </Link>

            <div className="hidden md:flex items-center space-x-6">
              <Link to="/produtos" className="hover:text-secondary transition-colors">
                Produtos
              </Link>

              <Link to="/piso-ideal" className="hover:text-secondary transition-colors">
                Piso Ideal
              </Link>

              <Link to="/dicas" className="hover:text-secondary transition-colors">
                Dicas
              </Link>
              <Link to="/faq" className="hover:text-secondary transition-colors">
                FAQ
              </Link>
            </div>
          </div>

          <div className="hidden md:flex items-center space-x-6">
            {(user?.isAdmin || user?.is_admin) && (
              <Link
                to="/AdminPanel/dashboard"
                className="font-semibold hover:text-secondary transition-colors text-yellow-300"
              >
                Painel Admin
              </Link>
            )}

            {user ? (
              <div className="relative">
                <button
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                  className="flex items-center space-x-1 hover:text-secondary focus:outline-none"
                >
                  <User className="h-5 w-5" />
                  <span>{user.name}</span>
                  <ChevronDown className="h-4 w-4" />
                </button>

                {userMenuOpen && (
                  <div className="absolute right-0 mt-2 bg-white text-black rounded-md shadow-lg py-2 w-40 z-50">
                    <button
                      onClick={handleMyAccount}
                      className="block w-full text-left px-4 py-2 hover:bg-gray-100"
                    >
                      Minha Conta
                    </button>
                    <button
                      onClick={handleLogout}
                      className="block w-full text-left px-4 py-2 hover:bg-gray-100 text-red-600"
                    >
                      Sair
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <Link to="/login">
                <Button variant="secondary" size="sm">
                  Entrar
                </Button>
              </Link>
            )}
          </div>

          {/* Botão Mobile */}
          <button
            className="md:hidden"
            onClick={() => setIsOpen(!isOpen)}
          >
            {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>

        {/* Menu Mobile */}
        {isOpen && (
          <div className="md:hidden pb-4 space-y-2">
            <Link to="/produtos" className="block py-2 hover:text-secondary transition-colors">
              Produtos
            </Link>

            <Link to="/piso-ideal" className="block py-2 hover:text-secondary transition-colors">
              Piso Ideal
            </Link>

            <Link to="/dicas" className="block py-2 hover:text-secondary transition-colors">
              Dicas
            </Link>
            <Link to="/faq" className="block py-2 hover:text-secondary transition-colors">
              FAQ
            </Link>

            {(user?.isAdmin || user?.is_admin) && (
              <Link
                to="/AdminPanel/dashboard"
                className="block py-2 hover:text-secondary transition-colors font-semibold text-yellow-300"
              >
                Painel Admin
              </Link>
            )}

            {user ? (
              <>
                <button
                  onClick={handleMyAccount}
                  className="block w-full text-left py-2 hover:text-secondary transition-colors"
                >
                  Minha Conta
                </button>
                <button
                  onClick={handleLogout}
                  className="block w-full text-left py-2 hover:text-secondary transition-colors text-red-400"
                >
                  Sair
                </button>
              </>
            ) : (
              <Link to="/login" className="block pt-2">
                <Button variant="secondary" className="w-full">
                  Entrar
                </Button>
              </Link>
            )}
          </div>
        )}
      </div>
    </nav>
  )
}
