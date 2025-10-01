import time
import cProfile
import pstats
from io import StringIO
from vitals_data_retrieving.vitals_data_retrieving_service import VitalsDataRetrievingService
from vitals_data_retrieving.data_consumption_tools.wearable_devices_retrieving.FitbitDataRetriever import FitbitDataRetriever

def debug_slow_algorithm():
    """Debug detallado del algoritmo lento"""
    print("🐌 DEBUG DETALLADO - ALGORITMO LENTO (30s)")
    print("=" * 60)
    
    # Crear instancias
    fitbit_retriever = FitbitDataRetriever()
    vitals_service = VitalsDataRetrievingService(fitbit_retriever)
    
    # Configurar profiler
    profiler = cProfile.Profile()
    
    print("1. 🔍 Iniciando profiling del método problemático...")
    
    # Ejecutar con profiling detallado
    profiler.enable()
    
    start_time = time.time()
    try:
        # Este es el método que tarda 30 segundos
        result = vitals_service.get_data_from_wearable_device_api(
            "test_user_performance",
            "2024-01-15", 
            ["heart_rate", "sleep"],
            False
        )
        execution_time = time.time() - start_time
        print(f"   ✅ Ejecución completada: {execution_time:.2f}s")
        
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"   ❌ Error después de {execution_time:.2f}s: {e}")
        print(f"   🐛 Tipo de error: {type(e).__name__}")
    
    profiler.disable()
    
    print("\n2. 📊 ANÁLISIS DE PERFORMANCE DETALLADO:")
    
    # Obtener estadísticas detalladas
    s = StringIO()
    ps = pstats.Stats(profiler, stream=s)
    ps.strip_dirs().sort_stats('cumulative')
    
    print("   📈 TOP 20 FUNCIONES MÁS LENTAS:")
    print("   " + "=" * 50)
    
    ps.print_stats(20)  # Top 20 funciones más lentas
    stats_output = s.getvalue()
    
    # Mostrar las funciones más problemáticas
    lines = stats_output.split('\n')
    for line in lines[:25]:  # Mostrar primeras 25 líneas
        if line.strip():
            print(f"   {line}")
    
    print("\n3. 💡 IDENTIFICANDO CUELOS DE BOTELLA:")
    
    # Buscar patrones comunes en funciones lentas
    slow_patterns = []
    for line in lines:
        if '30.0' in line or '29.' in line or '28.' in line:
            slow_patterns.append(line.strip())
    
    if slow_patterns:
        print("   🚨 FUNCIONES EXTREMADAMENTE LENTAS DETECTADAS:")
        for pattern in slow_patterns[:5]:
            print(f"      ⚠️  {pattern}")
    else:
        print("   🔍 El tiempo parece estar en esperas/externas, no en CPU")
    
    print("\n4. 🎯 CAUSA PROBABLE:")
    print("   ⏱️  El método está probablemente esperando:")
    print("      - Timeout de conexión a Fitbit API")
    print("      - Espera por credenciales/tokens")
    print("      - Llamadas HTTP bloqueantes")
    print("      - Retries automáticos por errores")

def analyze_fitbit_dependencies():
    """Analiza dependencias de Fitbit que pueden causar delays"""
    print("\n5. 🔗 ANALIZANDO DEPENDENCIAS EXTERNAS:")
    
    try:
        # Verificar si hay configuraciones que causen timeouts
        fitbit_retriever = FitbitDataRetriever()
        
        print("   📋 Atributos del FitbitDataRetriever:")
        attrs = [attr for attr in dir(fitbit_retriever) if not attr.startswith('_')]
        for attr in attrs[:10]:  # Mostrar primeros 10
            print(f"      - {attr}")
            
    except Exception as e:
        print(f"   ❌ Error analizando dependencias: {e}")

if __name__ == "__main__":
    debug_slow_algorithm()
    analyze_fitbit_dependencies()