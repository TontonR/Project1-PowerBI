import requests
import json
import re

def limpiar_html(texto_html):
    if not texto_html: return ""
    texto_limpio = re.sub(r'<[^>]+>', ' ', texto_html)
    texto_limpio = re.sub(r'\s+', ' ', texto_limpio).strip()
    return texto_limpio

def resumir_contenido(contenido):
    if not contenido or len(contenido) < 10:
        return "No hay descripción detallada disponible para esta noticia."
    
    oraciones = [o.strip() for o in contenido.split('. ') if len(o.strip()) > 15]
    
    if not oraciones:
        return contenido[:250] + "..."
        
    parrafo_1 = ". ".join(oraciones[:2]) + "."
    if len(oraciones) > 2:
        parrafo_2 = ". ".join(oraciones[2:4]) + "."
        return f"{parrafo_1}\n\n{parrafo_2}"
    
    return parrafo_1

def intentar_api_epic():
    url = "https://graphql.epicgames.com/graphql"
    headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
    
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
    
    try:
        response = requests.post(url, json=query, headers=headers, timeout=10)
        if response.status_code != 200: return None
        data = response.json()
        elements = data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", [])
        
        if not elements: return None
            
        noticias_procesadas = []
        for item in elements[:5]:
            noticias_procesadas.append({
                "titulo": item.get("title"),
                "fecha": item.get("expiryDate", "Reciente")[:10],
                "contenido": item.get("description")
            })
        return noticias_procesadas
    except:
        return None

def intentar_rss_comunidad():
    url = "https://api.rss2json.com/v1/api.json?rss_url=https://reddit.com/r/WutheringWaves/.rss"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200: return None
        data = response.json()
        items = data.get("items", [])
        
        noticias_procesadas = []
        for item in items:
            titulo = item.get("title", "")
            if any(k in titulo.lower() for k in ["patch", "update", "news", "event", "dev", "official", "1.", "2."]):
                noticias_procesadas.append({
                    "titulo": titulo,
                    "fecha": item.get("pubDate", "Reciente")[:10],
                    "contenido": limpiar_html(item.get("content", ""))
                })
            if len(noticias_procesadas) == 5: break
        return noticias_procesadas if noticias_procesadas else None
    except:
        return None

def pulir_titular(titulo):
    if not titulo: return "Noticia sin título"
    titulo_limpio = re.sub(r'^(Anuncio Oficial|NEWS|UPDATE|PATCH NOTES|EVENTO):\s*', '', titulo, flags=re.IGNORECASE)
    titulo_limpio = re.sub(r'\[.*?\]|\(.*?\)', '', titulo_limpio)
    titulo_limpio = re.sub(r'\s+', ' ', titulo_limpio).strip()
    if titulo_limpio:
        titulo_limpio = titulo_limpio[0].upper() + titulo_limpio[1:]
    return titulo_limpio

def evaluar_y_mostrar():
    noticias = intentar_api_epic()
    
    if not (noticias and len(noticias) >= 3):
        noticias = intentar_rss_comunidad()
        if not noticias:
            # Si todo falla por completo, generamos un reporte de error en el Markdown para que lo sepas
            with open("noticias_wuwa.md", "w", encoding="utf-8") as f:
                f.write("# 🚨 Error Crítico\nNo se pudo recuperar información de ninguna fuente en este intento.\n")
            return

    # --- ESCRITURA EN EL ARCHIVO MARKDOWN ---
    with open("noticias_wuwa.md", "w", encoding="utf-8") as f:
        f.write("# 🌊 Wuthering Waves — Últimas Novedades\n")
        f.write("Reporte automático generado en formato Markdown dentro del repositorio.\n\n")
        f.write("---\n\n")
        
        for idx, item in enumerate(noticias[:5], 1):
            titulo_mejorado = pulir_titular(item['titulo'])
            resumen = resumir_contenido(item['contenido'])
            
            f.write(f"## 📢 {idx}. {titulo_mejorado}\n")
            f.write(f"> 📅 **Fecha de publicación:** `{item['fecha']}`\n\n")
            f.write(f"{resumen}\n\n")
            f.write("---\n\n")
            
    print("✅ Archivo 'noticias_wuwa.md' creado y formateado correctamente.")

if __name__ == "__main__":
    evaluar_y_mostrar()
