import cProfile
import pstats
import time
import json
from datetime import datetime
import logging
from io import StringIO
from functools import wraps
from prometheus_client import Gauge, generate_latest, CONTENT_TYPE_LATEST
from opencensus.ext.azure.log_exporter import AzureLogHandler
from flask import Blueprint, Response
import os

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
performance_bp = Blueprint('performance_metrics', __name__)

if os.environ.get('APPLICATIONINSIGHTS_CONNECTION_STRING'):
    logger.addHandler(AzureLogHandler(
        connection_string=os.environ['APPLICATIONINSIGHTS_CONNECTION_STRING']
    ))

class RealAlgorithmProfiler:
    def __init__(self):
        self.results = {}
        self.profiler = cProfile.Profile()
        
    def profile_method(self, method_name):
        #"""Decorador para profilear métodos específicos"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                print(f"🔍 Profileando: {method_name}")
                
                self.profiler.enable()
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    success = True
                except Exception as e:
                    result = None
                    execution_time = time.time() - start_time
                    success = False
                    logger.error(f"Error en {method_name}: {e}")
                
                self.profiler.disable()
                
                # Obtener estadísticas de profiling
                s = StringIO()
                ps = pstats.Stats(self.profiler, stream=s)
                ps.strip_dirs().sort_stats('cumulative')
                profile_stats = s.getvalue()
                
                # Extraer métricas clave
                stats_summary = self._extract_profile_metrics(profile_stats)
                
                # Guardar resultados
                self.results[method_name] = {
                    'execution_time': execution_time,
                    'success': success,
                    'timestamp': datetime.now().isoformat(),
                    'performance_metrics': {
                        'throughput': 1 / execution_time if execution_time > 0 else 0,
                        'calls_per_second': stats_summary.get('total_calls', 0) / execution_time if execution_time > 0 else 0,
                        'memory_operations': stats_summary.get('memory_ops', 0)
                    },
                    'profile_summary': stats_summary,
                    'error': str(e) if not success else None
                }
                
                print(f"✅ {method_name}: {execution_time:.4f}s | Success: {success}")
                return result
            return wrapper
        return decorator
    
    def _extract_profile_metrics(self, profile_output):
        #"""Extrae métricas clave del output de profiling"""
        lines = profile_output.split('\n')
        metrics = {
            'total_calls': 0,
            'primitive_calls': 0,
            'total_time': 0,
            'cumulative_time': 0,
            'top_functions': []
        }
        
        for line in lines:
            if 'function calls' in line:
                # Ejemplo: "123456 function calls (12345 primitive calls) in 0.890 seconds"
                parts = line.split()
                if len(parts) >= 6:
                    metrics['total_calls'] = int(parts[0])
                    metrics['primitive_calls'] = int(parts[3])
                    metrics['total_time'] = float(parts[-2])
            elif line.strip() and not line.startswith('Ordered by') and 'ncalls' not in line:
                # Líneas de funciones individuales
                parts = line.split()
                if len(parts) >= 5:
                    try:
                        func_info = {
                            'calls': parts[0],
                            'total_time': float(parts[3]),
                            'per_call': float(parts[4]),
                            'function_name': ' '.join(parts[5:])
                        }
                        metrics['top_functions'].append(func_info)
                    except (ValueError, IndexError):
                        continue
        
        # Mantener solo top 10 funciones
        metrics['top_functions'] = metrics['top_functions'][:10]
        return metrics

# Instancia global del profiler
profiler = RealAlgorithmProfiler()

# Importar y profilear las clases REALES de tu proyecto
try:
    from vitals_data_retrieving.data_consumption_tools.wearable_devices_retrieving.FitbitDataRetriever import FitbitDataRetriever
    from vitals_data_retrieving.vitals_data_retrieving_service import VitalsDataRetrievingService
    from vitals_data_retrieving.data_consumption_tools.Entities.CryptoUtils import hash_data
    
    # Crear instancias para testing
    fitbit_retriever = FitbitDataRetriever()
    vitals_service = VitalsDataRetrievingService(fitbit_retriever)
    
except ImportError as e:
    logger.warning(f"No se pudieron importar algunos módulos: {e}")
    fitbit_retriever = None
    vitals_service = None

def analyze_fitbit_authentication():
    #"""Analiza performance del proceso de autenticación con Fitbit"""
    if not fitbit_retriever:
        return None
    
    @profiler.profile_method("fitbit_authentication_flow")
    def auth_flow():
        # Simular el flujo de autenticación
        try:
            # Esto probablemente fallará sin credenciales, pero queremos medir el performance
            auth_url = fitbit_retriever.connect_to_api()
            return auth_url
        except Exception as e:
            # Medimos el performance incluso en errores
            logger.info(f"Autenticación falló (esperado): {e}")
            return None
    
    return auth_flow()

