import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ArrowRight, CheckCircle, Star } from 'lucide-react'

export default function HomePage() {
  const features = [
    {
      title: 'Pisos Laminados',
      description: 'Durabilidade e beleza para seu ambiente',
      icon: '🏠'
    },
    {
      title: 'Pisos Vinílicos',
      description: 'Modernidade e praticidade em instalação',
      icon: '✨'
    },
    {
      title: 'Acabamentos Premium',
      description: 'Variedade de texturas e cores',
      icon: '🎨'
    }
  ]

  const benefits = [
    'Produtos de alta qualidade',
    'Garantia estendida',
    'Instalação profissional',
    'Atendimento personalizado',
    'Melhores preços do mercado',
    'Entrega rápida'
  ]

  return (
    <div>
      <section className="bg-gradient-to-br from-primary to-primary/80 text-primary-foreground py-20">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              Transforme Seu Ambiente com PiFloor
            </h1>
            <p className="text-xl md:text-2xl mb-8 opacity-90">
              Especialistas em revestimentos laminados e vinílicos de alta qualidade
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/produtos">
                <Button size="lg" variant="secondary" className="text-lg">
                  Ver Produtos
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
              <Link to="/cadastro">
                <Button size="lg" variant="outline" className="text-lg bg-transparent border-primary-foreground text-primary-foreground hover:bg-primary-foreground hover:text-primary">
                  Criar Conta
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      <section className="py-16 bg-background">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-12 text-foreground">
            Nossos Produtos
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="text-5xl mb-4">{feature.icon}</div>
                  <CardTitle className="text-2xl">{feature.title}</CardTitle>
                  <CardDescription className="text-lg">{feature.description}</CardDescription>
                </CardHeader>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section className="py-16 bg-muted">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-12 text-foreground">
            Por Que Escolher a PiFloor?
          </h2>
          <div className="max-w-3xl mx-auto">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {benefits.map((benefit, index) => (
                <div key={index} className="flex items-center space-x-3">
                  <CheckCircle className="h-6 w-6 text-secondary flex-shrink-0" />
                  <span className="text-lg">{benefit}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="py-16 bg-secondary text-secondary-foreground">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Pronto para Transformar Seu Espaço?
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Cadastre-se agora e tenha acesso a ofertas exclusivas
          </p>
          <Link to="/cadastro">
            <Button size="lg" variant="outline" className="text-lg border-secondary-foreground text-secondary-foreground hover:bg-secondary-foreground hover:text-secondary">
              Começar Agora
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </Link>
        </div>
      </section>
    </div>
  )
}