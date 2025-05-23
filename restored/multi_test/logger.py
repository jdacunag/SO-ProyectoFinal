"""
Logger - Sistema de logging para el sistema de backup
"""

import logging
import os
import sys
from datetime import datetime

# Singleton para el logger
_logger = None

def setup_logger(level='INFO', log_file=None):
    """
    Configura el logger global
    """
    global _logger
    
    if _logger is not None:
        return _logger
    
    # Crear logger
    _logger = logging.getLogger('secure_backup')
    
    # Configurar nivel de log
    log_level = getattr(logging, level.upper(), logging.INFO)
    _logger.setLevel(log_level)
    
    # Crear formateador
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Añadir handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    _logger.addHandler(console_handler)
    
    # Añadir handler para archivo si se especifica
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        _logger.addHandler(file_handler)
    else:
        # Si no se especifica, crear un archivo de log con la fecha actual
        log_dir = os.path.join(os.getcwd(), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        default_log_file = os.path.join(log_dir, f'secure_backup_{timestamp}.log')
        
        file_handler = logging.FileHandler(default_log_file)
        file_handler.setFormatter(formatter)
        _logger.addHandler(file_handler)
    
    return _logger

def get_logger():
    """
    Obtiene el logger global, inicializando con valores
    predeterminados si no ha sido configurado
    """
    global _logger
    
    if _logger is None:
        _logger = setup_logger()
    
    return _logger