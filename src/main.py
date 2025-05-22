#!/usr/bin/env python3
"""
Sistema de Backup Seguro - Interfaz de Línea de Comandos
"""

import argparse
import sys
import os
import getpass
from pathlib import Path

def create_parser():
    """Crea el parser principal con comandos completos"""
    
    parser = argparse.ArgumentParser(
        prog='secure-backup',
        description='Sistema de Backup Seguro con paralelismo usando Dask',
        epilog='Ejemplos:\n'
               '  %(prog)s backup -d ./docs -o backup.zip\n'
               '  %(prog)s backup -d ./docs ./fotos -o backup.zip.enc -e\n'
               '  %(prog)s restore -i backup.zip -o ./restaurado\n',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Opciones globales
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Mostrar información detallada')
    parser.add_argument('--workers', type=int, default=4,
                       help='Número de workers para paralelismo (default: 4)')
    
    # Subcomandos
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # COMANDO BACKUP
    backup_parser = subparsers.add_parser('backup', help='Crear un backup')
    backup_parser.add_argument('-d', '--directories', nargs='+', required=True,
                              help='Directorios a incluir en el backup')
    backup_parser.add_argument('-o', '--output', required=True,
                              help='Archivo de salida')
    backup_parser.add_argument('-a', '--algorithm', choices=['zip', 'gzip', 'bzip2'],
                              default='zip', help='Algoritmo de compresión')
    backup_parser.add_argument('-e', '--encrypt', action='store_true',
                              help='Encriptar el backup')
    backup_parser.add_argument('--password', help='Contraseña para encriptación')
    backup_parser.add_argument('-s', '--storage', choices=['local', 'cloud', 'fragments'],
                              default='local', help='Modo de almacenamiento')
    backup_parser.add_argument('--cloud-service', choices=['gdrive', 'dropbox'],
                              help='Servicio de nube')
    backup_parser.add_argument('--fragment-size', type=int, default=1024,
                              help='Tamaño de fragmentos en MB')
    
    # COMANDO RESTORE
    restore_parser = subparsers.add_parser('restore', help='Restaurar un backup')
    restore_parser.add_argument('-i', '--input', required=True,
                               help='Archivo de backup a restaurar')
    restore_parser.add_argument('-o', '--output-dir', required=True,
                               help='Directorio donde restaurar')
    restore_parser.add_argument('--password', help='Contraseña para desencriptar')
    
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

def create_output_directory(output_path):
    """Crea el directorio de salida si no existe"""
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
            print(f"Directorio creado: {output_dir}")
        except PermissionError:
            print(f"Error: Sin permisos para crear '{output_dir}'")
            return False
    return True

def handle_backup(args):
    """Maneja el comando backup"""
    
    print("Iniciando proceso de backup...")
    
    # Validar directorios
    if not validate_directories(args.directories):
        return False
    
    # Crear directorio de salida
    if not create_output_directory(args.output):
        return False
    
    # Manejar encriptación
    if args.encrypt and not args.password:
        args.password = getpass.getpass("Ingrese contraseña para encriptación: ")
        if not args.password:
            print("Error: Se requiere contraseña para encriptación")
            return False
    
    # Mostrar información
    if args.verbose:
        print(f"Directorios a respaldar: {', '.join(args.directories)}")
        print(f"Archivo de salida: {args.output}")
        print(f"Algoritmo: {args.algorithm}")
        print(f"Encriptación: {'SI' if args.encrypt else 'NO'}")
        print(f"Almacenamiento: {args.storage}")
        print(f"Workers: {args.workers}")
        print()
    
    try:
        # Importar módulos necesarios
        from src.core import scanner, compressor, encryptor, storage, restore
        from src.utils import logger
        
        # Configurar logger
        log_level = 'DEBUG' if args.verbose else 'INFO'
        logger.setup_logger(log_level)
        
        # 1. ESCANEAR ARCHIVOS
        print("Escaneando directorios...")
        files = scanner.scan_directories(args.directories, parallel=True)
        
        if not files:
            print("No se encontraron archivos para respaldar")
            return False
        
        print(f"Encontrados {len(files)} archivos")
        
        # 2. COMPRIMIR
        print(f"Comprimiendo con {args.algorithm}...")
        compressed_file = compressor.compress_files(
            files,
            algorithm=args.algorithm,
            output=args.output,
            encrypt=args.encrypt,
            password=args.password,
            workers=args.workers
        )
        
        if not compressed_file:
            print("Error durante la compresión")
            return False
        
        print(f"Compresión completada: {compressed_file}")
        
        # 3. ENCRIPTAR (si se solicita)
        if args.encrypt:
            print("Encriptando backup...")
            encrypted_file = args.output + ".enc" if not args.output.endswith('.enc') else args.output
            encryptor.encrypt_file(compressed_file, encrypted_file, args.password)
            print(f"Encriptación completada: {encrypted_file}")
            
            # Eliminar archivo sin encriptar
            if compressed_file != encrypted_file:
                os.remove(compressed_file)
                compressed_file = encrypted_file
        
        # 4. ALMACENAR según el modo seleccionado
        if args.storage == 'local':
            # Para almacenamiento local, el archivo ya está en su destino final
            print(f"Archivo almacenado localmente: {compressed_file}")
        elif args.storage == 'cloud':
            print(f"Subiendo a {args.cloud_service}...")
            storage.store_cloud(compressed_file, args.cloud_service)
        elif args.storage == 'fragments':
            print(f"Fragmentando en archivos de {args.fragment_size}MB...")
            storage.fragment_file(compressed_file, args.fragment_size)
        
        # Mostrar estadísticas finales
        final_size = os.path.getsize(compressed_file)
        print(f"\nBACKUP COMPLETADO EXITOSAMENTE")
        print(f"Archivo final: {compressed_file}")
        print(f"Tamaño: {final_size / (1024*1024):.2f} MB")
        
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

def handle_restore(args):
    """Maneja el comando restore"""
    
    print("Iniciando proceso de restauración...")
    
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
            print(f"RESTAURACIÓN COMPLETADA")
            print(f"Archivos restaurados en: {args.output_dir}")
            
            # Mostrar algunos archivos restaurados
            restored_files = []
            for root, dirs, files in os.walk(args.output_dir):
                for file in files[:5]:  # Mostrar solo los primeros 5
                    restored_files.append(os.path.join(root, file))
            
            if restored_files:
                print("Algunos archivos restaurados:")
                for file in restored_files:
                    print(f"   {file}")
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
        print("Sistema de Backup Seguro")
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
        print("=" * 50)
        print("SISTEMA DE BACKUP SEGURO")
        print("   Compresión + Paralelismo con Dask")
        print("=" * 50)
    
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