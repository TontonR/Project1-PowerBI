import requests
import re

def limpiar_html(texto_html):
    """Elimina etiquetas HTML y limpia espacios en blanco."""
    if not texto_html:
        return ""
    texto_limpio = re.sub(r'<[^>]+>', ' ', texto_html)
    texto_limpio = re.sub(r'\s+', ' ', texto_limpio).strip()
    return texto_limpio

def resumir_contenido(contenido_limpio):
    """Crea un resumen de 1 o 2 párrafos a partir del contenido."""
    if not contenido_limpio:
        return "No hay contenido detallado disponible para resumir."
    
    oraciones = contenido_limpio.split('. ')
    oraciones = [o.strip() for o in oraciones if len(o.strip()) > 10]
    
    if not oraciones:
        return contenido_limpio[:250] + "..."

    parrafo_1 = ". ".join(oraciones[:3]) + "."
    if len(oraciones) > 3:
        parrafo_2 = ". ".join(oraciones[3:6]) + "."
        return f"{parrafo_1}\n\n{parrafo_2}"
    
    return parrafo_1

def obtener_noticias_wuwa():
    # URL de la API Global Oficial de Kuro Games para noticias
    url = "https://wutheringwaves.kurogames-global.com/modules/websiteOfficial/news/list"
    
    params = {
        "page": 1,
        "pageSize": 5,
        "language": "en",
        "type": "all"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://wutheringwaves.kurogames-global.com/",
        "Accept": "application/json, text/plain, */*"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=12)
        
        # Validar códigos de estado HTTP
        if response.status_code != 200:
            print(f"❌ Error de conexión con el servidor de Kuro Games. Código HTTP: {response.status_code}")
            return

        # EVITAR EL ERROR (char 0): Comprobar si la respuesta es realmente JSON
        try:
            data = response.json()
        except ValueError:
            print("⚠️ El servidor no devolvió un JSON válido. Posible bloqueo de seguridad o cambio de URL.")
            print("Contenido recibido (primeros 200 caracteres):", response.text[:200])
            return
        
        # Validar la estructura interna de la respuesta de Kuro Games
        if data.get("code") != 200 or "data" not in data or "list" not in data["data"]:
            print("⚠️ Estructura de API desconocida o mantenimiento del servidor.")
            return
            
        noticias = data["data"]["list"]
        
        print(f"==================================================")
        print(f"   ÚLTIMAS 5 NOVEDADES DE WUTHERING WAVES         ")
        print(f"==================================================\n")
        
        for idx, item in enumerate(noticias[:5], 1):
            titulo = item.get("title", "Sin título")
            fecha = item.get("publishTime", "Fecha desconocida")
            contenido_raw = item.get("content", "")
            
            contenido_limpio = limpiar_html(contenido_raw)
            resumen = resumir_contenido(contenido_limpio)
            
            print(f"📢 [{idx}] TÍTULO: {titulo}")
            print(f"📅 Fecha: {fecha}")
            print(f"📝 RESUMEN:\n{resumen}")
            print(f"\n--------------------------------------------------\n")
            
    except requests.exceptions.Timeout:
        print("❌ Error: Tiempo de espera agotado al conectar con el servidor del juego.")
    except Exception as e:
        print(f"❌ Ocurrió un error inesperado al procesar la información: {e}")

if __name__ == "__main__":
    obtener_noticias_wuwa()
