"""
Storage - Módulo para gestionar diferentes opciones de almacenamiento
"""

import os
import shutil
from pathlib import Path
import dask.bag as db
from src.utils import logger

def store_local(source_file, destination):
    """
    Almacena el archivo de backup en un destino local (posiblemente disco externo)
    """
    logger.get_logger().info(f"Almacenando archivo en destino local: {destination}")
    
    # Asegurarse de que el directorio destino existe
    destination_path = Path(destination)
    os.makedirs(destination_path.parent, exist_ok=True)
    
    # Copiar archivo
    shutil.copy2(source_file, destination)
    logger.get_logger().info(f"Archivo almacenado correctamente en: {destination}")
    return destination

def store_cloud(source_file, service_name, credentials=None):
    """
    Almacena el archivo de backup en un servicio en la nube
    """
    logger.get_logger().info(f"Almacenando archivo en la nube usando {service_name}")
    
    if service_name == 'gdrive':
        return _upload_to_gdrive(source_file, credentials)
    elif service_name == 'dropbox':
        return _upload_to_dropbox(source_file, credentials)
    else:
        logger.get_logger().error(f"Servicio de nube no soportado: {service_name}")
        raise ValueError(f"Servicio de nube no soportado: {service_name}")

def _upload_to_gdrive(source_file, credentials=None):
    """
    Sube un archivo a Google Drive (implementación simulada)
    """
    logger.get_logger().info("Simulando subida a Google Drive...")
    
    # En una implementación real, aquí usarías la API de Google Drive
    # from googleapiclient.discovery import build
    # from google.auth.transport.requests import Request
    # etc.
    
    # Simulación de subida
    upload_path = f"gdrive://{os.path.basename(source_file)}"
    logger.get_logger().info(f"Archivo subido a: {upload_path}")
    
    print(f"☁️  Simulación: Archivo subido a Google Drive como {upload_path}")
    return upload_path

def _upload_to_dropbox(source_file, credentials=None):
    """
    Sube un archivo a Dropbox (implementación simulada)
    """
    logger.get_logger().info("Simulando subida a Dropbox...")
    
    # En una implementación real, aquí usarías la API de Dropbox
    # import dropbox
    # dbx = dropbox.Dropbox(ACCESS_TOKEN)
    # etc.
    
    # Simulación de subida
    upload_path = f"dropbox://{os.path.basename(source_file)}"
    logger.get_logger().info(f"Archivo subido a: {upload_path}")
    
    print(f"☁️  Simulación: Archivo subido a Dropbox como {upload_path}")
    return upload_path

def fragment_file(source_file, fragment_size_mb=1024, output_dir=None):
    """
    Divide un archivo en fragmentos para almacenamiento en USB
    Utiliza paralelismo para escribir fragmentos
    """
    if not output_dir:
        output_dir = Path(source_file).parent / f"{Path(source_file).stem}_fragments"
    
    os.makedirs(output_dir, exist_ok=True)
    file_size = os.path.getsize(source_file)
    fragment_size = fragment_size_mb * 1024 * 1024  # Convertir a bytes
    num_fragments = (file_size + fragment_size - 1) // fragment_size
    
    logger.get_logger().info(f"Dividiendo archivo en {num_fragments} fragmentos de {fragment_size_mb} MB")
    
    def write_fragment(fragment_info):
        """Escribe un fragmento del archivo"""
        index, start, end = fragment_info
        output_path = os.path.join(output_dir, f"{Path(source_file).stem}.part{index:03d}")
        
        with open(source_file, 'rb') as f_in:
            f_in.seek(start)
            data = f_in.read(end - start)
            
            with open(output_path, 'wb') as f_out:
                f_out.write(data)
        
        return output_path
    
    # Crear información de fragmentos
    fragments = []
    for i in range(num_fragments):
        start = i * fragment_size
        end = min(start + fragment_size, file_size)
        fragments.append((i, start, end))
    
    # Procesar fragmentos en paralelo
    try:
        fragments_bag = db.from_sequence(fragments)
        fragment_paths = fragments_bag.map(write_fragment).compute()
    except:
        # Fallback secuencial
        logger.get_logger().warning("Error con Dask, fragmentando secuencialmente")
        fragment_paths = [write_fragment(frag) for frag in fragments]
    
    # Escribir metadatos para facilitar la restauración
    metadata_path = os.path.join(output_dir, f"{Path(source_file).stem}.metadata")
    with open(metadata_path, 'w') as f:
        f.write(f"original_file: {source_file}\n")
        f.write(f"file_size: {file_size}\n")
        f.write(f"fragment_size: {fragment_size}\n")
        f.write(f"num_fragments: {num_fragments}\n")
        f.write(f"fragments: {','.join([os.path.basename(p) for p in fragment_paths])}\n")
    
    logger.get_logger().info(f"Archivo dividido en {num_fragments} fragmentos en: {output_dir}")
    
    print(f"🧩 Archivo fragmentado exitosamente:")
    print(f"   📁 Directorio: {output_dir}")
    print(f"   📊 {num_fragments} fragmentos de {fragment_size_mb}MB cada uno")
    print(f"   📋 Metadata: {metadata_path}")
    
    return output_dir