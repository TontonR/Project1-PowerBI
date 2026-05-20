import requests
import json
import re

def limpiar_html(texto_html):
    if not texto_html: return ""
    # Remover etiquetas HTML y códigos raros de formato
    texto_limpio = re.sub(r'<[^>]+>', ' ', texto_html)
    texto_limpio = re.sub(r'\s+', ' ', texto_limpio).strip()
    return texto_limpio

def resumir_contenido(contenido):
    if not contenido or len(contenido) < 10:
        return "No hay descripción detallada disponible para esta noticia."
    
    # Intentar separar por oraciones limpias
    oraciones = [o.strip() for o in contenido.split('. ') if len(o.strip()) > 15]
    
    if not oraciones:
        return contenido[:250] + "..."
        
    parrafo_1 = ". ".join(oraciones[:2]) + "."
    if len(oraciones) > 2:
        parrafo_2 = ". ".join(oraciones[2:4]) + "."
        return f"{parrafo_1}\n\n{parrafo_2}"
    
    return parrafo_1

def intentar_api_epic():
    """Ruta Principal: Obtiene las noticias estructuradas desde el catálogo de Epic Games."""
    print("🔄 [Intento 1] Conectando con la API Global de Epic Games Store...")
    
    url = "https://graphql.epicgames.com/graphql"
    headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
    
    # Query GraphQL oficial para extraer noticias/items de Wuthering Waves
    query = {
        "query": """
        {
          Catalog {
            searchStore(keywords: "Wuthering Waves", category: "games", locale: "en-US") {
              elements {
                title
                description
                expiryDate
              }
            }
          }
        }
        """
    }
    
    response = requests.post(url, json=query, headers=headers, timeout=10)
    if response.status_code != 200:
        return None
        
    data = response.json()
    elements = data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", [])
    
    if not elements:
        return None
        
    noticias_procesadas = []
    for item in elements[:5]:
        noticias_procesadas.append({
            "titulo": item.get("title"),
            "fecha": item.get("expiryDate", "Reciente")[:10], # SoloAAAA-MM-DD
            "contenido": item.get("description")
        })
    return noticias_procesadas

def intentar_rss_comunidad():
    """Ruta de Respaldo: Si la API principal falla, extrae del feed de parches oficiales."""
    print("⚠️ [Intento 2] Ejecutando respaldo: Buscando en canales de distribución alternativos...")
    # Usamos una pasarela espejo de parches de Kuro/comunidad estable
    url = "https://api.rss2json.com/v1/api.json?rss_url=https://reddit.com/r/WutheringWaves/.rss"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code != 200:
        return None
        
    data = response.json()
    items = data.get("items", [])
    
    noticias_procesadas = []
    for item in items:
        # Filtrar solo hilos oficiales o de anuncios importantes
        titulo = item.get("title", "")
        if any(k in titulo.lower() for k in ["patch", "update", "news", "event", "dev", "official", "1.", "2."]):
            noticias_procesadas.append({
                "titulo": titulo,
                "fecha": item.get("pubDate", "Reciente")[:10],
                "contenido": limpiar_html(item.get("content", ""))
            })
        if len(noticias_procesadas) == 5:
            break
            
    return noticias_procesadas if noticias_procesadas else None

def evaluar_y_mostrar():
    # --- EJECUCIÓN DEL PROCESO ---
    noticias = intentar_api_epic()
    
    # --- TEST FINAL EVALUADOR ---
    # Evaluamos si el resultado es válido y vale la pena (no está vacío y trae estructura correcta)
    if noticias and len(noticias) >= 3:
        print("✅ [TEST PASADO]: Datos obtenidos con éxito de la fuente primaria.\n")
    else:
        print("❌ [TEST FALLIDO]: La fuente primaria no devolvió suficiente información.")
        # RE-EJECUCIÓN DE TODO EL PROCESO CON FUENTE ALTERNATIVA
        noticias = intentar_rss_comunidad()
        
        if noticias:
            print("✅ [TEST DE RESPALDO PASADO]: Datos recuperados mediante la ruta alternativa.\n")
        else:
            print("🚨 [CRÍTICO]: Todos los reintentos fallaron. El servidor de origen no responde.")
            return

    # --- IMPRESIÓN FINAL DE LOS RESULTADOS ---
    print(f"==================================================")
    print(f"   ÚLTIMAS NOVEDADES DE WUTHERING WAVES           ")
    print(f"==================================================\n")
    
    for idx, item in enumerate(noticias[:5], 1):
        resumen = resumir_contenido(item['contenido'])
        print(f"📢 [{idx}] TÍTULO: {item['titulo']}")
        print(f"📅 Fecha: {item['fecha']}")
        print(f"📝 RESUMEN:\n{resumen}")
        print(f"\n--------------------------------------------------\n")

if __name__ == "__main__":
    evaluar_y_mostrar()