def analyze_data_processing():
    #"""Analiza performance del procesamiento de datos"""
    if not vitals_service:
        return None
    
    @profiler.profile_method("data_processing_pipeline")
    def process_data():
        # Simular procesamiento de datos
        test_data = {
            "user_id": "test_user_performance",
            "date": "2024-01-15",
            "scope": ["heart_rate", "sleep"]
        }
        
        try:
            # Este método probablemente fallará sin tokens, pero medimos el performance
            result = vitals_service.get_data_from_wearable_device_api(
                test_data["user_id"],
                test_data["date"],
                test_data["scope"],
                False
            )
            return result
        except Exception as e:
            logger.info(f"Procesamiento falló (esperado): {e}")
            return None
    
    return process_data()

def analyze_crypto_operations():
    #"""Analiza performance de operaciones criptográficas"""
    try:
        from vitals_data_retrieving.data_consumption_tools.Entities.CryptoUtils import hash_data
        
        @profiler.profile_method("crypto_hashing_operations")
        def crypto_ops():
            # Probar operaciones de hashing
            test_data = "user_id_12345"
            
            # Multiple hashing operations
            for i in range(1000):
                hashed = hash_data(f"{test_data}_{i}")
            
            return hashed
        
        return crypto_ops()
    except ImportError:
        logger.warning("CryptoUtils no disponible para profiling")
        return None

def analyze_service_initialization():
    #"""Analiza performance de inicialización de servicios"""
    
    @profiler.profile_method("service_initialization")
    def init_services():
        # Medir tiempo de inicialización
        try:
            from vitals_data_retrieving.data_consumption_tools.wearable_devices_retrieving.FitbitDataRetriever import FitbitDataRetriever
            from vitals_data_retrieving.vitals_data_retrieving_service import VitalsDataRetrievingService
            
            start_time = time.time()
            retriever = FitbitDataRetriever()
            service = VitalsDataRetrievingService(retriever)
            initialization_time = time.time() - start_time
            
            return initialization_time
        except Exception as e:
            logger.info(f"Inicialización falló: {e}")
            return None
    
    return init_services()

def analyze_memory_usage():
    #"""Analiza uso de memoria de los algoritmos"""
    import psutil
    import os
    
    @profiler.profile_method("memory_usage_analysis")
    def memory_analysis():
        process = psutil.Process(os.getpid())
        
        # Medir memoria antes
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Ejecutar algunas operaciones
        operations = []
        for i in range(1000):
            operations.append({"data": "test" * 100, "index": i})
        
        # Medir memoria después
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = memory_after - memory_before
        
        return {
            "memory_before_mb": memory_before,
            "memory_after_mb": memory_after,
            "memory_increase_mb": memory_increase,
            "operations_count": len(operations)
        }
    
    return memory_analysis()

