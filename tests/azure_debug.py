import requests
import json

AZURE_URL = "https://smieae-cic-f7anavbdh9fdc6c5.canadacentral-01.azurewebsites.net"

def debug_azure_app():
    """Debug completo de la app en Azure"""
    print("🐛 DEBUG DETALLADO DE AZURE APP")
    print("=" * 60)
    
    # 1. Verificar que la app Flask esté corriendo
    print("1. 🔍 Verificando aplicación Flask...")
    try:
        response = requests.get(AZURE_URL, timeout=10)
        print(f"   ✅ App responde: Status {response.status_code}")
        
        # Verificar si es una app Flask
        if "Flask" in response.text or "python" in response.text.lower():
            print("   🐍 Detectada aplicación Python/Flask")
        else:
            print("   ❓ No se detecta aplicación Flask - ¿Static site?")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # 2. Verificar estructura de la app
    print("\n2. 📁 Verificando estructura de la app...")
    test_paths = [
        "/", 
        "/static/",  # Carpeta static común en Flask
        "/vitals_data_retrieving/connect_to_api",
        "/api/",
        "/health/"
    ]
    
    for path in test_paths:
        try:
            response = requests.get(f"{AZURE_URL}{path}", timeout=5)
            print(f"   📍 {path:40} -> Status: {response.status_code}")
        except Exception as e:
            print(f"   📍 {path:40} -> Error: {e}")
    
    # 3. Verificar si hay algún endpoint funcionando
    print("\n3. 🎯 Buscando endpoints activos...")
    possible_endpoints = [
        "/", "/home", "/index", "/api", "/health", "/status",
        "/test", "/debug", "/vitals", "/fitbit", "/connect"
    ]
    
    active_endpoints = []
    for endpoint in possible_endpoints:
        try:
            response = requests.get(f"{AZURE_URL}{endpoint}", timeout=5)
            if response.status_code == 200:
                active_endpoints.append(endpoint)
                print(f"   ✅ {endpoint} -> FUNCIONA (200)")
        except:
            pass
    
    if not active_endpoints:
        print("   ❌ No se encontraron endpoints activos (solo /)")
    
    # 4. Conclusión
    print("\n4. 📋 DIAGNÓSTICO:")
    if active_endpoints:
        print(f"   ✅ App Flask detectada con {len(active_endpoints)} endpoints")
        print(f"   🔧 Endpoints activos: {active_endpoints}")
    else:
        print("   ❌ PROBLEMA: App Flask no tiene endpoints registrados")
        print("   💡 Posibles causas:")
        print("      - Blueprint no registrado en app.py")
        print("      - Código diferente en Azure vs Local")
        print("      - Error en deployment de GitHub Actions")
        print("      - Variables de entorno faltantes")

if __name__ == "__main__":
    debug_azure_app()