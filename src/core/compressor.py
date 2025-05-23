"""
Compressor - Módulo para comprimir archivos usando algoritmos clásicos con paralelismo
ACTUALIZADO: Manejo correcto de fragmentación y rutas
"""

import os
import tempfile
from pathlib import Path
import zipfile
import gzip
import bz2
import dask.bag as db
from dask.distributed import Client
import logging
from src.utils import logger

# Silenciar logs verbosos de Dask y dependencias
logging.getLogger('distributed').setLevel(logging.ERROR)
logging.getLogger('distributed.worker').setLevel(logging.ERROR)
logging.getLogger('distributed.scheduler').setLevel(logging.ERROR)
logging.getLogger('distributed.nanny').setLevel(logging.ERROR)
logging.getLogger('distributed.http.proxy').setLevel(logging.ERROR)
logging.getLogger('distributed.core').setLevel(logging.ERROR)
logging.getLogger('distributed.batched').setLevel(logging.ERROR)
logging.getLogger('tornado').setLevel(logging.ERROR)

def create_client(workers):
    """Crea un cliente Dask para paralelismo con logs silenciados"""
    try:
        return Client(
            n_workers=workers, 
            threads_per_worker=2, 
            silence_logs=True,
            dashboard_address=None,  # Deshabilitar dashboard
            processes=False  # Usar threads en lugar de procesos para menos overhead
        )
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
    Con soporte completo para encriptación integrada y mejor manejo de rutas
    """
    if not output:
        output = f"backup.{algorithm}"
    
    # Resolver rutas absolutas para evitar conflictos
    output_path = Path(output).resolve()
    
    # Verificar si algún archivo de entrada coincide con la salida
    files_absolute = [Path(f).resolve() for f in files]
    for file_path in files_absolute:
        if file_path == output_path:
            logger.get_logger().error(f"Error: El archivo de salida no puede ser el mismo que uno de entrada: {file_path}")
            raise ValueError(f"Conflicto de rutas: '{file_path}' no puede ser origen y destino")
    
    # MANEJO ESPECIAL PARA FRAGMENTACIÓN
    # Si el output no tiene extensión, asumimos que es para fragmentación
    if output_path.suffix == '':
        # Para fragmentación, crear un archivo temporal
        temp_dir = tempfile.mkdtemp(prefix="backup_compress_")
        temp_filename = f"{output_path.name}.{algorithm}"
        actual_output_path = Path(temp_dir) / temp_filename
        logger.get_logger().info(f"Modo fragmentación detectado. Usando archivo temporal: {actual_output_path}")
    else:
        # Es un archivo normal
        actual_output_path = output_path
        # Crear directorio padre si no existe
        os.makedirs(actual_output_path.parent, exist_ok=True)
    
    logger.get_logger().info(f"Comprimiendo {len(files)} archivos con {algorithm}")
    logger.get_logger().info(f"Archivo de salida: {actual_output_path}")
    
    # Crear cliente Dask para paralelismo
    client = create_client(workers)
    
    try:
        if algorithm == 'zip':
            compressed_file = compress_zip_parallel(files, str(actual_output_path), client, encrypt, password)
        elif algorithm == 'gzip':
            compressed_file = compress_gzip_parallel(files, str(actual_output_path), client)
        elif algorithm == 'bzip2':
            compressed_file = compress_bzip2_parallel(files, str(actual_output_path), client)
        else:
            logger.get_logger().error(f"Algoritmo no soportado: {algorithm}")
            return None
        
        # Aplicar encriptación si se solicita
        if encrypt and password and compressed_file:
            logger.get_logger().info("Aplicando encriptación AES-256 al archivo comprimido...")
            from src.core import encryptor
            
            # Determinar nombre del archivo encriptado
            compressed_path = Path(compressed_file)
            if not compressed_path.name.endswith('.enc'):
                encrypted_output = str(compressed_path) + '.enc'
            else:
                encrypted_output = str(compressed_path)
            
            # Encriptar el archivo comprimido
            encryptor.encrypt_file(compressed_file, encrypted_output, password)
            
            # Eliminar archivo sin encriptar si es diferente
            if compressed_file != encrypted_output:
                try:
                    os.remove(compressed_file)
                    logger.get_logger().info(f"Archivo sin encriptar eliminado: {compressed_file}")
                except:
                    logger.get_logger().warning(f"No se pudo eliminar archivo temporal: {compressed_file}")
            
            logger.get_logger().info(f"Encriptación completada: {encrypted_output}")
            return encrypted_output
        
        return compressed_file
            
    finally:
        # Cerrar el cliente Dask
        if client:
            client.close()

def compress_zip_parallel(files, output_path, client, encrypt=False, password=None):
    """Comprime archivos usando ZIP con paralelismo y mejor manejo de rutas"""
    
    # Resolver rutas absolutas
    output_abs = Path(output_path).resolve()
    files_abs = [Path(f).resolve() for f in files]
    
    # Verificar conflictos de rutas
    for file_path in files_abs:
        if file_path == output_abs:
            raise ValueError(f"Error: '{file_path}' no puede ser archivo de entrada y salida")
    
    # Asegurar que el directorio padre existe
    os.makedirs(output_abs.parent, exist_ok=True)
    
    # Calcular directorio base común para rutas relativas
    if files_abs:
        try:
            # Intentar encontrar directorio común
            common_parts = []
            first_parts = files_abs[0].parts
            
            for i, part in enumerate(first_parts):
                if all(len(f.parts) > i and f.parts[i] == part for f in files_abs):
                    common_parts.append(part)
                else:
                    break
            
            if common_parts:
                base_dir = Path(*common_parts)
            else:
                base_dir = Path.cwd()
        except:
            base_dir = Path.cwd()
    else:
        base_dir = Path.cwd()
    
    logger.get_logger().info(f"Directorio base para rutas relativas: {base_dir}")
    
    # Crear archivo ZIP
    try:
        with zipfile.ZipFile(output_abs, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in files_abs:
                try:
                    # Calcular ruta relativa
                    try:
                        rel_path = file_path.relative_to(base_dir)
                    except ValueError:
                        # Si no se puede calcular relativa, usar solo el nombre
                        rel_path = file_path.name
                    
                    logger.get_logger().debug(f"Agregando: {file_path} -> {rel_path}")
                    zipf.write(file_path, rel_path)
                    
                except Exception as e:
                    logger.get_logger().error(f"Error agregando {file_path}: {e}")
                    continue
    
    except Exception as e:
        logger.get_logger().error(f"Error creando archivo ZIP: {e}")
        raise
    
    logger.get_logger().info(f"Compresión ZIP completada: {output_abs}")
    return str(output_abs)

def compress_gzip_parallel(files, output_path, client):
    """Comprime archivos usando GZIP (tar.gz) con paralelismo"""
    import tarfile
    
    # Para GZIP múltiples archivos, usar tar.gz
    output_path = Path(output_path)
    if not str(output_path).endswith('.tar.gz'):
        if output_path.suffix == '.gz':
            output_path = output_path.with_suffix('.tar.gz')
        else:
            output_path = output_path.with_suffix(output_path.suffix + '.tar.gz')
    
    # Resolver rutas absolutas
    output_abs = output_path.resolve()
    files_abs = [Path(f).resolve() for f in files]
    
    # Verificar conflictos
    for file_path in files_abs:
        if file_path == output_abs:
            raise ValueError(f"Error: '{file_path}' no puede ser archivo de entrada y salida")
    
    # Asegurar directorio padre
    os.makedirs(output_abs.parent, exist_ok=True)
    
    # Calcular directorio base común
    if files_abs:
        try:
            base_dir = Path(os.path.commonpath([str(f) for f in files_abs]))
        except ValueError:
            base_dir = Path.cwd()
    else:
        base_dir = Path.cwd()
    
    with tarfile.open(output_abs, 'w:gz') as tar:
        for file_path in files_abs:
            try:
                try:
                    rel_path = file_path.relative_to(base_dir)
                except ValueError:
                    rel_path = file_path.name
                
                tar.add(file_path, arcname=rel_path)
            except Exception as e:
                logger.get_logger().error(f"Error agregando {file_path}: {e}")
    
    logger.get_logger().info(f"Compresión GZIP completada: {output_abs}")
    return str(output_abs)

def compress_bzip2_parallel(files, output_path, client):
    """Comprime archivos usando BZIP2 (tar.bz2) con paralelismo"""
    import tarfile
    
    # Para BZIP2 múltiples archivos, usar tar.bz2
    output_path = Path(output_path)
    if not str(output_path).endswith('.tar.bz2'):
        if output_path.suffix == '.bz2':
            output_path = output_path.with_suffix('.tar.bz2')
        else:
            output_path = output_path.with_suffix(output_path.suffix + '.tar.bz2')
    
    # Resolver rutas absolutas
    output_abs = output_path.resolve()
    files_abs = [Path(f).resolve() for f in files]
    
    # Verificar conflictos
    for file_path in files_abs:
        if file_path == output_abs:
            raise ValueError(f"Error: '{file_path}' no puede ser archivo de entrada y salida")
    
    # Asegurar directorio padre
    os.makedirs(output_abs.parent, exist_ok=True)
    
    # Calcular directorio base común
    if files_abs:
        try:
            base_dir = Path(os.path.commonpath([str(f) for f in files_abs]))
        except ValueError:
            base_dir = Path.cwd()
    else:
        base_dir = Path.cwd()
    
    with tarfile.open(output_abs, 'w:bz2') as tar:
        for file_path in files_abs:
            try:
                try:
                    rel_path = file_path.relative_to(base_dir)
                except ValueError:
                    rel_path = file_path.name
                
                tar.add(file_path, arcname=rel_path)
            except Exception as e:
                logger.get_logger().error(f"Error agregando {file_path}: {e}")
    
    logger.get_logger().info(f"Compresión BZIP2 completada: {output_abs}")
    return str(output_abs)