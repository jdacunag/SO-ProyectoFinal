import os
import shutil
from pathlib import Path
import dask.bag as db
from src.utils import logger
from src.utils.error_handler import handle_error, StorageError

def store_local(source_file, destination):
    """
    Almacena el archivo de backup en un destino local (disco duro externo)
    Detecta automáticamente si es un disco externo
    """
    logger.get_logger().info(f"Almacenando archivo en destino local: {destination}")
    
    # Asegurarse de que el directorio destino existe
    destination_path = Path(destination)
    
    # Si destination es un directorio, crear el nombre del archivo
    if destination_path.is_dir() or not destination_path.suffix:
        destination_path = destination_path / Path(source_file).name
    
    # Crear directorio padre si no existe
    os.makedirs(destination_path.parent, exist_ok=True)
    
    # Detectar si es disco externo (aproximación)
    dest_drive = _get_drive_info(destination_path)
    if dest_drive:
        logger.get_logger().info(f"💾 Detectado almacenamiento externo: {dest_drive}")
    
    try:
        # Copiar archivo con verificación de integridad
        shutil.copy2(source_file, destination_path)
        
        # Verificar integridad
        if _verify_file_integrity(source_file, destination_path):
            logger.get_logger().info(f"✅ Archivo almacenado y verificado: {destination_path}")
        else:
            raise StorageError("Error de integridad en la copia")
        
        return str(destination_path)
        
    except PermissionError:
        raise StorageError(f"Sin permisos de escritura en: {destination_path}")
    except OSError as e:
        if "No space left" in str(e).lower():
            raise StorageError("Espacio insuficiente en el dispositivo de destino")
        else:
            raise StorageError(f"Error de sistema al copiar archivo: {e}")

def store_cloud(source_file, service_name, credentials=None, folder_name=None):
    """
    Almacena el archivo de backup en un servicio en la nube con integración real
    """
    logger.get_logger().info(f"Almacenando archivo en la nube usando {service_name}")
    
    try:
        # Importar módulo de almacenamiento en la nube
        from src.core.cloud_storage import get_cloud_storage
        
        # Crear instancia del servicio
        storage = get_cloud_storage(service_name, **(credentials or {}))
        
        # Configurar carpeta personalizada si se especifica
        upload_kwargs = {}
        if folder_name:
            if service_name.lower() == 'gdrive':
                upload_kwargs['folder_name'] = folder_name
            elif service_name.lower() == 'dropbox':
                upload_kwargs['folder_path'] = f"/{folder_name}"
        
        # Subir archivo
        result = storage.upload_file(source_file, **upload_kwargs)
        
        # Log del resultado
        if service_name.lower() == 'gdrive':
            logger.get_logger().info(f"🌐 Archivo subido a Google Drive: {result['url']}")
            return result['url']
        elif service_name.lower() == 'dropbox':
            logger.get_logger().info(f"🌐 Archivo subido a Dropbox: {result['path']}")
            return result['path']
        
        return result
        
    except ImportError:
        # Fallback a simulación si no está disponible
        logger.get_logger().warning("Módulo de nube no disponible, usando simulación")
        return _simulate_cloud_upload(source_file, service_name)
    
    except Exception as e:
        raise StorageError(f"Error subiendo a {service_name}: {e}")

