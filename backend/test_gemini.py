"""
Teste de integração com Google Gemini (OPCIONAL).

Este teste só roda se a biblioteca google-generativeai estiver instalada.
Para instalar: pip install google-generativeai
"""
import os
import pytest

# Tenta importar Gemini (opcional)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Pula todos os testes deste arquivo se Gemini não estiver disponível
pytestmark = pytest.mark.skipif(
    not GEMINI_AVAILABLE,
    reason="google-generativeai não está instalado. Instale com: pip install google-generativeai"
)


def test_gemini_api_key_and_models():
    """Testa se a API key do Gemini está configurada e lista modelos disponíveis."""
    from dotenv import load_dotenv
    
    # Carrega variáveis do .env
    load_dotenv()
    
    # Pega a chave
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        pytest.skip("GOOGLE_API_KEY não configurada no .env")
    
    # Configura o genai
    genai.configure(api_key=api_key)
    
    # Lista modelos
    found_models = False
    compatible_models = []
    
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            compatible_models.append(m.name)
            found_models = True
    
    # Assertions
    assert found_models, "Nenhum modelo compatível com 'generateContent' foi encontrado"
    assert len(compatible_models) > 0, "Lista de modelos está vazia"
    
    print(f"\n✅ Modelos compatíveis encontrados: {compatible_models}")


def test_gemini_simple_generation():
    """Testa geração simples de texto com Gemini."""
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        pytest.skip("GOOGLE_API_KEY não configurada no .env")
    
    genai.configure(api_key=api_key)
    
    # Lista modelos disponíveis e escolhe o primeiro com generateContent
    available_model = None
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_model = m.name
                break
    except Exception as e:
        pytest.skip(f"Erro ao listar modelos: {e}")
    
    if not available_model:
        pytest.skip("Nenhum modelo Gemini disponível com generateContent")
    
    # Usa o modelo disponível
    model = genai.GenerativeModel(available_model)
    
    # Gera resposta simples
    response = model.generate_content("Diga apenas 'OK' se você está funcionando")
    
    # Verifica se houve resposta
    assert response is not None
    assert response.text is not None
    assert len(response.text) > 0
    
    print(f"\n✅ Modelo usado: {available_model}")
    print(f"✅ Resposta do Gemini: {response.text}")


if __name__ == "__main__":
    """Permite executar o teste diretamente: python test_gemini.py"""
    if not GEMINI_AVAILABLE:
        print("❌ google-generativeai não está instalado")
        print("Instale com: pip install google-generativeai")
    else:
        print("✅ google-generativeai está instalado")
        print("\nExecutando testes...")
        pytest.main([__file__, "-v"])
