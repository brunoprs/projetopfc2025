
# ================================
# FILTRO DE PALAVRAS PROIBIDAS
# ================================

# Lista de palavras proibidas 
BANNED_WORDS = [
    "pinto", "coco", "penis", "puta", "caralho", "merda", "buceta", "cu", "foda",
    "porra", "viado", "bicha", "traveco", "arrombado", "fdp", "filho da puta",
    "bosta", "cacete", "piru", "xota", "vadia", "safada", "tesao", "tesão",
    
]

def contains_banned_word(text: str) -> bool:
    """
    Verifica se o texto contém alguma palavra proibida.
    Ignora maiúsculas/minúsculas.
    """
    if not text:
        return False
    text_lower = text.lower()
    return any(word in text_lower for word in BANNED_WORDS)

def censor_text(text: str) -> str:
    """
    Substitui palavras proibidas por asteriscos: "pinto" → "*****"
    """
    if not text:
        return text
    result = text
    for word in BANNED_WORDS:
        # Substitui a palavra exata CASO EU QUERIA ADICIONAR!!! (isso aqui é case-insensitive)
        import re
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        result = pattern.sub('*' * len(word), result)
    return result