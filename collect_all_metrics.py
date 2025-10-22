from algorithm_profiler import main as analyze_algorithm
from live_user_metrics import LiveMetricsCollector
import json
import os

def collect_all():
    print(" Ejecutando análisis de algoritmo...")
    analyze_algorithm()

    print("\n👥 Recolectando métricas de usuarios (Fitbit simulados)...")
    azure_url = os.getenv("AZURE_APP_URL", "http://127.0.0.1:5000")
    collector = LiveMetricsCollector(azure_url)
    collector.simulate_user_activity(3)
    user_report = collector.generate_live_report()

    # Cargar resultados del profiler
    with open('performance_summary.json') as f:
        algorithm_summary = json.load(f)

    final_report = {
        "algorithm_summary": algorithm_summary,
        "user_metrics": user_report,
    }

    with open('integrated_metrics_report.json', 'w') as f:
        json.dump(final_report, f, indent=2)

    print("\n Reporte integrado generado: integrated_metrics_report.json")

if __name__ == "__main__":
    collect_all()