def generate_performance_report():
    """Genera reporte completo de performance"""
    report = {
        'project': 'SMIEAE - Vitals Data Consumption Service',
        'analysis_timestamp': datetime.now().isoformat(),
        'algorithms_analyzed': list(profiler.results.keys()),
        'performance_metrics': {},
        'detailed_analysis': profiler.results,
        'recommendations': [],
        'performance_benchmarks': {
            'excellent': {'max_time': 0.1, 'min_success_rate': 95},
            'good': {'max_time': 0.5, 'min_success_rate': 85},
            'needs_improvement': {'max_time': 1.0, 'min_success_rate': 70},
            'critical': {'max_time': 5.0, 'min_success_rate': 50}
        }
        
    }
    
    # Análisis de performance general
    if profiler.results:
        successful_operations = [r for r in profiler.results.values() if r['success']]
        
        report['performance_metrics'] = {
            'total_operations_analyzed': len(profiler.results),
            'successful_operations': len(successful_operations),
            'success_rate': (len(successful_operations) / len(profiler.results)) * 100,
            'average_execution_time': sum(r['execution_time'] for r in profiler.results.values()) / len(profiler.results),
            'total_analysis_time': sum(r['execution_time'] for r in profiler.results.values()),
            'fastest_operation': min(profiler.results.items(), key=lambda x: x[1]['execution_time'])[0] if successful_operations else 'N/A',
            'slowest_operation': max(profiler.results.items(), key=lambda x: x[1]['execution_time'])[0] if successful_operations else 'N/A'
        }
    
    # Generar recomendaciones basadas en benchmarks
    for op_name, data in profiler.results.items():
        execution_time = data['execution_time']
        success = data['success']
        
        if not success:
            report['recommendations'].append(f"🔴 REVISAR: {op_name} - Operación falló")
        elif execution_time > 1.0:
            report['recommendations'].append(f"🟠 OPTIMIZAR: {op_name} - Tiempo muy alto: {execution_time:.4f}s")
        elif execution_time > 0.5:
            report['recommendations'].append(f"🟡 MEJORAR: {op_name} - Tiempo alto: {execution_time:.4f}s")
        elif execution_time <= 0.1:
            report['recommendations'].append(f"🟢 EXCELENTE: {op_name} - Tiempo óptimo: {execution_time:.4f}s")
        else:
            report['recommendations'].append(f"🔵 ACEPTABLE: {op_name} - Tiempo: {execution_time:.4f}s")
    
    # Guardar reporte detallado
    with open('real_algorithm_performance_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # Guardar resumen ejecutivo
    summary = {
        'timestamp': report['analysis_timestamp'],
        'total_operations': report['performance_metrics']['total_operations_analyzed'],
        'success_rate': report['performance_metrics']['success_rate'],
        'avg_execution_time': report['performance_metrics']['average_execution_time'],
        'key_recommendations': report['recommendations'][:5]  # Top 5 recomendaciones
    }
    
    with open('performance_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    return report

def main():
    #"""Ejecuta análisis completo de performance"""
    print("🎯 REAL ALGORITHM PERFORMANCE ANALYSIS - SMIEAE")
    print("=" * 70)
    
    # Instalar psutil si no está disponible
    try:
        import psutil
    except ImportError:
        print("Instalando psutil para análisis de memoria...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'psutil'])
        import psutil
    
    # Ejecutar análisis de diferentes componentes
    print("\n1. 🚀 ANALIZANDO COMPONENTES DEL PROYECTO...")
    
    print("\n   🔐 Autenticación Fitbit...")
    analyze_fitbit_authentication()
    
    print("\n   📊 Procesamiento de datos...")
    analyze_data_processing()
    
    print("\n   🔒 Operaciones criptográficas...")
    analyze_crypto_operations()
    
    print("\n   ⚡ Inicialización de servicios...")
    analyze_service_initialization()
    
    print("\n   💾 Uso de memoria...")
    analyze_memory_usage()
    
    # Generar reporte
    print("\n2. 📊 GENERANDO REPORTE DE PERFORMANCE...")
    report = generate_performance_report()
    logger.info("AlgorithmPerformance", extra={
    'custom_dimensions': {
        'success_rate': report['performance_metrics']['success_rate'],
        'avg_execution_time': report['performance_metrics']['average_execution_time'],
        'fastest_operation': report['performance_metrics']['fastest_operation'],
        'slowest_operation': report['performance_metrics']['slowest_operation']
        }
    })
    
    # Mostrar resultados
    print("\n" + "=" * 70)
    print("📈 RESUMEN DE PERFORMANCE - ALGORITMOS REALES")
    print("=" * 70)
    
    metrics = report['performance_metrics']
    print(f"📊 Operaciones analizadas: {metrics['total_operations_analyzed']}")
    print(f"✅ Tasa de éxito: {metrics['success_rate']:.1f}%")
    print(f"⏱️  Tiempo promedio: {metrics['average_execution_time']:.4f}s")
    print(f"🕐 Tiempo total análisis: {metrics['total_analysis_time']:.4f}s")
    print(f"⚡ Operación más rápida: {metrics['fastest_operation']}")
    print(f"🐌 Operación más lenta: {metrics['slowest_operation']}")
    
    print(f"\n💡 RECOMENDACIONES PRINCIPALES:")
    for i, rec in enumerate(report['recommendations'][:5], 1):
        print(f"   {i}. {rec}")
    
    print(f"\n💾 ARCHIVOS GENERADOS:")
    print(f"   📄 real_algorithm_performance_report.json - Análisis detallado")
    print(f"   📋 performance_summary.json - Resumen ejecutivo")

if __name__ == "__main__":
    main()

# Métricas Prometheus
algorithm_time_gauge = Gauge('algorithm_execution_time_seconds', 'Execution time per algorithm', ['method'])
algorithm_success_gauge = Gauge('algorithm_success', 'Success rate per algorithm', ['method'])

@performance_bp.route('/performance_metrics')
def get_performance_metrics():
    for method, data in profiler.results.items():
        algorithm_time_gauge.labels(method).set(data['execution_time'])
        algorithm_success_gauge.labels(method).set(1 if data['success'] else 0)
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)