import os
import re
import time
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
AMAZON_TAG = os.getenv("AMAZON_TAG")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
}

def extract_asin(url_or_id):
    """Extrai o ASIN (Amazon Standard Identification Number) de um link ou string."""
    match = re.search(r'([A-Z0-9]{10})', url_or_id)
    if match:
        return match.group(1)
    return None

def is_search_url(url):
    """Verifica se a URL é de uma busca na Amazon."""
    return 'amazon.com.br/s?' in url

def search_amazon(query):
    """Faz a busca na Amazon e retorna os 10 primeiros ASINs encontrados."""
    # Se for uma URL direta de busca
    if is_search_url(query):
        url = query
    else:
        # Se for apenas palavras-chave
        from urllib.parse import quote_plus
        url = f"https://www.amazon.com.br/s?k={quote_plus(query)}"
        
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.find_all('div', {'data-component-type': 's-search-result'})
            
            asins = []
            for item in items[:10]: # Pega apenas os 10 primeiros
                asin = item.get('data-asin')
                if asin:
                    asins.append(asin)
            return asins
        else:
            print(f"Erro ao acessar busca na Amazon: HTTP {response.status_code}")
            return []
    except Exception as e:
        print(f"Erro ao buscar '{query}': {e}")
        return []

def get_amazon_details(asin):
    """Busca os detalhes do produto na Amazon (título e preço)."""
    url = f"https://www.amazon.com.br/dp/{asin}"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Tenta pegar o título
            title_element = soup.find(id="productTitle")
            title = title_element.text.strip() if title_element else "Produto Amazon"
            
            # Tenta pegar o preço (existem várias classes para preço na Amazon)
            price = "Verificar no site"
            price_whole = soup.find("span", class_="a-price-whole")
            price_fraction = soup.find("span", class_="a-price-fraction")
            
            if price_whole and price_fraction:
                price = f"R$ {price_whole.text.strip()}{price_fraction.text.strip()}"
            else:
                # Tenta outras classes ou o preço alternativo
                price_alt = soup.find("span", class_="a-offscreen")
                if price_alt:
                    price = price_alt.text.strip()
                
            return title, price
        else:
            print(f"Erro ao acessar página da Amazon: HTTP {response.status_code}")
            return "Produto Amazon", "Verificar no site"
    except Exception as e:
        print(f"Erro ao obter detalhes para {asin}: {e}")
        return "Produto Amazon", "Verificar no site"

def send_telegram_message(message):
    """Envia uma mensagem para o chat/grupo do Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("✅ Mensagem enviada com sucesso pro Telegram!")
        else:
            print(f"❌ Erro ao enviar pro Telegram: {response.text}")
    except Exception as e:
        print(f"❌ Exceção ao enviar pro Telegram: {e}")

def process_asin(asin):
    """Processa um único ASIN e envia pro Telegram."""
    title, price = get_amazon_details(asin)
    
    # Link de afiliado montado
    affiliate_link = f"https://www.amazon.com.br/dp/{asin}?tag={AMAZON_TAG}"
    
    # Montar a mensagem do Telegram
    message = (
        f"🛒 <b>{title}</b>\n\n"
        f"💰 Preço: {price}\n\n"
        f"🔗 Compre pelo link de afiliado:\n{affiliate_link}"
    )
    
    send_telegram_message(message)

def main():
    if not all([TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, AMAZON_TAG]):
        print("⚠️  ERRO: Certifique-se de configurar TELEGRAM_TOKEN, TELEGRAM_CHAT_ID e AMAZON_TAG no arquivo .env")
        return
        
    try:
        with open("produtos.txt", "r", encoding="utf-8") as file:
            items = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print("⚠️  Arquivo produtos.txt não encontrado. Criando um arquivo de exemplo...")
        with open("produtos.txt", "w", encoding="utf-8") as file:
            file.write("https://www.amazon.com.br/s?k=escorredor+de+pratos\n")
            file.write("B07XQXZXJC\n")
            file.write("smartphone samsung\n")
        print("Edite o arquivo produtos.txt e rode o script novamente.")
        return

    if not items:
        print("⚠️  O arquivo produtos.txt está vazio. Adicione buscas, links ou ASINs de produtos.")
        return

    print(f"🚀 Iniciando o processamento de {len(items)} linha(s)...\n")
    
    for item in items:
        # Pular linhas que são comentários (começando com #)
        if item.startswith('#'):
            continue
            
        print(f"\n--- Processando linha: {item} ---")
        
        # 1. Tenta extrair um ASIN direto
        asin = extract_asin(item)
        
        # 2. Se for uma URL de busca ou não tiver aparência de ASIN (ex: termo livre)
        if is_search_url(item) or not asin:
            print(f"🔍 Identificado como busca. Buscando top 10 resultados para: {item}")
            asins = search_amazon(item)
            
            if not asins:
                print("❌ Nenhum produto encontrado nesta busca.")
                continue
                
            print(f"✅ Encontrados {len(asins)} produtos. Processando...")
            for i, search_asin in enumerate(asins):
                print(f"  Produto {i+1}/10: {search_asin}")
                process_asin(search_asin)
                time.sleep(2) # Pausa amigável
                
        else:
            # Se for um ASIN ou URL direto de produto
            print(f"📦 Identificado ASIN direto: {asin}")
            process_asin(asin)
            time.sleep(2)
            
        print("-" * 50)

if __name__ == "__main__":
    main()
