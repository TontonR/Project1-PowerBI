import requests
from bs4 import BeautifulSoup

def buscar_noticias():
    # URL oficial de noticias de Wuthering Waves
    url = "https://wutheringwaves.kurogames.com/en/main/news"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # NOTA: Este selector es un ejemplo genérico. 
            # Los sitios web de gachas cambian a menudo de estructura, adáptalo según inspecciones su HTML.
            noticias = soup.find_all('li', class_='news-item') 
            
            print(f"--- Últimas Novedades de Wuthering Waves ---")
            if not noticias:
                print("Se accedió a la web, pero no se encontraron elementos con el selector actual.")
            else:
                for idx, item in enumerate(noticias[:5], 1):
                    print(f"{idx}. {item.text.strip()}")
        else:
            print(f"No se pudo acceder a la web. Código de estado: {response.status_code}")
            
    except Exception as e:
        print(f"Ocurrió un error durante el scraping: {e}")

if __name__ == "__main__":
    buscar_noticias()
