"""
Scanner - Módulo para escanear directorios y encontrar archivos
"""

import os
import dask.bag as db
from pathlib import Path
from src.utils import logger

def scan_directory(directory):
    """
    Escanea un directorio recursivamente y retorna lista de archivos
    """
    files = []
    directory_path = Path(directory)
    
    if not directory_path.exists():
        logger.get_logger().error(f"El directorio {directory} no existe")
        return []
    
    logger.get_logger().info(f"Escaneando directorio: {directory}")
    
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            files.append(file_path)
    
    logger.get_logger().info(f"Encontrados {len(files)} archivos en {directory}")
    return files

def scan_directories(directories, parallel=True):
    """
    Escanea múltiples directorios utilizando paralelismo con Dask
    """
    if parallel:
        try:
            # Utilizar Dask para paralelizar el escaneo
            directories_bag = db.from_sequence(directories)
            all_files = directories_bag.map(scan_directory).flatten().compute()
        except Exception as e:
            logger.get_logger().warning(f"Error en escaneo paralelo: {e}, cambiando a secuencial")
            # Fallback a versión secuencial
            all_files = []
            for directory in directories:
                all_files.extend(scan_directory(directory))
    else:
        # Versión secuencial
        all_files = []
        for directory in directories:
            all_files.extend(scan_directory(directory))
    
    logger.get_logger().info(f"Total de archivos encontrados: {len(all_files)}")
    return all_files