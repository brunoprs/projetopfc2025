#!/usr/bin/env python3
"""Script para testar a API do PiFloor"""

import requests
import json
from colorama import init, Fore, Style

# Inicializar colorama para Windows
init(autoreset=True)

BASE_URL = "http://localhost:5000"

def print_header(text):
    print(f"\n{Fore.CYAN}{'='*50}")
    print(f"{Fore.CYAN}{text.center(50)}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")

def print_success(text):
    print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")

def print_error(text):
    print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")

def print_info(text):
    print(f"{Fore.YELLOW}→ {text}{Style.RESET_ALL}")

def test_connection():
    """Testa a conexão com o backend"""
    print_header("TESTANDO CONEXÃO")
    try:
        response = requests.get(f"{BASE_URL}/products", timeout=5)
        if response.status_code == 200:
            print_success("Backend está online e respondendo")
            return True
        else:
            print_error(f"Backend retornou status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Backend não está rodando ou não está acessível")
        print_info("Execute: python run.py")
        return False
    except Exception as e:
        print_error(f"Erro inesperado: {e}")
        return False

def test_products():
    """Testa o endpoint de produtos"""
    print_header("TESTANDO PRODUTOS")
    try:
        response = requests.get(f"{BASE_URL}/products", timeout=5)
        if response.status_code == 200:
            data = response.json()
            products = data.get('products', [])
            print_success(f"GET /products - {len(products)} produtos encontrados")
            if products:
                print_info(f"Exemplo: {products[0].get('name', 'N/A')}")
            return True
        else:
            print_error(f"GET /products - Status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Erro ao testar produtos: {e}")
        return False

def test_faqs():
    """Testa o endpoint de FAQs"""
    print_header("TESTANDO FAQs")
    try:
        response = requests.get(f"{BASE_URL}/faqs", timeout=5)
        if response.status_code == 200:
            data = response.json()
            faqs = data.get('faqs', [])
            print_success(f"GET /faqs - {len(faqs)} FAQs encontradas")
            if faqs:
                print_info(f"Exemplo: {faqs[0].get('question', 'N/A')}")
            return True
        else:
            print_error(f"GET /faqs - Status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Erro ao testar FAQs: {e}")
        return False

def test_tips():
    """Testa o endpoint de dicas"""
    print_header("TESTANDO DICAS")
    try:
        response = requests.get(f"{BASE_URL}/tips", timeout=5)
        if response.status_code == 200:
            data = response.json()
            tips = data.get('tips', [])
            print_success(f"GET /tips - {len(tips)} dicas encontradas")
            if tips:
                print_info(f"Exemplo: {tips[0].get('title', 'N/A')}")
            return True
        else:
            print_error(f"GET /tips - Status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Erro ao testar dicas: {e}")
        return False

def test_cors():
    """Testa se CORS está habilitado"""
    print_header("TESTANDO CORS")
    try:
        headers = {
            'Origin': 'http://localhost:5173',
            'Access-Control-Request-Method': 'GET'
        }
        response = requests.options(f"{BASE_URL}/products", headers=headers, timeout=5)
        cors_header = response.headers.get('Access-Control-Allow-Origin')
        if cors_header:
            print_success(f"CORS habilitado - Origin permitida: {cors_header}")
            return True
        else:
            print_error("CORS não está configurado corretamente")
            return False
    except Exception as e:
        print_error(f"Erro ao testar CORS: {e}")
        return False

def main():
    print(f"\n{Fore.MAGENTA}{'='*50}")
    print(f"{Fore.MAGENTA}{'TESTE DA API PIFLOOR'.center(50)}")
    print(f"{Fore.MAGENTA}{'='*50}{Style.RESET_ALL}\n")
    
    results = []
    
    # Testa conexão primeiro
    if not test_connection():
        print_error("\nNão foi possível conectar ao backend. Abortando testes.")
        input("\nPressione Enter para sair...")
        return
    
    # Executa os testes
    results.append(("Produtos", test_products()))
    results.append(("FAQs", test_faqs()))
    results.append(("Dicas", test_tips()))
    results.append(("CORS", test_cors()))
    
    # Resumo
    print_header("RESUMO DOS TESTES")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        if result:
            print_success(f"{name}: PASSOU")
        else:
            print_error(f"{name}: FALHOU")
    
    print(f"\n{Fore.CYAN}Total: {passed}/{total} testes passaram{Style.RESET_ALL}")
    
    if passed == total:
        print(f"\n{Fore.GREEN}{'='*50}")
        print(f"{Fore.GREEN}{'✓ TODOS OS TESTES PASSARAM!'.center(50)}")
        print(f"{Fore.GREEN}{'='*50}{Style.RESET_ALL}\n")
    else:
        print(f"\n{Fore.YELLOW}{'='*50}")
        print(f"{Fore.YELLOW}{'⚠ ALGUNS TESTES FALHARAM'.center(50)}")
        print(f"{Fore.YELLOW}{'='*50}{Style.RESET_ALL}\n")
    
    input("\nPressione Enter para sair...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Teste interrompido pelo usuário{Style.RESET_ALL}")

