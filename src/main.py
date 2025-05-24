import argparse
import sys
import os
import getpass
import tempfile
from pathlib import Path
from datetime import datetime

def create_parser():
    """Crea el parser principal con información detallada del sistema"""
    
    # Descripción principal del sistema
    main_description = """
🛡️  SISTEMA DE BACKUP SEGURO 
=====================================

Un sistema completo de respaldo con encriptación AES-256, compresión avanzada 
y múltiples opciones de almacenamiento.
------------------------------------------------------------------------------------------------------------------------
🔥 CARACTERÍSTICAS PRINCIPALES:
   📁 Respaldo de múltiples carpetas simultáneamente
   🔒 Encriptación AES-256 de grado militar  
   📦 Compresión con algoritmos ZIP, GZIP y BZIP2
   ⚡ Procesamiento paralelo con Dask para máximo rendimiento
   💾 Almacenamiento local para discos externos
   🧩 Fragmentación automática para distribución en USBs
   ☁️  Integración con Google Drive y Dropbox
   📋 Generación automática de informes de respaldo
   🔄 Sistema completo de restauración
------------------------------------------------------------------------------------------------------------------------
🎯 CASOS DE USO TÍPICOS:
   • Respaldo completo del sistema antes de actualizaciones críticas
   • Migración segura de datos entre computadoras
   • Archivo a largo plazo de proyectos y documentos importantes
   • Distribución de backups grandes en múltiples dispositivos USB
   • Sincronización automática con servicios en la nube
   • Backup empresarial con fragmentación y encriptación
------------------------------------------------------------------------------------------------------------------------   
   """

    # Ejemplos detallados por categoría
    examples_section = """
📚 EJEMPLOS DE USO COMPLETOS:

-----------------------------------------------------------------------------------------------------------------------
🔹 RESPALDO BÁSICO LOCAL:
   python -m src.main backup -d ./documentos -o ./backupz/backup_docs.zip 

   python -m src.main backup -d ./documentos -o ./backupz/backup_docs (Esto creará una carpeta y dentro estará el .zip)
------------------------------------------------------------------------------------------------------------------------
🔹 RESPALDO CON ENCRIPTACIÓN:
   python -m src.main backup -d ./privado -o backup_seguro.zip.enc -e

   python -m src.main backup -d ./empresa -o datos_empresa.enc -e --password mi_clave_secreta
------------------------------------------------------------------------------------------------------------------------
🔹 FRAGMENTACIÓN PARA USB (Recomendado para backups grandes):
   python -m src.main -d ./sistema -o backup -s fragments --fragment-size 500
   
   python -m src.main -d ./multimedia -o backup -s fragments --fragment-size 1000 -e (Con encriptación)

   cd backups/carpeta_archivos_fragmentados 
   python rebuild.py (para volverlo un .zip)
------------------------------------------------------------------------------------------------------------------------
🔹 ALMACENAMIENTO EN LA NUBE:
   python -m src.main backup -d ./documentos -o backup.zip -s cloud --cloud-service gdrive

   python -m src.main backup -d ./proyectos -o backup.zip -s cloud --cloud-service dropbox --cloud-folder "Backups/2025"
------------------------------------------------------------------------------------------------------------------------
🔹 CONFIGURACIÓN AVANZADA:
   python -m src.main backup -d ./src ./docs ./tests -o proyecto_completo.bz2 -a bzip2 -e --workers 8 -v

   python -m src.main backup -d ./datos -o backup -s fragments --fragment-size 750 -e --workers 6
------------------------------------------------------------------------------------------------------------------------
🔹 RESTAURACIÓN:
   python -m src.main restore -i backup_docs.zip -o ./restaurado

   python -m src.main restore -i backup_seguro.zip.enc -o ./restaurado --password mi_clave_secreta
------------------------------------------------------------------------------------------------------------------------
⚡ OPTIMIZACIÓN DE RENDIMIENTO:

   • Use --workers para ajustar el paralelismo (default: 4, recomendado: 4-8)
   • Para SSD rápidos: hasta 8 workers
   • Para HDD tradicionales: 2-4 workers
   • Para fragmentación: ajuste fragment-size según capacidad de USB
------------------------------------------------------------------------------------------------------------------------
❗ Para más información sobre los comandos de "backup" y "restore" puedes ingresar:

   python -m src.main backup --help

   python -m src.main restore --help
------------------------------------------------------------------------------------------------------------------------
"""

    parser = argparse.ArgumentParser(
        prog='secure-backup',
        description=main_description,
        epilog=examples_section,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False  # Deshabilitamos help por defecto para personalizarlo
    )
    
    # OPCIONES GLOBALES ORGANIZADAS
    global_group = parser.add_argument_group(
        title="🌐 OPCIONES GLOBALES",
        description="Configuraciones que aplican a todos los comandos"
    )
    
    global_group.add_argument('-h', '--help', action='help',
                             help='Mostrar esta ayuda completa y salir')
    global_group.add_argument('-v', '--verbose', action='store_true',
                             help='Activar modo detallado con información de depuración')
    global_group.add_argument('--workers', type=int, default=4, metavar='N',
                             help='Número de procesos paralelos (1-16, default: 4)\n'
                                  'Recomendado: SSD=6-8, HDD=2-4, USB=1-2')
    
    # SUBCOMANDOS
    subparsers = parser.add_subparsers(
        dest='command',
        title="🎯 COMANDOS DISPONIBLES",
        description="Selecciona la operación que deseas realizar",
        help="Usa 'comando --help' para ayuda específica"
    )
    
    # ==================== COMANDO BACKUP ====================
    backup_parser = subparsers.add_parser(
        'backup',
        help='Crear un respaldo completo y seguro',
        description="""
🔐 COMANDO BACKUP - Creación de Respaldos Seguros
================================================

Crea respaldos completos con encriptación, compresión y múltiples opciones
de almacenamiento. Ideal para proteger datos importantes y facilitar
migraciones de sistema.
""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Argumentos requeridos para backup
    required_backup = backup_parser.add_argument_group(
        title="📁 DIRECTORIOS Y SALIDA (Requeridos)",
        description="Especifica qué respaldar y dónde guardarlo"
    )
    
    required_backup.add_argument('-d', '--directories', nargs='+', required=True,
                                metavar='DIR',
                                help='Uno o más directorios para respaldar\n'
                                     'Ejemplos: -d ./docs\n'
                                     '          -d ./fotos ./videos ./documentos\n'
                                     '          -d /home/usuario/proyectos')
    
    required_backup.add_argument('-o', '--output', required=True, metavar='ARCHIVO',
                                help='Archivo o directorio de salida\n'
                                     'Para local: backup.zip, datos.tar.gz\n'
                                     'Para fragmentos: directorio_base\n'
                                     'Para encriptación: archivo.enc')
    
    # Opciones de compresión
    compression_group = backup_parser.add_argument_group(
        title="📦 COMPRESIÓN",
        description="Algoritmos de compresión disponibles"
    )
    
    compression_group.add_argument('-a', '--algorithm', 
                                  choices=['zip', 'gzip', 'bzip2'],
                                  default='zip', metavar='ALG',
                                  help='Algoritmo de compresión:\n'
                                       '• zip    - Rápido, compatible (default)\n'
                                       '• gzip   - Buena compresión, estándar\n'
                                       '• bzip2  - Máxima compresión, más lento')
    
    # Opciones de seguridad
    security_group = backup_parser.add_argument_group(
        title="🔒 SEGURIDAD Y ENCRIPTACIÓN",
        description="Protección avanzada de datos"
    )
    
    security_group.add_argument('-e', '--encrypt', action='store_true',
                               help='Activar encriptación AES-256\n'
                                    'Protege tu backup con contraseña segura\n'
                                    'Se solicitará contraseña interactivamente')
    
    security_group.add_argument('--password', metavar='PASS',
                               help='Contraseña para encriptación (no recomendado)\n'
                                    'Mejor práctica: omitir para ingreso interactivo\n'
                                    'Mínimo 8 caracteres requeridos')
    
    # Opciones de almacenamiento
    storage_group = backup_parser.add_argument_group(
        title="💾 MODOS DE ALMACENAMIENTO",
        description="Diferentes estrategias para guardar tu backup"
    )
    
    storage_group.add_argument('-s', '--storage', 
                              choices=['local', 'cloud', 'fragments'],
                              default='local', metavar='MODO',
                              help='Modo de almacenamiento:\n'
                                   '• local     - Archivo único (default)\n'
                                   '• cloud     - Subir a Google Drive/Dropbox\n'
                                   '• fragments - Dividir en partes para USB')
    
    # Opciones específicas para la nube
    cloud_group = backup_parser.add_argument_group(
        title="☁️  CONFIGURACIÓN DE NUBE",
        description="Opciones para almacenamiento en servicios cloud"
    )
    
    cloud_group.add_argument('--cloud-service', 
                            choices=['gdrive', 'dropbox'], metavar='SERVICIO',
                            help='Servicio de nube (REQUERIDO con -s cloud):\n'
                                 '• gdrive  - Google Drive\n'
                                 '• dropbox - Dropbox')
    
    cloud_group.add_argument('--cloud-folder', metavar='CARPETA',
                            help='Carpeta destino en la nube\n'
                                 'Ejemplos: "Backups", "Backups/2025"\n'
                                 'Si no existe, se creará automáticamente')
    
    # Opciones de fragmentación
    fragment_group = backup_parser.add_argument_group(
        title="🧩 CONFIGURACIÓN DE FRAGMENTOS",
        description="División de backups para distribución en múltiples dispositivos"
    )
    
    fragment_group.add_argument('--fragment-size', type=int, default=1024, 
                               metavar='MB',
                               help='Tamaño de cada fragmento en MB (default: 1024)\n'
                                    'Tamaños recomendados:\n'
                                    '• USB 1GB  : 900 MB\n'
                                    '• USB 2GB  : 1900 MB\n'
                                    '• USB 4GB  : 3800 MB\n'
                                    '• USB 8GB  : 7500 MB')
    
    # ==================== COMANDO RESTORE ====================
    restore_parser = subparsers.add_parser(
        'restore',
        help='Restaurar un backup existente',
        description="""
🔄 COMANDO RESTORE - Restauración de Respaldos
==============================================

Restaura backups creados con este sistema, incluyendo archivos encriptados
y fragmentados. Mantiene la estructura original de directorios y archivos.
""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Argumentos requeridos para restore
    required_restore = restore_parser.add_argument_group(
        title="📂 ARCHIVOS Y DESTINO (Requeridos)",
        description="Especifica qué restaurar y dónde"
    )
    
    required_restore.add_argument('-i', '--input', required=True, metavar='ARCHIVO',
                                 help='Archivo de backup a restaurar\n'
                                      'Soporta: .zip, .tar.gz, .bz2, .enc\n'
                                      'Para fragmentos: usar rebuild.py primero')
    
    required_restore.add_argument('-o', '--output-dir', required=True, metavar='DIR',
                                 help='Directorio donde restaurar los archivos\n'
                                      'Se creará si no existe\n'
                                      'Estructura original se preservará')
    
    # Opciones de seguridad para restore
    restore_security = restore_parser.add_argument_group(
        title="🔓 DESENCRIPTACIÓN",
        description="Opciones para archivos encriptados"
    )
    
    restore_security.add_argument('--password', metavar='PASS',
                                 help='Contraseña para desencriptar\n'
                                      'Requerido para archivos .enc\n'
                                      'Se solicitará interactivamente si no se proporciona')
    
    return parser

def validate_directories(directories):
    """Valida que los directorios existan"""
    for directory in directories:
        if not os.path.exists(directory):
            print(f"Error: El directorio '{directory}' no existe")
            return False
        if not os.path.isdir(directory):
            print(f"Error: '{directory}' no es un directorio")
            return False
    return True

def validate_storage_options(args):
    """Valida las opciones de almacenamiento"""
    if args.storage == 'cloud':
        if not args.cloud_service:
            print("Error: --cloud-service es requerido cuando se usa -s cloud")
            print("Servicios disponibles: gdrive, dropbox")
            return False
    
    if args.fragment_size <= 0:
        print("Error: --fragment-size debe ser mayor a 0")
        return False
    
    return True

def create_organized_backup_folder(base_output, directories, storage_mode, algorithm, encrypt):
    """
    Crea una carpeta organizada para el backup con numeración incremental
    """
    # Construir nombre base según el modo de almacenamiento
    if storage_mode == 'fragments':
        base_name = "backup_fragments"
    elif storage_mode == 'cloud':
        base_name = "backup_cloud"
    else:
        base_name = "backup_local"
    
    # Añadir sufijo de encriptación si está activada
    if encrypt:
        base_name += "_encrypted"
    
    # Buscar el siguiente número disponible
    base_dir = Path(base_output).parent
    counter = 1
    
    while True:
        folder_name = f"{base_name}_{counter}"
        backup_folder = base_dir / folder_name
        
        if not backup_folder.exists():
            break
        counter += 1
        
        # Evitar bucle infinito (máximo 9999 backups)
        if counter > 9999:
            raise ValueError("Demasiados backups existentes. Limpia directorios antiguos.")
    
    # Crear la carpeta
    os.makedirs(backup_folder, exist_ok=True)
    
    return backup_folder, folder_name

def create_backup_info_file(backup_folder, directories, algorithm, storage_mode, encrypt, fragment_size=None):
    """
    Crea un archivo con información detallada del backup
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    info_content = f"""# Información del Backup - Sistema de Backup Seguro

## Detalles del Backup
- **Fecha y hora:** {timestamp}
- **Directorios respaldados:** {len(directories)}
- **Algoritmo de compresión:** {algorithm.upper()}
- **Modo de almacenamiento:** {storage_mode}
- **Encriptación:** {'AES-256' if encrypt else 'No'}

## Directorios Incluidos
"""
    
    for i, directory in enumerate(directories, 1):
        abs_dir = os.path.abspath(directory)
        try:
            # Contar archivos en el directorio
            file_count = sum(len(files) for _, _, files in os.walk(directory))
            dir_size = sum(os.path.getsize(os.path.join(root, file)) 
                          for root, _, files in os.walk(directory) 
                          for file in files)
            size_mb = dir_size / (1024 * 1024)
            
            info_content += f"{i}. **{directory}**\n"
            info_content += f"   - Ruta completa: `{abs_dir}`\n"
            info_content += f"   - Archivos: {file_count}\n"
            info_content += f"   - Tamaño: {size_mb:.2f} MB\n\n"
        except:
            info_content += f"{i}. **{directory}**\n"
            info_content += f"   - Ruta completa: `{abs_dir}`\n"
            info_content += f"   - Error calculando estadísticas\n\n"
    
    if storage_mode == 'fragments':
        info_content += f"""## Configuración de Fragmentación
- **Tamaño por fragmento:** {fragment_size} MB
- **Uso recomendado:** Copiar cada fragmento a un USB diferente
- **Para reconstruir:** Ejecutar `rebuild.py` en este directorio

"""
    
    info_content += """## Comandos de Restauración

### Para archivos locales:
```bash
python -m src.main restore -i ARCHIVO_BACKUP -o ./restaurado
```

### Para archivos encriptados:
```bash
python -m src.main restore -i ARCHIVO_BACKUP.enc -o ./restaurado --password TU_PASSWORD
```

### Para fragmentos:
```bash
# Ir al directorio de fragmentos y ejecutar:
python rebuild.py
```

## Notas
- Este backup fue creado con el Sistema de Backup Seguro v1.0
- Guarda este archivo junto con tu backup para referencia futura
- Para fragmentos: todos los archivos .part### son necesarios para la reconstrucción
"""
    
    info_file = backup_folder / "BACKUP_INFO.md"
    with open(info_file, 'w', encoding='utf-8') as f:
        f.write(info_content)
    
    return info_file

def create_output_directory(output_path, storage_mode):
    """Crea el directorio de salida si no existe"""
    if storage_mode == 'fragments':
        # Para fragmentos, el output es un directorio base
        output_dir = os.path.dirname(output_path) if os.path.dirname(output_path) else '.'
    else:
        # Para archivos normales
        output_dir = os.path.dirname(output_path)
    
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
            print(f"Directorio creado: {output_dir}")
        except PermissionError:
            print(f"Error: Sin permisos para crear '{output_dir}'")
            return False
    return True

def validate_and_get_password(encrypt, current_password=None):
    """Valida y obtiene la contraseña para encriptación con confirmación"""
    if not encrypt:
        return None
    
    if current_password:
        # Validar longitud mínima
        if len(current_password) < 8:
            print("Error: La contraseña debe tener al menos 8 caracteres.")
            return None
        return current_password
    
    # Solicitar contraseña con confirmación
    while True:
        password1 = getpass.getpass("Ingrese contraseña para encriptación (mín. 8 caracteres): ")
        
        if len(password1) < 8:
            print("Error: La contraseña debe tener al menos 8 caracteres. Intente nuevamente.")
            continue
        
        password2 = getpass.getpass("Confirme la contraseña: ")
        
        if password1 == password2:
            return password1
        else:
            print("Error: Las contraseñas no coinciden. Intente nuevamente.")

def show_storage_info(args, backup_folder=None):
    """Muestra información sobre el modo de almacenamiento seleccionado"""
    if args.storage == 'local':
        print("💾 Modo: Almacenamiento Local/Disco Externo")
        print(f"   Destino: {args.output}")
        
    elif args.storage == 'fragments':
        print("🧩 Modo: Fragmentación para USB")
        if backup_folder:
            print(f"   📁 Carpeta de backup: {backup_folder}")
        print(f"   🧩 Tamaño por fragmento: {args.fragment_size} MB")
        
    elif args.storage == 'cloud':
        print(f"☁️  Modo: Almacenamiento en {args.cloud_service.upper()}")
        if args.cloud_folder:
            print(f"   Carpeta: {args.cloud_folder}")

def handle_backup(args):
    """Maneja el comando backup con carpetas organizadas"""
    
    print("\033[1mIniciando proceso de backup...\033[0m")
    print("----------------------------------------------------------------------------------------")
    
    # Validar directorios
    if not validate_directories(args.directories):
        return False
    
    # Validar opciones de almacenamiento
    if not validate_storage_options(args):
        return False
    
    # Crear directorio de salida base
    if not create_output_directory(args.output, args.storage):
        return False
    
    # Manejar encriptación
    if args.encrypt:
        args.password = validate_and_get_password(args.encrypt, args.password)
        if not args.password:
            print("Error: Se requiere una contraseña válida para encriptación")
            return False
    
    # NUEVO: Crear carpeta organizada para fragmentos
    if args.storage == 'fragments':
        backup_folder, folder_name = create_organized_backup_folder(
            args.output, args.directories, args.storage, args.algorithm, args.encrypt
        )
        print(f"📁 Carpeta de backup creada: {backup_folder}")
        
        # Crear archivo de información
        info_file = create_backup_info_file(
            backup_folder, args.directories, args.algorithm, 
            args.storage, args.encrypt, args.fragment_size
        )
        print(f"📋 Información del backup: {info_file}")
        print("----------------------------------------------------------------------------------------")
        
        # Ajustar la salida para usar la nueva carpeta
        actual_output = backup_folder / "backup"
    else:
        actual_output = args.output
        backup_folder = None
    
    # Mostrar información
    
    print(f"Directorios a respaldar: {', '.join(args.directories)}")
    print("")
    print(f"Algoritmo: {args.algorithm}")
    print(f"Encriptación: {'SI (AES-256)' if args.encrypt else 'NO'}")
    print(f"Workers: {args.workers}")
    print("")
    show_storage_info(args, backup_folder)
    print("----------------------------------------------------------------------------------------")
    
    try:
        # Importar módulos necesarios
        from src.core import scanner, compressor, storage
        from src.utils import logger
        
        # Configurar logger
        log_level = 'DEBUG' if args.verbose else 'INFO'
        logger.setup_logger(log_level)
        
        # 1. ESCANEAR ARCHIVOS
        print("Escaneando directorios...")
        print("")
        files = scanner.scan_directories(args.directories, parallel=True)
        
        if not files:
            print("No se encontraron archivos para respaldar")
            return False
        
        print("")
        print(f"🔍 Encontrados {len(files)} archivos en {len(args.directories)} carpeta(s)")
        print("----------------------------------------------------------------------------------------")
        if args.verbose:
            print("Directorios escaneados:")
            for directory in args.directories:
                dir_files = [f for f in files if f.startswith(os.path.abspath(directory))]
                print(f"  {directory}: {len(dir_files)} archivos")
        
        # 2. DETERMINAR ARCHIVO TEMPORAL PARA COMPRESIÓN
        if args.storage == 'local':
            # Para almacenamiento local, usar archivo temporal primero
            temp_dir = tempfile.mkdtemp(prefix="backup_temp_")
            temp_output = os.path.join(temp_dir, f"backup_temp.{args.algorithm}")
        else:
            # Para otros modos, usar el output ajustado
            temp_output = actual_output
        
        # 3. COMPRIMIR
        print(f"📩 Comprimiendo con {args.algorithm}...")
        print("")
        
        if args.encrypt:
            print("La encriptación AES-256 se aplicará automáticamente...")
        
        compressed_file = compressor.compress_files(
            files,
            algorithm=args.algorithm,
            output=temp_output,
            encrypt=args.encrypt,
            password=args.password,
            workers=args.workers
        )
        
        if not compressed_file:
            print("Error durante la compresión")
            return False
        
        print("")
        print(f"Compresión completada: {compressed_file}")
        print("----------------------------------------------------------------------------------------")
        
        # 4. ALMACENAR según el modo
        final_result = None
        print("💽 Iniciando almacenamiento...")
        print("")
        
        if args.storage == 'local':
            # Para local, mover desde temporal al destino final
            final_output_path = Path(args.output).resolve()
            compressed_path = Path(compressed_file).resolve()
            
            if compressed_path != final_output_path:
                final_result = storage.store_local(compressed_file, args.output)
                # Limpiar archivo temporal
                try:
                    import shutil
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except:
                    pass
            else:
                final_result = str(final_output_path)
            
            print("")
            print(f"✅ Archivo almacenado localmente: {final_result}")
            print("----------------------------------------------------------------------------------------")
            
        elif args.storage == 'cloud':
            print(f"Subiendo a {args.cloud_service}...")
            
            credentials = {}
            if hasattr(args, 'cloud_credentials'):
                credentials = args.cloud_credentials
            
            final_result = storage.store_cloud(
                compressed_file, 
                args.cloud_service,
                credentials=credentials,
                folder_name=args.cloud_folder
            )
            print("----------------------------------------------------------------------------------------")
            print(f"✅ Archivo subido a la nube: {final_result}")
            
        elif args.storage == 'fragments':
            print(f"Fragmentando en archivos de {args.fragment_size}MB...")
            
            # CAMBIO CLAVE: Fragmentar dentro de la carpeta organizada
            fragments_dir = backup_folder / "fragments"
            final_result = storage.fragment_file(
                compressed_file, 
                args.fragment_size,
                str(fragments_dir)
            )
            print("----------------------------------------------------------------------------------------")
            print(f"✅ Archivo fragmentado: {final_result}")
        
        # Mostrar estadísticas finales - SECCIÓN CORREGIDA
        final_size = 0
        
        if args.storage == 'local':
            try:
                # Para almacenamiento local, usar el tamaño del archivo final
                final_size = os.path.getsize(final_result)
                if args.verbose:
                    print(f"   🔍 Debug local: Archivo {final_result}, Tamaño: {final_size} bytes")
            except Exception as e:
                if args.verbose:
                    print(f"   ⚠️  Error obteniendo tamaño local: {e}")
                # Fallback: usar archivo comprimido
                try:
                    final_size = os.path.getsize(compressed_file)
                    if args.verbose:
                        print(f"   🔍 Fallback: Usando archivo comprimido: {final_size} bytes")
                except:
                    final_size = 0
        
        elif args.storage == 'cloud':
            try:
                # Para nube, usar el tamaño del archivo comprimido antes de subir
                final_size = os.path.getsize(compressed_file)
                if args.verbose:
                    print(f"   🔍 Debug nube: Archivo comprimido {compressed_file}, Tamaño: {final_size} bytes")
            except Exception as e:
                if args.verbose:
                    print(f"   ⚠️  Error obteniendo tamaño de nube: {e}")
                final_size = 0
        
        elif args.storage == 'fragments':
            try:
                # Para fragmentos, calcular tamaño total de todos los fragmentos
                fragments_path = Path(final_result)
                
                # Buscar archivos .part* en el directorio de fragmentos
                fragment_files = list(fragments_path.glob('*.part*'))
                
                if fragment_files:
                    final_size = sum(f.stat().st_size for f in fragment_files)
                    if args.verbose:
                        print(f"   🔍 Debug fragmentos:")
                        print(f"      Directorio: {fragments_path}")
                        print(f"      Fragmentos encontrados: {len(fragment_files)}")
                        for frag in fragment_files:
                            size_mb = frag.stat().st_size / (1024*1024)
                            print(f"         {frag.name}: {size_mb:.2f} MB")
                        print(f"      Tamaño total: {final_size} bytes")
                else:
                    # Si no hay fragmentos, usar el archivo comprimido original
                    final_size = os.path.getsize(compressed_file)
                    if args.verbose:
                        print(f"   ⚠️  No se encontraron fragmentos, usando archivo comprimido: {final_size} bytes")
                
            except Exception as e:
                if args.verbose:
                    print(f"   ⚠️  Error calculando tamaño de fragmentos: {e}")
                    print(f"      final_result: {final_result}")
                    print(f"      compressed_file: {compressed_file}")
                try:
                    # Fallback: usar tamaño del archivo comprimido
                    final_size = os.path.getsize(compressed_file)
                    if args.verbose:
                        print(f"   🔍 Fallback fragmentos: {final_size} bytes")
                except Exception as e2:
                    if args.verbose:
                        print(f"   ❌ Fallback también falló: {e2}")
                    final_size = 0
        
        print(f"\n\033[1m🎉 BACKUP COMPLETADO EXITOSAMENTE\033[0m")
        print("")

        print(f"📁 Carpetas respaldadas: {len(args.directories)}")
        print(f"📄 Archivos procesados: {len(files)}")
        
        if args.storage == 'local':
            print(f"📦 Archivo final: {final_result}")
        elif args.storage == 'cloud':
            print(f"☁️  Almacenado en: {final_result}")
        elif args.storage == 'fragments':
            print(f"📁 Carpeta de backup: {backup_folder}")
            print(f"🧩 Fragmentos en: {final_result}")
        
        # MOSTRAR TAMAÑO SIEMPRE (no solo si > 0)
        # MOSTRAR TAMAÑO CON UNIDADES APROPIADAS
        if final_size >= 1024 * 1024:  # >= 1 MB
           print(f"💾 Tamaño: {final_size / (1024*1024):.2f} MB")
        elif final_size >= 1024:  # >= 1 KB
           print(f"💾 Tamaño: {final_size / 1024:.2f} KB")
        else:  # < 1 KB
           print(f"💾 Tamaño: {final_size} bytes")
        
        if args.encrypt:
            print(f"🔒 Encriptación: AES-256 aplicada")
        
        # Mostrar instrucciones específicas
        show_next_steps(args, final_result, backup_folder)
        
        return True
        
    except ImportError as e:
        print(f"Error: Módulo no implementado - {e}")
        print("Implementa los módulos faltantes en src/core/")
        return False
    except Exception as e:
        if args.verbose:
            import traceback
            traceback.print_exc()
        else:
            print(f"Error durante el backup: {e}")
        return False

def show_next_steps(args, result, backup_folder=None):
    """Muestra instrucciones específicas según el tipo de almacenamiento"""
    print(f"\n💡 Próximos pasos:")
    
    if args.storage == 'local':
        print("   • El archivo está listo para usar")
        print("   • Puedes copiarlo a tu disco externo si es necesario")
        print(f"   • Para restaurar: python -m src.main restore -i \"{result}\" -o ./restaurado")
        
    elif args.storage == 'cloud':
        print("   • El archivo está disponible en tu nube")
        print("   • Puedes acceder desde cualquier dispositivo")
        print("   • Para restaurar, primero descarga el archivo")
        
    elif args.storage == 'fragments':
        print(f"   • Revisa la carpeta: {backup_folder}")
        print("   • Los fragmentos están listos para copiar a USBs")
        print("   • Cada fragmento puede ir en un USB diferente")
        print(f"   • Para reconstruir: ve a {result} y ejecuta rebuild.py")
        print("   • Lee BACKUP_INFO.md para instrucciones completas")

def handle_restore(args):
    """Maneja el comando restore"""
    
    print("🔃 Iniciando proceso de restauración...")
    print("----------------------------------------------------------------------------------------")
    
    # Validar archivo de entrada
    if not os.path.exists(args.input):
        print(f"Error: El archivo '{args.input}' no existe")
        return False
    
    # Crear directorio de salida
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir, exist_ok=True)
        print(f"Directorio creado: {args.output_dir}")
    
    # Mostrar información
    if args.verbose:
        print(f"Archivo de entrada: {args.input}")
        print(f"Directorio de salida: {args.output_dir}")
        print(f"Con contraseña: {'SI' if args.password else 'NO'}")
        print()
    
    try:
        from src.core import restore
        from src.utils import logger
        
        # Configurar logger
        log_level = 'DEBUG' if args.verbose else 'INFO'
        logger.setup_logger(log_level)
        print("")
        print("Restaurando backup...")
        
        # Solicitar contraseña si el archivo parece encriptado
        if args.input.endswith('.enc') and not args.password:
            args.password = getpass.getpass("Ingrese contraseña para desencriptar: ")
        
        # Ejecutar proceso de restauración
        if args.password:
            result = restore.restore_backup(args.input, args.output_dir, password=args.password)
        else:
            result = restore.restore_backup(args.input, args.output_dir)
        
        if result:
            print("----------------------------------------------------------------------------------------")
            print(f"🎉 RESTAURACIÓN COMPLETADA")
            print("")
            print(f"📂 Archivos restaurados en: {args.output_dir}")
            
            # Mostrar algunos archivos restaurados
            restored_files = []
            for root, dirs, files in os.walk(args.output_dir):
                for file in files[:5]:  # Mostrar solo los primeros 5
                    restored_files.append(os.path.join(root, file))
            
            if restored_files:
                print("Algunos archivos restaurados:")
                for file in restored_files:
                    print(f"   📄 {file}")
                if len(restored_files) == 5:
                    print("   ...")
        else:
            print("Error durante la restauración")
            return False
        
        return True
        
    except ImportError as e:
        print(f"Error: Módulo no implementado - {e}")
        print("Implementa el módulo restore en src/core/")
        return False
    except Exception as e:
        if args.verbose:
            import traceback
            traceback.print_exc()
        else:
            print(f"Error durante la restauración: {e}")
        return False

def main():
    """Función principal del programa"""
    
    parser = create_parser()
    
    # Si no hay argumentos, mostrar ayuda
    if len(sys.argv) == 1:
        print("🛡️  Sistema de Backup Seguro")
        print("=" * 40)
        parser.print_help()
        return
    
    # Parsear argumentos
    args = parser.parse_args()
    
    # Si no hay comando, mostrar ayuda
    if not args.command:
        parser.print_help()
        return
    
    # Mostrar banner si es verboso
    if args.verbose:
        print("=" * 60)
        print("🛡️  SISTEMA DE BACKUP SEGURO")
        print("   📁 Múltiples Carpetas + 🔒 Encriptación AES-256")
        print("   ⚡ Compresión + Paralelismo con Dask")
        print("   💾 Local + 🧩 Fragmentos + ☁️  Nube")
        print("=" * 60)
    
    # Ejecutar comando correspondiente
    try:
        if args.command == 'backup':
            success = handle_backup(args)
        elif args.command == 'restore':
            success = handle_restore(args)
        else:
            print(f"Comando no válido: {args.command}")
            print("Use -h para ver opciones.")
            success = False
        
        # Código de salida
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario")
        sys.exit(1)

if __name__ == "__main__":
    main()