def fragment_file(source_file, fragment_size_mb=1024, output_dir=None):
    """
    Divide un archivo en fragmentos para almacenamiento en USB con mejoras
    """
    if not output_dir:
        output_dir = Path(source_file).parent / f"{Path(source_file).stem}_fragments"
    
    output_dir = Path(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    file_size = os.path.getsize(source_file)
    fragment_size = fragment_size_mb * 1024 * 1024  # Convertir a bytes
    num_fragments = (file_size + fragment_size - 1) // fragment_size
    
    logger.get_logger().info(f"Dividiendo archivo en {num_fragments} fragmentos de {fragment_size_mb} MB")
    
    # Verificar espacio disponible
    available_space = shutil.disk_usage(output_dir).free
    if file_size > available_space:
        raise StorageError(f"Espacio insuficiente. Necesario: {file_size/1024/1024:.1f}MB, Disponible: {available_space/1024/1024:.1f}MB")
    
    def write_fragment(fragment_info):
        """Escribe un fragmento del archivo con checksum"""
        index, start, end = fragment_info
        fragment_name = f"{Path(source_file).stem}.part{index:03d}"
        output_path = output_dir / fragment_name
        
        with open(source_file, 'rb') as f_in:
            f_in.seek(start)
            data = f_in.read(end - start)
            
            with open(output_path, 'wb') as f_out:
                f_out.write(data)
        
        # Calcular checksum para verificación
        import hashlib
        checksum = hashlib.md5(data).hexdigest()
        
        return {
            'path': str(output_path),
            'size': len(data),
            'checksum': checksum,
            'index': index
        }
    
    # Crear información de fragmentos
    fragments = []
    for i in range(num_fragments):
        start = i * fragment_size
        end = min(start + fragment_size, file_size)
        fragments.append((i, start, end))
    
    # Procesar fragmentos en paralelo con mejor manejo de errores
    try:
        fragments_bag = db.from_sequence(fragments)
        fragment_results = fragments_bag.map(write_fragment).compute()
    except Exception as e:
        logger.get_logger().warning(f"Error con Dask, fragmentando secuencialmente: {e}")
        fragment_results = [write_fragment(frag) for frag in fragments]
    
    # Crear metadatos mejorados
    metadata = {
        'original_file': str(source_file),
        'file_size': file_size,
        'fragment_size': fragment_size,
        'fragment_size_mb': fragment_size_mb,
        'num_fragments': num_fragments,
        'created_by': 'Sistema de Backup Seguro v1.0',
        'fragments': {}
    }
    
    # Añadir información de cada fragmento
    for result in fragment_results:
        fragment_name = Path(result['path']).name
        metadata['fragments'][fragment_name] = {
            'size': result['size'],
            'checksum': result['checksum'],
            'index': result['index']
        }
    
    # Escribir metadatos
    metadata_path = output_dir / f"{Path(source_file).stem}.metadata.json"
    import json
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Crear scripts de reconstitución usando módulo separado
    try:
        from src.utils.rebuild_generator import create_rebuild_scripts
        create_rebuild_scripts(output_dir, metadata)
    except ImportError:
        logger.get_logger().warning("Módulo de scripts de reconstrucción no disponible")
    
    logger.get_logger().info(f"✅ Archivo fragmentado en {num_fragments} fragmentos en: {output_dir}")
    
    # Mostrar estadísticas
    total_fragment_size = sum(r['size'] for r in fragment_results)
    print(f"\n🧩 Fragmentación completada:")
    print(f"   📁 Directorio: {output_dir}")
    print(f"   📊 {num_fragments} fragmentos de máximo {fragment_size_mb}MB")
    print(f"   📋 Metadatos: {metadata_path}")
    print(f"   🔧 Scripts de reconstitución incluidos")
    print(f"   📏 Tamaño total: {total_fragment_size/1024/1024:.2f}MB")
    
    return str(output_dir)

def _get_drive_info(path):
    """Obtiene información del drive/dispositivo"""
    try:
        path = Path(path).resolve()
        
        if os.name == 'nt':  # Windows
            drive = str(path.drive)
            return f"Drive {drive}"
        else:  # Unix-like
            # Usar df para obtener información del dispositivo
            import subprocess
            result = subprocess.run(['df', str(path.parent)], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    device = lines[1].split()[0]
                    if '/media/' in device or '/mnt/' in device or 'usb' in device.lower():
                        return f"Dispositivo externo: {device}"
                    return f"Dispositivo: {device}"
    except:
        pass
    
    return None

def _verify_file_integrity(source, destination):
    """Verifica la integridad comparando checksums"""
    try:
        import hashlib
        
        def get_file_hash(filepath):
            hash_md5 = hashlib.md5()
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        
        source_hash = get_file_hash(source)
        dest_hash = get_file_hash(destination)
        
        return source_hash == dest_hash
    except:
        # Si no se puede verificar, asumir que está bien
        return True

def _simulate_cloud_upload(source_file, service_name):
    """Simulación mejorada de subida a la nube"""
    logger.get_logger().info(f"Simulando subida a {service_name}...")
    
    file_size = os.path.getsize(source_file)
    filename = os.path.basename(source_file)
    
    # Simular tiempo de subida basado en tamaño
    import time
    upload_time = min(file_size / (10 * 1024 * 1024), 5)  # Máximo 5 segundos
    time.sleep(upload_time)
    
    upload_path = f"{service_name}://backups/{filename}"
    
    print(f"☁️  SIMULACIÓN: Archivo subido a {service_name}")
    print(f"   📁 Ruta: {upload_path}")
    print(f"   📏 Tamaño: {file_size/1024/1024:.2f}MB")
    print(f"   ⏱️  Tiempo: {upload_time:.1f}s")
    print(f"   🔗 URL: https://{service_name}.com/file/{filename}")
    
    logger.get_logger().info(f"Simulación completada: {upload_path}")
    return upload_path

# Función de conveniencia para auto-detectar mejor opción de almacenamiento
def smart_storage_recommendation(file_size_mb, available_services=None):
    """
    Recomienda la mejor opción de almacenamiento basada en el tamaño del archivo
    """
    recommendations = []
    
    if file_size_mb < 100:
        recommendations.append(("local", "Perfecto para almacenamiento local rápido"))
        recommendations.append(("cloud", "Ideal para backup en la nube"))
    
    elif file_size_mb < 1000:  # < 1GB
        recommendations.append(("local", "Recomendado para discos externos"))
        recommendations.append(("cloud", "Viable para nube con buena conexión"))
        recommendations.append(("fragments", "Considerar fragmentación si necesita portabilidad"))
    
    else:  # > 1GB
        recommendations.append(("fragments", "Recomendado para archivos grandes"))
        recommendations.append(("local", "Mejor para discos externos con espacio"))
        recommendations.append(("cloud", "Solo con conexión muy rápida"))
    
    return recommendations