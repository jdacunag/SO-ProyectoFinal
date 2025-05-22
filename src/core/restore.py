"""
Restore - Módulo para restaurar backups comprimidos/encriptados
"""

import os
import zipfile
import gzip
import bz2
import shutil
import tarfile
from pathlib import Path
import dask.bag as db
from src.utils import logger
from src.core import encryptor

def restore_backup(backup_path, output_dir, password=None):
    """
    Restaura un backup a partir de un archivo o directorio
    """
    backup_path = Path(backup_path)
    output_dir = Path(output_dir)
    
    # Asegurarse de que el directorio de salida existe
    os.makedirs(output_dir, exist_ok=True)
    
    logger.get_logger().info(f"Restaurando backup desde: {backup_path}")
    
    # Determinar el tipo de backup
    if backup_path.is_dir():
        # Es un backup fragmentado
        return restore_fragments(backup_path, output_dir)
    else:
        # Es un archivo de backup
        extension = backup_path.suffix.lower()
        
        if extension == '.enc':  # Archivo encriptado
            if not password:
                raise ValueError("Se requiere contraseña para restaurar un backup encriptado")
            
            # Desencriptar primero
            temp_file = backup_path.with_suffix('.tmp')
            encryptor.decrypt_file(str(backup_path), str(temp_file), password)
            
            # Determinar el tipo y restaurar
            result = restore_backup(temp_file, output_dir)
            
            # Limpiar archivo temporal
            os.unlink(temp_file)
            return result
            
        elif extension == '.zip':
            return restore_zip(backup_path, output_dir, password)
        elif extension == '.gz':
            if str(backup_path).endswith('.tar.gz'):
                return restore_tar_gz(backup_path, output_dir)
            else:
                return restore_gzip(backup_path, output_dir)
        elif extension == '.bz2':
            if str(backup_path).endswith('.tar.bz2'):
                return restore_tar_bz2(backup_path, output_dir)
            else:
                return restore_bzip2(backup_path, output_dir)
        else:
            logger.get_logger().error(f"Formato de backup no soportado: {extension}")
            raise ValueError(f"Formato de backup no soportado: {extension}")

def restore_zip(zip_path, output_dir, password=None):
    """
    Restaura un backup ZIP
    """
    logger.get_logger().info(f"Restaurando archivo ZIP: {zip_path}")
    
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        if password:
            # Si hay contraseña, verificarla
            try:
                zipf.extractall(path=output_dir, pwd=password.encode())
            except RuntimeError as e:
                logger.get_logger().error(f"Error al extraer ZIP: {e}")
                raise ValueError("Contraseña incorrecta o archivo ZIP dañado")
        else:
            zipf.extractall(path=output_dir)
    
    logger.get_logger().info(f"Backup ZIP restaurado en: {output_dir}")
    return output_dir

def restore_tar_gz(tar_gz_path, output_dir):
    """
    Restaura un archivo comprimido con TAR.GZ
    """
    logger.get_logger().info(f"Restaurando archivo TAR.GZ: {tar_gz_path}")
    
    with tarfile.open(tar_gz_path, 'r:gz') as tar:
        tar.extractall(path=output_dir)
    
    logger.get_logger().info(f"Archivo TAR.GZ restaurado en: {output_dir}")
    return output_dir

def restore_tar_bz2(tar_bz2_path, output_dir):
    """
    Restaura un archivo comprimido con TAR.BZ2
    """
    logger.get_logger().info(f"Restaurando archivo TAR.BZ2: {tar_bz2_path}")
    
    with tarfile.open(tar_bz2_path, 'r:bz2') as tar:
        tar.extractall(path=output_dir)
    
    logger.get_logger().info(f"Archivo TAR.BZ2 restaurado en: {output_dir}")
    return output_dir

def restore_gzip(gzip_path, output_dir):
    """
    Restaura un archivo comprimido con GZIP
    """
    logger.get_logger().info(f"Restaurando archivo GZIP: {gzip_path}")
    
    # GZIP comprime un solo archivo, extraemos su nombre base
    output_file = output_dir / gzip_path.stem
    
    with gzip.open(gzip_path, 'rb') as f_in:
        with open(output_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    logger.get_logger().info(f"Archivo GZIP restaurado en: {output_file}")
    return output_file

def restore_bzip2(bzip2_path, output_dir):
    """
    Restaura un archivo comprimido con BZIP2
    """
    logger.get_logger().info(f"Restaurando archivo BZIP2: {bzip2_path}")
    
    # BZIP2 comprime un solo archivo, extraemos su nombre base
    output_file = output_dir / bzip2_path.stem
    
    with bz2.open(bzip2_path, 'rb') as f_in:
        with open(output_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    logger.get_logger().info(f"Archivo BZIP2 restaurado en: {output_file}")
    return output_file

def restore_fragments(fragments_dir, output_dir):
    """
    Restaura un archivo a partir de sus fragmentos
    """
    logger.get_logger().info(f"Restaurando desde fragmentos: {fragments_dir}")
    
    # Leer metadatos
    metadata_path = next(Path(fragments_dir).glob("*.metadata"), None)
    
    if not metadata_path:
        logger.get_logger().error("No se encontraron metadatos en el directorio de fragmentos")
        raise ValueError("No se encontraron metadatos en el directorio de fragmentos")
    
    metadata = {}
    with open(metadata_path, 'r') as f:
        for line in f:
            if ': ' in line:
                key, value = line.strip().split(': ', 1)
                metadata[key] = value
    
    original_filename = os.path.basename(metadata['original_file'])
    output_file = os.path.join(output_dir, original_filename)
    
    # Buscar todos los fragmentos
    fragment_paths = sorted(Path(fragments_dir).glob("*.part*"))
    
    if not fragment_paths:
        logger.get_logger().error("No se encontraron fragmentos en el directorio")
        raise ValueError("No se encontraron fragmentos en el directorio")
    
    logger.get_logger().info(f"Combinando {len(fragment_paths)} fragmentos...")
    
    # Combinar fragmentos
    with open(output_file, 'wb') as f_out:
        for fragment_path in fragment_paths:
            logger.get_logger().info(f"Procesando fragmento: {fragment_path.name}")
            with open(fragment_path, 'rb') as f_in:
                shutil.copyfileobj(f_in, f_out)
    
    logger.get_logger().info(f"Fragmentos restaurados en: {output_file}")
    
    # Verificar tamaño si está en metadatos
    if 'file_size' in metadata:
        expected_size = int(metadata['file_size'])
        actual_size = os.path.getsize(output_file)
        if expected_size == actual_size:
            logger.get_logger().info("✅ Verificación de tamaño exitosa")
        else:
            logger.get_logger().warning(f"⚠️  Tamaño no coincide: esperado {expected_size}, actual {actual_size}")
    
    # Ahora restaurar el archivo combinado si es un backup comprimido
    file_extension = Path(output_file).suffix.lower()
    if file_extension in ['.zip', '.gz', '.bz2', '.enc']:
        logger.get_logger().info("Detectado archivo comprimido, extrayendo contenido...")
        temp_extract_dir = output_dir / 'extracted'
        result = restore_backup(output_file, temp_extract_dir)
        
        # Mover contenido extraído al directorio principal
        if temp_extract_dir.exists():
            for item in temp_extract_dir.iterdir():
                shutil.move(str(item), str(output_dir))
            shutil.rmtree(temp_extract_dir)
        
        # Eliminar el archivo comprimido temporal
        os.remove(output_file)
        
        return output_dir
    
    return output_file