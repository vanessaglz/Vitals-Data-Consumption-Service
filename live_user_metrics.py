import requests
import time
import json
from datetime import datetime
from pymongo import MongoClient
import os


class LiveMetricsCollector:
    def __init__(self, azure_url):
        self.azure_url = azure_url
        self.metrics = {
            'start_time': datetime.now().isoformat(),
            'requests': [],
            'user_activity': {}
        }
    
    def simulate_user_activity(self, user_count=5):
        #Simula actividad de usuarios reales
        print(f"👥 SIMULANDO {user_count} USUARIOS ACTIVOS")
        print("=" * 50)
        
        for i in range(user_count):
            user_id = f"test_user_{i+1}"
            print(f"\n🔍 Usuario: {user_id}")
            
            # Simular diferentes operaciones
            operations = [
                self.test_get_user_info,
                self.test_get_vitals_data,
                self.test_connect_to_api
            ]
            
            for operation in operations:
                operation(user_id)
                time.sleep(1)  # Pausa entre operaciones
    
    def test_get_user_info(self, user_id):
        #Test endpoint get_user_info
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.azure_url}/vitals_data_retrieving/get_user_info",
                json={"user_id": user_id},
                timeout=10
            )
            execution_time = time.time() - start_time
            
            self.record_metric(
                user_id=user_id,
                operation='get_user_info',
                execution_time=execution_time,
                success=response.status_code == 200,
                status_code=response.status_code
            )
            
            print(f"   ✅ get_user_info: {execution_time:.3f}s - Status: {response.status_code}")
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.record_metric(
                user_id=user_id,
                operation='get_user_info',
                execution_time=execution_time,
                success=False,
                error=str(e)
            )
            print(f"   ❌ get_user_info: Error - {e}")
    
    def test_get_vitals_data(self, user_id):
        #Test endpoint get_vitals_data
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.azure_url}/vitals_data_retrieving/get_vitals_data",
                json={
                    "user_id": user_id,
                    "date": "2024-01-15",
                    "scope": ["heart_rate", "sleep"],
                    "db_storage": False
                },
                timeout=10
            )
            execution_time = time.time() - start_time
            
            self.record_metric(
                user_id=user_id,
                operation='get_vitals_data',
                execution_time=execution_time,
                success=response.status_code == 200,
                status_code=response.status_code
            )
            
            print(f"   ✅ get_vitals_data: {execution_time:.3f}s - Status: {response.status_code}")
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.record_metric(
                user_id=user_id,
                operation='get_vitals_data',
                execution_time=execution_time,
                success=False,
                error=str(e)
            )
            print(f"   ❌ get_vitals_data: Error - {e}")
    
    def test_connect_to_api(self, user_id):
        #Test endpoint connect_to_api
        start_time = time.time()
        try:
            response = requests.get(
                f"{self.azure_url}/vitals_data_retrieving/connect_to_api",
                timeout=10
            )
            execution_time = time.time() - start_time
            
            self.record_metric(
                user_id=user_id,
                operation='connect_to_api',
                execution_time=execution_time,
                success=response.status_code == 200,
                status_code=response.status_code
            )
            
            print(f"   ✅ connect_to_api: {execution_time:.3f}s - Status: {response.status_code}")
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.record_metric(
                user_id=user_id,
                operation='connect_to_api',
                execution_time=execution_time,
                success=False,
                error=str(e)
            )
            print(f"   ❌ connect_to_api: Error - {e}")
    
    def record_metric(self, user_id, operation, execution_time, success, status_code=None, error=None):
        #Registra métricas individuales
        metric = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'operation': operation,
            'execution_time': execution_time,
            'success': success,
            'status_code': status_code,
            'error': error
        }
        
        self.metrics['requests'].append(metric)
        
        # Actualizar actividad por usuario
        if user_id not in self.metrics['user_activity']:
            self.metrics['user_activity'][user_id] = {
                'operations': 0,
                'total_time': 0,
                'successful_operations': 0
            }
        
        user_activity = self.metrics['user_activity'][user_id]
        user_activity['operations'] += 1
        user_activity['total_time'] += execution_time
        
        if success:
            user_activity['successful_operations'] += 1
        
        try:
            mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/vitals_db")
            client = MongoClient(mongo_uri)
            db = client.get_default_database()
            db['metrics_user_live'].insert_one(metric)
        except Exception as e:
            print(f" Error guardando métrica en MongoDB: {e}")
    
    def generate_live_report(self):
        #Genera reporte en tiempo real
        total_requests = len(self.metrics['requests'])
        successful_requests = sum(1 for r in self.metrics['requests'] if r['success'])
        
        if total_requests > 0:
            success_rate = (successful_requests / total_requests) * 100
            avg_time = sum(r['execution_time'] for r in self.metrics['requests']) / total_requests
        else:
            success_rate = 0
            avg_time = 0
        
        report = {
            'collection_period': {
                'start': self.metrics['start_time'],
                'end': datetime.now().isoformat(),
                'duration_seconds': (datetime.now() - datetime.fromisoformat(self.metrics['start_time'])).total_seconds()
            },
            'summary': {
                'total_users': len(self.metrics['user_activity']),
                'total_requests': total_requests,
                'success_rate': success_rate,
                'average_response_time': avg_time,
                'requests_per_second': total_requests / ((datetime.now() - datetime.fromisoformat(self.metrics['start_time'])).total_seconds() or 1)
            },
            'user_activity': self.metrics['user_activity'],
            'detailed_requests': self.metrics['requests'][-100:]  # Últimas 100 requests
        }
        
        # Guardar reporte
        with open('live_metrics_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        return report

# Uso
if __name__ == "__main__":
    azure_url = "https://smieae-cic-f7anavbdh9fdc6c5.canadacentral-01.azurewebsites.net"
    collector = LiveMetricsCollector(azure_url)
    
    print("🎯 COLECTANDO MÉTRICAS DE USUARIOS EN TIEMPO REAL")
    print("=" * 60)
    
    # Simular actividad de usuarios
    collector.simulate_user_activity(3)
    
    # Generar reporte
    report = collector.generate_live_report()
    
    print(f"\n📊 REPORTE FINAL:")
    print(f"   👥 Usuarios únicos: {report['summary']['total_users']}")
    print(f"   📨 Total requests: {report['summary']['total_requests']}")
    print(f"   ✅ Tasa de éxito: {report['summary']['success_rate']:.1f}%")
    print(f"   ⏱️  Tiempo promedio: {report['summary']['average_response_time']:.3f}s")
    print(f"   🚀 Requests/segundo: {report['summary']['requests_per_second']:.2f}")