import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

AMAZON_TAG = os.getenv("AMAZON_TAG")

def get_amazon_search_results(url, max_results=10):
    """Scrapes an Amazon search results page for the top products."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    
    print(f"Buscando produtos em: {url}\n")
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Erro ao acessar a página: HTTP {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Encontra blocos de resultados de pesquisa
        results = soup.find_all('div', {'data-component-type': 's-search-result'})
        
        products = []
        for res in results:
            if len(products) >= max_results:
                break
                
            asin = res.get('data-asin')
            if not asin:
                continue
                
            # Extrai título
            title_el = res.find('h2')
            title = title_el.text.strip() if title_el else "Produto sem título"
            
            # Extrai preço principal e centavos
            price = "Preço indisponível"
            price_whole = res.find("span", class_="a-price-whole")
            price_fraction = res.find("span", class_="a-price-fraction")
            
            if price_whole:
                whole = price_whole.text.strip()
                fraction = price_fraction.text.strip() if price_fraction else "00"
                price = f"R$ {whole}{fraction}"
            else:
                price_alt = res.find("span", class_="a-offscreen")
                if price_alt:
                    price = price_alt.text.strip()
                    
            products.append({
                'asin': asin,
                'title': title,
                'price': price
            })
            
        return products
    except Exception as e:
        print(f"Erro ao raspar a página: {e}")
        return []

def main():
    if not AMAZON_TAG:
        print("⚠️  ERRO: AMAZON_TAG não encontrada. Verifique seu arquivo .env")
        return
        
    url = input("Cole a URL de pesquisa da Amazon: ").strip()
    
    if not url:
        print("URL inválida.")
        return
        
    products = get_amazon_search_results(url, max_results=10)
    
    if not products:
        print("Nenhum produto encontrado. Verifique a URL.")
        return
        
    print(f"✅ Encontrados {len(products)} produtos top!\n")
    print("-" * 60)
    
    for i, prod in enumerate(products, 1):
        affiliate_link = f"https://www.amazon.com.br/dp/{prod['asin']}?tag={AMAZON_TAG}"
        print(f"{i}. {prod['title']}")
        print(f"   Preço: {prod['price']}")
        print(f"   Link Afiliado: {affiliate_link}")
        print("-" * 60)

if __name__ == "__main__":
    main()
