import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from "@/components/ui/checkbox"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

import { authService } from '@/services/api'
import logo from '../assets/logo.png'

const TermsAndConditions = () => (
  <div className="max-h-[60vh] overflow-y-auto pr-4 space-y-2 text-sm text-muted-foreground">
    <p><strong>Última atualização:</strong> 05 de Novembro de 2025</p>
    <p>Bem-vindo à PiFloor Pisos! Ao criar uma conta e utilizar nossos serviços, você concorda em cumprir os seguintes termos e condições:</p>

    <h3 className="font-semibold text-foreground pt-2">1. Uso da Conta</h3>
    <p>Você é inteiramente responsável por manter a confidencialidade de sua senha e conta. Você concorda em notificar imediatamente a PiFloor sobre qualquer uso não autorizado de sua conta.</p>

    <h3 className="font-semibold text-foreground pt-2">2. Coleta de Dados</h3>
    <p>Coletamos dados como nome, e-mail e nome de usuário para fornecer e melhorar nossos serviços. Não compartilharemos seus dados pessoais com terceiros sem seu consentimento explícito, exceto quando exigido por lei.</p>

    <h3 className="font-semibold text-foreground pt-2">3. Conduta do Usuário</h3>
    <p>Você concorda em não usar o serviço para postar ou transmitir qualquer material que seja ilegal, difamatório, ofensivo ou que infrinja os direitos de terceiros.</p>

    <h3 className="font-semibold text-foreground pt-2">4. Produtos e Serviços</h3>
    <p>As informações sobre produtos, como preços e estoque, estão sujeitas a alterações sem aviso prévio. Tentamos ser o mais precisos possível, mas não garantimos que as descrições dos produtos ou outros conteúdos sejam livres de erros.</p>

    <h3 className="font-semibold text-foreground pt-2">5. Limitação de Responsabilidade</h3>
    <p>A PiFloor não será responsável por quaisquer danos diretos ou indiretos resultantes do uso ou da incapacidade de usar nossos serviços.</p>
  </div>
);


export default function RegisterPage() {
  const [formData, setFormData] = useState({
    name: '',
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const [agreed, setAgreed] = useState(false)

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!agreed) {
      setError('Você deve aceitar os termos de uso para continuar.')
      return
    }

    if (formData.password !== formData.confirmPassword) {
      setError('As senhas não coincidem')
      return
    }

    if (formData.password.length < 6) {
      setError('A senha deve ter pelo menos 6 caracteres')
      return
    }

    setLoading(true)

    try {
      await authService.register(
        formData.username,
        formData.email,
        formData.password,
        formData.name
      )

      navigate('/login', {
        state: { message: 'Cadastro realizado com sucesso! Faça login para continuar.' }
      })
    } catch (err) {
      setError(err.message || 'Erro ao cadastrar usuário')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center bg-muted py-12 px-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            <img src={logo} alt="PiFloor Logo" className="h-20 w-20" />
          </div>
          <CardTitle className="text-2xl">Criar Conta</CardTitle>
          <CardDescription>Preencha os dados para se cadastrar</CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            {error && (
              <div className="bg-destructive/10 text-destructive px-4 py-2 rounded-md text-sm">
                {error}
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="name">Nome Completo</Label>
              <Input id="name" name="name" type="text" placeholder="Seu nome" value={formData.name} onChange={handleChange} required disabled={loading} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="username">Nome de usuário</Label>
              <Input id="username" name="username" type="text" placeholder="seu_usuario" value={formData.username} onChange={handleChange} required disabled={loading} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">E-mail</Label>
              <Input id="email" name="email" type="email" placeholder="seu@email.com" value={formData.email} onChange={handleChange} required disabled={loading} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Senha</Label>
              <Input id="password" name="password" type="password" placeholder="••••••••" value={formData.password} onChange={handleChange} required disabled={loading} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirmar Senha</Label>
              <Input id="confirmPassword" name="confirmPassword" type="password" placeholder="••••••••" value={formData.confirmPassword} onChange={handleChange} required disabled={loading} />
            </div>

            <div className="flex items-center space-x-2 pt-2">
              <Checkbox
                id="terms"
                checked={agreed}
                onCheckedChange={setAgreed}
                disabled={loading}
              />
              <Label htmlFor="terms" className="text-sm font-medium leading-none text-muted-foreground">
                Eu li e aceito os{" "}
                <Dialog>
                  <DialogTrigger asChild>
                    <span className="text-primary hover:underline cursor-pointer">
                      Termos de Uso
                    </span>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-[600px]">
                    <DialogHeader>
                      <DialogTitle>Termos de Uso</DialogTitle>
                    </DialogHeader>
                    <TermsAndConditions />
                  </DialogContent>
                </Dialog>
              </Label>
            </div>

          </CardContent>
          <CardFooter className="flex flex-col space-y-4 pt-4">

            <Button
              type="submit"
              className="w-full"
              disabled={loading || !agreed}
            >
              {loading ? 'Cadastrando...' : 'Cadastrar'}
            </Button>

            <p className="text-sm text-center text-muted-foreground">
              Já tem uma conta?{' '}
              <Link to="/login" className="text-primary hover:underline font-semibold">
                Faça login
              </Link>
            </p>
          </CardFooter>
        </form>
      </Card>
    </div>
  )
}