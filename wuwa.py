import requests
import re

def limpiar_html(texto_html):
    """Elimina etiquetas HTML y limpia espacios en blanco."""
    if not texto_html:
        return ""
    # Quitar etiquetas HTML
    texto_limpio = re.sub(r'<[^>]+>', ' ', texto_html)
    # Normalizar espacios en blanco
    texto_limpio = re.sub(r'\s+', ' ', texto_limpio).strip()
    return texto_limpio

def resumir_contenido(contenido_limpio):
    """Crea un resumen de 1 o 2 párrafos a partir del contenido."""
    if not contenido_limpio:
        return "No hay contenido disponible para resumir."
    
    # Dividimos por puntos para separar oraciones
    oraciones = contenido_limpio.split('. ')
    
    # Filtramos oraciones vacías o extremadamente cortas
    oraciones = [o.strip() for o in oraciones if len(o.strip()) > 10]
    
    if not oraciones:
        return contenido_limpio[:300] + "..."

    # Párrafo 1: Introducción (primeras 3 oraciones)
    parrafo_1 = ". ".join(oraciones[:3]) + "."
    
    # Párrafo 2: Detalles (siguientes 3 oraciones si existen)
    if len(oraciones) > 3:
        parrafo_2 = ". ".join(oraciones[3:6]) + "."
        return f"{parrafo_1}\n\n{parrafo_2}"
    
    return parrafo_1

def obtener_noticias_wuwa():
    # API pública oficial que alimenta la sección de noticias en inglés de Wuthering Waves
    url = "https://wutheringwaves.kurogames.com/modules/websiteOfficial/news/list"
    
    # Parámetros exactos para pedir las últimas noticias oficiales, en inglés y paginadas
    params = {
        "page": 1,
        "pageSize": 5,
        "language": "en",
        "type": "all" # Trae avisos, eventos, actualizaciones, etc.
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://wutheringwaves.kurogames.com/"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"Error al conectar con la API oficial. Código: {response.status_code}")
            return

        data = response.json()
        
        # Estructura interna de respuesta de Kuro Games
        if data.get("code") != 200 or "data" not in data or "list" not in data["data"]:
            print("La API respondió pero el formato de datos ha cambiado.")
            return
            
        noticias = data["data"]["list"]
        
        print(f"==================================================")
        print(f"   ÚLTIMAS 5 NOVEDADES DE WUTHERING WAVES (API)   ")
        print(f"==================================================\n")
        
        for idx, item in enumerate(noticias, 1):
            titulo = item.get("title", "Sin título")
            fecha = item.get("publishTime", "Fecha desconocida")
            
            # El contenido original suele venir con HTML de los editores
            contenido_raw = item.get("content", "")
            contenido_limpio = limpiar_html(contenido_raw)
            resumen = resumir_contenido(contenido_limpio)
            
            print(f"📢 [{idx}] TÍTULO: {titulo}")
            print(f"📅 Fecha: {fecha}")
            print(f"📝 RESUMEN:\n{resumen}")
            print(f"\n--------------------------------------------------\n")
            
    except Exception as e:
        print(f"Ocurrió un error inesperado al procesar la información: {e}")

if __name__ == "__main__":
    obtener_noticias_wuwa()
