import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class UserMetricsTracker:
    def __init__(self):
        self.operations = []

    def track_user_operation(self, operation_name):
        """Decorador para registrar operación del usuario."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    success = True
                except Exception as e:
                    logger.error(f"Error en {operation_name}: {e}")
                    result = ({"error": str(e)}, 500)
                    success = False
                duration = time.time() - start_time
                self.operations.append({
                    "operation": operation_name,
                    "duration": duration,
                    "success": success,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                })
                return result
            wrapper.__name__ = f"{func.__name__}_{operation_name}"
            return wrapper
        return decorator

user_tracker = UserMetricsTracker()