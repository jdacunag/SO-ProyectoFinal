import sys
from functools import wraps
from src.utils import logger

class BackupError(Exception):
    """Excepción base para errores en el sistema de backup"""
    pass

class CompressionError(BackupError):
    """Error durante la compresión"""
    pass

class EncryptionError(BackupError):
    """Error durante la encriptación"""
    pass

class StorageError(BackupError):
    """Error durante el almacenamiento"""
    pass

class RestoreError(BackupError):
    """Error durante la restauración"""
    pass

def handle_error(func):
    """
    Decorador para manejar errores de forma consistente
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BackupError as e:
            logger.get_logger().error(f"Error en operación de backup: {str(e)}")
            raise
        except Exception as e:
            logger.get_logger().error(f"Error inesperado: {str(e)}", exc_info=True)
            # Convertir a un tipo de error específico del backup
            raise BackupError(f"Error inesperado: {str(e)}")
    
    return wrapper

def retry(max_attempts=3, exceptions=(Exception,)):
    """
    Decorador para reintentar una función en caso de error
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    logger.get_logger().warning(
                        f"Intento {attempt+1}/{max_attempts} fallido: {str(e)}"
                    )
            
            # Si llegamos aquí, todos los intentos fallaron
            raise last_exception
        
        return wrapper
    
    return decorator

def safe_cloud_operation(operation_func):
    """
    Decorador específico para operaciones en la nube, manejando problemas de conexión
    """
    @wraps(operation_func)
    @retry(max_attempts=3, exceptions=(ConnectionError, TimeoutError))
    def wrapper(*args, **kwargs):
        try:
            return operation_func(*args, **kwargs)
        except ConnectionError as e:
            logger.get_logger().error(f"Error de conexión a la nube: {str(e)}")
            raise StorageError(f"Error de conexión a la nube: {str(e)}")
        except TimeoutError as e:
            logger.get_logger().error(f"Tiempo de espera agotado en operación en la nube: {str(e)}")
            raise StorageError(f"Tiempo de espera agotado: {str(e)}")
        except Exception as e:
            logger.get_logger().error(f"Error en operación en la nube: {str(e)}")
            raise StorageError(f"Error en almacenamiento en la nube: {str(e)}")
    
    return wrapper