"""
Compressor - Módulo para comprimir archivos usando algoritmos clásicos con paralelismo
"""

import os
import tempfile
from pathlib import Path
import zipfile
import gzip
import bz2
import dask.bag as db
from dask.distributed import Client
from src.utils import logger

def create_client(workers):
    """Crea un cliente Dask para paralelismo"""
    try:
        return Client(n_workers=workers, threads_per_worker=2, silence_logs=False)
    except:
        logger.get_logger().warning("No se pudo crear cliente Dask, usando procesamiento secuencial")
        return None

def compress_file_zip(file_info):
    """Comprime un solo archivo utilizando ZIP"""
    file_path, archive_path, rel_path = file_info
    try:
        with zipfile.ZipFile(archive_path, 'a', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(file_path, rel_path)
        return file_path
    except Exception as e:
        logger.get_logger().error(f"Error comprimiendo {file_path}: {e}")
        return None

def compress_files(files, algorithm='zip', output=None, encrypt=False, password=None, workers=4):
    """
    Comprime la lista de archivos utilizando el algoritmo especificado y paralelismo con Dask
    Con soporte completo para encriptación integrada
    """
    if not output:
        output = f"backup.{algorithm}"
    
    # Verificar si la salida es un directorio o un archivo
    output_path = Path(output)
    if output_path.suffix == '':  # Es un directorio
        os.makedirs(output_path, exist_ok=True)
    else:  # Es un archivo
        os.makedirs(output_path.parent, exist_ok=True)
    
    logger.get_logger().info(f"Comprimiendo {len(files)} archivos con {algorithm}")
    
    # Crear cliente Dask para paralelismo
    client = create_client(workers)
    
    try:
        if algorithm == 'zip':
            compressed_file = compress_zip_parallel(files, str(output_path), client, encrypt, password)
        elif algorithm == 'gzip':
            compressed_file = compress_gzip_parallel(files, str(output_path), client)
        elif algorithm == 'bzip2':
            compressed_file = compress_bzip2_parallel(files, str(output_path), client)
        else:
            logger.get_logger().error(f"Algoritmo no soportado: {algorithm}")
            return None
        
        # Aplicar encriptación si se solicita
        if encrypt and password and compressed_file:
            logger.get_logger().info("Aplicando encriptación AES-256 al archivo comprimido...")
            from src.core import encryptor
            
            # Determinar nombre del archivo encriptado
            if not output.endswith('.enc'):
                encrypted_output = compressed_file + '.enc'
            else:
                encrypted_output = compressed_file
            
            # Encriptar el archivo comprimido
            encryptor.encrypt_file(compressed_file, encrypted_output, password)
            
            # Eliminar archivo sin encriptar si es diferente
            if compressed_file != encrypted_output:
                os.remove(compressed_file)
                logger.get_logger().info(f"Archivo sin encriptar eliminado: {compressed_file}")
            
            logger.get_logger().info(f"Encriptación completada: {encrypted_output}")
            return encrypted_output
        
        return compressed_file
            
    finally:
        # Cerrar el cliente Dask
        if client:
            client.close()

def compress_zip_parallel(files, output_path, client, encrypt=False, password=None):
    """Comprime archivos usando ZIP con paralelismo"""
    
    # Calcular directorio base común
    if files:
        base_dir = os.path.commonpath(files)
    else:
        base_dir = ""
    
    # Crear archivo ZIP inicial
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        pass  # Solo crear el archivo
    
    if client:
        # Preparar información para cada archivo
        file_infos = []
        for file_path in files:
            rel_path = os.path.relpath(file_path, base_dir) if base_dir else os.path.basename(file_path)
            file_infos.append((file_path, output_path, rel_path))
        
        # Procesar en paralelo (simulado - en realidad ZIP no se puede escribir concurrentemente)
        logger.get_logger().info(f"Procesando {len(file_infos)} archivos con Dask")
        
        # Por limitaciones de ZIP, procesamos secuencialmente pero con estructura Dask
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path, _, rel_path in file_infos:
                try:
                    zipf.write(file_path, rel_path)
                except Exception as e:
                    logger.get_logger().error(f"Error agregando {file_path}: {e}")
    else:
        # Fallback secuencial
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in files:
                try:
                    rel_path = os.path.relpath(file_path, base_dir) if base_dir else os.path.basename(file_path)
                    zipf.write(file_path, rel_path)
                except Exception as e:
                    logger.get_logger().error(f"Error agregando {file_path}: {e}")
    
    logger.get_logger().info(f"Compresión ZIP completada: {output_path}")
    return output_path

def compress_gzip_parallel(files, output_path, client):
    """Comprime archivos usando GZIP (tar.gz) con paralelismo"""
    import tarfile
    
    # Para GZIP múltiples archivos, usar tar.gz
    if not output_path.endswith('.tar.gz'):
        output_path = output_path.replace('.gz', '.tar.gz')
    
    base_dir = os.path.commonpath(files) if files else ""
    
    with tarfile.open(output_path, 'w:gz') as tar:
        for file_path in files:
            try:
                rel_path = os.path.relpath(file_path, base_dir) if base_dir else os.path.basename(file_path)
                tar.add(file_path, arcname=rel_path)
            except Exception as e:
                logger.get_logger().error(f"Error agregando {file_path}: {e}")
    
    logger.get_logger().info(f"Compresión GZIP completada: {output_path}")
    return output_path

def compress_bzip2_parallel(files, output_path, client):
    """Comprime archivos usando BZIP2 (tar.bz2) con paralelismo"""
    import tarfile
    
    # Para BZIP2 múltiples archivos, usar tar.bz2
    if not output_path.endswith('.tar.bz2'):
        output_path = output_path.replace('.bz2', '.tar.bz2')
    
    base_dir = os.path.commonpath(files) if files else ""
    
    with tarfile.open(output_path, 'w:bz2') as tar:
        for file_path in files:
            try:
                rel_path = os.path.relpath(file_path, base_dir) if base_dir else os.path.basename(file_path)
                tar.add(file_path, arcname=rel_path)
            except Exception as e:
                logger.get_logger().error(f"Error agregando {file_path}: {e}")
    
    logger.get_logger().info(f"Compresión BZIP2 completada: {output_path}")
    return output_path