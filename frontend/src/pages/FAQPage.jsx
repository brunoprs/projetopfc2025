import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ChevronDown, ChevronUp } from 'lucide-react'
import { faqService } from '@/services/api'

export default function FAQPage() {
  const [faqs, setFaqs] = useState([])
  const [openIndex, setOpenIndex] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadFaqs()
  }, [])

  const loadFaqs = async () => {
    try {
      setLoading(true)
      const response = await faqService.getAll()
      setFaqs(response.faqs || [])
      setError('')
    } catch (err) {
      setError('Erro ao carregar FAQs')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const toggleFaq = (index) => {
    setOpenIndex(openIndex === index ? null : index)
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <p className="text-center">Carregando perguntas frequentes...</p>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-4xl font-bold mb-4 text-foreground text-center">
          Perguntas Frequentes
        </h1>
        <p className="text-lg text-muted-foreground mb-8 text-center">
          Encontre respostas para as dúvidas mais comuns
        </p>

        {error && (
          <div className="bg-destructive/10 text-destructive px-4 py-2 rounded-md mb-4">
            {error}
          </div>
        )}

        {faqs.length === 0 ? (
          <p className="text-center text-muted-foreground">Nenhuma pergunta frequente disponível.</p>
        ) : (
          <div className="space-y-4">
            {faqs.map((faq, index) => (
              <Card key={faq.id} className="overflow-hidden">
                <CardHeader
                  className="cursor-pointer hover:bg-muted/50 transition-colors"
                  onClick={() => toggleFaq(index)}
                >
                  <div className="flex justify-between items-center">
                    <CardTitle className="text-lg pr-4">{faq.question}</CardTitle>
                    {openIndex === index ? (
                      <ChevronUp className="h-5 w-5 flex-shrink-0 text-primary" />
                    ) : (
                      <ChevronDown className="h-5 w-5 flex-shrink-0 text-muted-foreground" />
                    )}
                  </div>
                </CardHeader>
                {openIndex === index && (
                  <CardContent className="pt-0">
                    <p className="text-muted-foreground">{faq.answer}</p>
                  </CardContent>
                )}
              </Card>
            ))}
          </div>
        )}

        <Card className="mt-8 bg-secondary text-secondary-foreground">
          <CardHeader>
            <CardTitle>Não encontrou sua resposta?</CardTitle>
            <CardDescription className="text-secondary-foreground/80">
              Entre em contato conosco pelo e-mail contato@pifloor.com.br ou telefone (11) 1234-5678
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    </div>
  )
}

