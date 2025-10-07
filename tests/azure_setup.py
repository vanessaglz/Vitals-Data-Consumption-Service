import requests
import json
from datetime import datetime

def verify_azure_deployment():
    """Verifica que el deployment en Azure esté funcionando correctamente"""
    
    # Tu URL de Azure - ACTUALIZA si es diferente
    AZURE_URL = "https://smieae-cic-f7anavbdh9fdc6c5.canadacentral-01.azurewebsites.net"
    
    print("🔍 VERIFICANDO NUEVO SETUP DE AZURE")
    print("=" * 60)
    print(f"📋 URL: {AZURE_URL}")
    print(f"🕐 Fecha: {datetime.now().isoformat()}")
    print("=" * 60)
    
    # Lista de endpoints que DEBERÍAN funcionar ahora
    endpoints_to_test = [
        {
            "path": "/",
            "method": "GET",
            "description": "Página principal"
        },
        {
            "path": "/vitals_data_retrieving/connect_to_api", 
            "method": "GET",
            "description": "Conexión a Fitbit API"
        },
        {
            "path": "/vitals_data_retrieving/get_user_info",
            "method": "POST", 
            "description": "Información de usuario",
            "data": {"user_id": "test_user_azure"}
        },
        {
            "path": "/vitals_data_retrieving/get_vitals_data",
            "method": "POST",
            "description": "Datos de vitals",
            "data": {
                "user_id": "test_user_azure",
                "date": "2024-01-15",
                "scope": ["heart_rate"],
                "db_storage": False
            }
        }
    ]
    
    results = {}
    
    for endpoint in endpoints_to_test:
        full_url = f"{AZURE_URL}{endpoint['path']}"
        print(f"\n🎯 Testing: {endpoint['description']}")
        print(f"   📍 {endpoint['method']} {endpoint['path']}")
        
        try:
            if endpoint['method'] == 'POST':
                response = requests.post(
                    full_url,
                    json=endpoint.get('data', {}),
                    timeout=10,
                    headers={'Content-Type': 'application/json'}
                )
            else:
                response = requests.get(full_url, timeout=10)
            
            # Análisis de la respuesta
            status_emoji = "✅" if response.status_code in [200, 302] else "⚠️" if response.status_code == 404 else "❌"
            
            print(f"   {status_emoji} Status: {response.status_code}")
            print(f"   ⏱️  Tiempo: {response.elapsed.total_seconds():.3f}s")
            print(f"   📦 Tamaño: {len(response.content)} bytes")
            
            # Información adicional para diagnósticos
            if response.status_code == 302:
                print(f"   🔄 Redirect to: {response.headers.get('Location', 'Unknown')}")
            elif response.status_code == 200:
                content_preview = response.text[:100] + "..." if len(response.text) > 100 else response.text
                print(f"   📝 Preview: {content_preview}")
            elif response.status_code == 404:
                print(f"   💡 El endpoint existe pero no está registrado en el blueprint")
            
            results[endpoint['path']] = {
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'content_size': len(response.content),
                'timestamp': datetime.now().isoformat()
            }
            
        except requests.exceptions.Timeout:
            print(f"   ❌ TIMEOUT - El endpoint no responde")
            results[endpoint['path']] = {
                'status_code': 'timeout',
                'response_time': 10.0,
                'error': 'timeout',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results[endpoint['path']] = {
                'status_code': 'error', 
                'response_time': 0.0,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    # Generar reporte
    report = {
        'verification_timestamp': datetime.now().isoformat(),
        'azure_url': AZURE_URL,
        'setup_type': 'fork_with_github_actions',
        'endpoint_results': results,
        'summary': {
            'total_endpoints_tested': len(results),
            'successful_endpoints': sum(1 for r in results.values() if r['status_code'] in [200, 302]),
            'failed_endpoints': sum(1 for r in results.values() if r['status_code'] not in [200, 302]),
            'average_response_time': sum(r['response_time'] for r in results.values() if isinstance(r['response_time'], (int, float))) / len(results)
        }
    }
    
    # Guardar reporte
    with open('azure_verification_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # Mostrar resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 60)
    
    successful = report['summary']['successful_endpoints']
    total = report['summary']['total_endpoints_tested']
    
    print(f"✅ Endpoints exitosos: {successful}/{total}")
    print(f"📈 Tasa de éxito: {(successful/total)*100:.1f}%")
    print(f"⏱️  Tiempo promedio: {report['summary']['average_response_time']:.3f}s")
    
    if successful == total:
        print("\n🎉 ¡EXCELENTE! Todos los endpoints funcionan correctamente")
        print("   Tu setup de Azure + GitHub está funcionando perfectamente")
    elif successful > 0:
        print(f"\n⚠️  Parcialmente exitoso: {successful}/{total} endpoints funcionan")
        print("   Revisa los endpoints fallidos arriba")
    else:
        print("\n❌ Problemas detectados - Revisa el deployment")
    
    print(f"\n💾 Reporte guardado: azure_verification_report.json")
    
    return report

if __name__ == "__main__":
    verify_azure_deployment()