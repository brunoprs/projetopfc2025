import google.generativeai as genai
import os
from dotenv import load_dotenv 

# 1. Carrega as variáveis do arquivo .env
load_dotenv() 

# 2. Pega a chave (do .env)
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("--- ERRO ---")
    print("A variável de ambiente GOOGLE_API_KEY não foi encontrada no .env")
    print("Verifique se o nome está correto (GOOGLE_API_KEY) e se a chave é válida.")
else:
    # 3. Configura o genai com a chave
    genai.configure(api_key=api_key)
    
    try:
        print("Buscando modelos compatíveis com 'generateContent'...")
        print("-------------------------------------------------")
        found_models = False
        
        # 4. Lista os modelos
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"✅ {m.name}") # Este é o nome que precisamos!
                found_models = True
        
        if not found_models:
            print("\nNenhum modelo compatível com 'generateContent' foi encontrado.")
            print("Isso pode ser um problema com a sua chave de API ou permissões.")
            
    except Exception as e:
        print(f"\n--- ERRO AO CONECTAR NA API ---")
        print(f"Ocorreu um erro ao listar os modelos: {e}")
        print("Verifique se sua chave de API é válida e se a 'Generative Language API' está ativada no seu projeto Google Cloud.")