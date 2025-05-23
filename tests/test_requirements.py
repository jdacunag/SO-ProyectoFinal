#!/usr/bin/env python3
"""
Script de prueba para validar los requisitos del proyecto:
1. Selección de múltiples carpetas
2. Encriptación opcional con AES-256
"""

import os
import sys
import shutil
import tempfile
import subprocess
from pathlib import Path

def create_test_structure():
    """Crea estructura de carpetas y archivos de prueba"""
    base_dir = tempfile.mkdtemp(prefix="backup_test_")
    
    # Carpeta 1: Documentos
    docs_dir = os.path.join(base_dir, "documentos")
    os.makedirs(docs_dir)
    
    with open(os.path.join(docs_dir, "reporte.txt"), "w") as f:
        f.write("Este es un reporte importante\n" * 100)
    
    with open(os.path.join(docs_dir, "config.json"), "w") as f:
        f.write('{"configuracion": "sistema", "version": "1.0"}')
    
    # Subcarpeta en documentos
    sub_docs_dir = os.path.join(docs_dir, "privados")
    os.makedirs(sub_docs_dir)
    
    with open(os.path.join(sub_docs_dir, "confidencial.txt"), "w") as f:
        f.write("Información confidencial muy importante")
    
    # Carpeta 2: Proyectos
    projects_dir = os.path.join(base_dir, "proyectos")
    os.makedirs(projects_dir)
    
    # Subcarpetas en proyectos
    proyecto1_dir = os.path.join(projects_dir, "proyecto1")
    os.makedirs(proyecto1_dir)
    
    with open(os.path.join(proyecto1_dir, "main.py"), "w") as f:
        f.write("# Archivo principal del proyecto\nprint('Hola mundo')")
    
    with open(os.path.join(proyecto1_dir, "README.md"), "w") as f:
        f.write("# Proyecto 1\nEste es el primer proyecto")
    
    proyecto2_dir = os.path.join(projects_dir, "proyecto2")
    os.makedirs(proyecto2_dir)
    
    with open(os.path.join(proyecto2_dir, "app.js"), "w") as f:
        f.write("// Aplicación JavaScript\nconsole.log('Aplicación iniciada');")
    
    # Carpeta 3: Imágenes
    images_dir = os.path.join(base_dir, "imagenes")
    os.makedirs(images_dir)
    
    # Simular archivos de imagen
    with open(os.path.join(images_dir, "foto1.jpg"), "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + b"fake_image_data" * 100)
    
    with open(os.path.join(images_dir, "foto2.png"), "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + b"fake_png_data" * 150)
    
    return base_dir, [docs_dir, projects_dir, images_dir]

def run_command(cmd, input_text=None):
    """Ejecuta un comando y retorna el resultado"""
    try:
        process = subprocess.Popen(
            cmd, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=input_text)
        return process.returncode, stdout, stderr
    except Exception as e:
        return -1, "", str(e)

def test_multiple_folders_backup():
    """Prueba 1: Selección de múltiples carpetas"""
    print("🧪 PRUEBA 1: Selección de múltiples carpetas")
    print("=" * 50)
    
    # Crear estructura de prueba
    base_dir, folders = create_test_structure()
    output_file = os.path.join(base_dir, "backup_multiple.zip")
    
    print(f"📁 Carpetas de prueba creadas en: {base_dir}")
    for folder in folders:
        folder_name = os.path.basename(folder)
        file_count = sum(len(files) for _, _, files in os.walk(folder))
        print(f"   📂 {folder_name}: {file_count} archivos")
    
    # Construir comando
    folders_str = " ".join(f'"{folder}"' for folder in folders)
    cmd = f'python -m src.main backup -d {folders_str} -o "{output_file}" -v'
    
    print(f"🚀 Ejecutando: {cmd}")
    returncode, stdout, stderr = run_command(cmd)
    
    if returncode == 0:
        print("✅ ÉXITO: Backup de múltiples carpetas completado")
        if os.path.exists(output_file):
            size_mb = os.path.getsize(output_file) / (1024 * 1024)
            print(f"📦 Archivo creado: {output_file} ({size_mb:.2f} MB)")
        else:
            print("❌ ERROR: Archivo de backup no encontrado")
            return False
    else:
        print("❌ ERROR en el backup de múltiples carpetas")
        print(f"Código de error: {returncode}")
        print(f"Error: {stderr}")
        return False
    
    print(f"Output:\n{stdout}")
    
    # Limpiar
    shutil.rmtree(base_dir)
    print("🧹 Archivos de prueba limpiados")
    return True

def test_encryption_backup():
    """Prueba 2: Encriptación opcional con AES-256"""
    print("\n🧪 PRUEBA 2: Encriptación opcional con AES-256")
    print("=" * 50)
    
    # Crear estructura de prueba
    base_dir, folders = create_test_structure()
    output_file = os.path.join(base_dir, "backup_encrypted")
    restore_dir = os.path.join(base_dir, "restored")
    
    print(f"📁 Carpetas de prueba creadas en: {base_dir}")
    
    # Test con encriptación
    folders_str = " ".join(f'"{folder}"' for folder in folders[:2])  # Solo 2 carpetas para rapidez
    password = "TestPassword123"
    
    cmd = f'python -m src.main backup -d {folders_str} -o "{output_file}" -e --password "{password}" -v'
    
    print(f"🔒 Ejecutando backup con encriptación: {cmd}")
    returncode, stdout, stderr = run_command(cmd)
    
    if returncode == 0:
        print("✅ ÉXITO: Backup con encriptación completado")
        
        # Buscar archivo encriptado
        encrypted_file = None
        for ext in [".enc", ".zip.enc"]:
            potential_file = output_file + ext
            if os.path.exists(potential_file):
                encrypted_file = potential_file
                break
        
        if not encrypted_file and os.path.exists(output_file):
            encrypted_file = output_file
        
        if encrypted_file:
            size_mb = os.path.getsize(encrypted_file) / (1024 * 1024)
            print(f"🔒 Archivo encriptado: {encrypted_file} ({size_mb:.2f} MB)")
            
            # Probar restauración
            print(f"🔓 Probando restauración con contraseña...")
            cmd_restore = f'python -m src.main restore -i "{encrypted_file}" -o "{restore_dir}" --password "{password}" -v'
            
            print(f"🚀 Ejecutando: {cmd_restore}")
            returncode_restore, stdout_restore, stderr_restore = run_command(cmd_restore)
            
            if returncode_restore == 0:
                print("✅ ÉXITO: Restauración con desencriptación completada")
                
                # Verificar archivos restaurados
                if os.path.exists(restore_dir):
                    restored_files = []
                    for root, dirs, files in os.walk(restore_dir):
                        restored_files.extend(files)
                    print(f"📂 Archivos restaurados: {len(restored_files)}")
                    if restored_files:
                        print("Algunos archivos restaurados:")
                        for file in restored_files[:5]:
                            print(f"   📄 {file}")
                else:
                    print("❌ ERROR: Directorio de restauración no encontrado")
                    return False
            else:
                print("❌ ERROR en la restauración")
                print(f"Error: {stderr_restore}")
                return False
        else:
            print("❌ ERROR: Archivo encriptado no encontrado")
            return False
    else:
        print("❌ ERROR en el backup con encriptación")
        print(f"Código de error: {returncode}")
        print(f"Error: {stderr}")
        return False
    
    print(f"Output backup:\n{stdout}")
    
    # Limpiar
    shutil.rmtree(base_dir)
    print("🧹 Archivos de prueba limpiados")
    return True

def test_encryption_wrong_password():
    """Prueba 3: Verificar que falla con contraseña incorrecta"""
    print("\n🧪 PRUEBA 3: Verificación de contraseña incorrecta")
    print("=" * 50)
    
    # Crear estructura de prueba
    base_dir, folders = create_test_structure()
    output_file = os.path.join(base_dir, "backup_encrypted")
    restore_dir = os.path.join(base_dir, "restored_wrong")
    
    folders_str = f'"{folders[0]}"'  # Solo una carpeta
    correct_password = "CorrectPassword123"
    wrong_password = "WrongPassword456"
    
    # Crear backup encriptado
    cmd = f'python -m src.main backup -d {folders_str} -o "{output_file}" -e --password "{correct_password}" -v'
    
    print(f"🔒 Creando backup encriptado...")
    returncode, stdout, stderr = run_command(cmd)
    
    if returncode != 0:
        print("❌ ERROR: No se pudo crear backup encriptado")
        shutil.rmtree(base_dir)
        return False
    
    # Buscar archivo encriptado
    encrypted_file = None
    for ext in [".enc", ".zip.enc"]:
        potential_file = output_file + ext
        if os.path.exists(potential_file):
            encrypted_file = potential_file
            break
    
    if not encrypted_file and os.path.exists(output_file):
        encrypted_file = output_file
    
    if encrypted_file:
        # Intentar restaurar con contraseña incorrecta
        print(f"🔓 Probando restauración con contraseña INCORRECTA...")
        cmd_restore = f'python -m src.main restore -i "{encrypted_file}" -o "{restore_dir}" --password "{wrong_password}" -v'
        
        returncode_restore, stdout_restore, stderr_restore = run_command(cmd_restore)
        
        if returncode_restore != 0:
            print("✅ ÉXITO: El sistema rechazó correctamente la contraseña incorrecta")
        else:
            print("❌ ERROR: El sistema NO rechazó la contraseña incorrecta")
            shutil.rmtree(base_dir)
            return False
    else:
        print("❌ ERROR: No se encontró archivo encriptado")
        shutil.rmtree(base_dir)
        return False
    
    # Limpiar
    shutil.rmtree(base_dir)
    print("🧹 Archivos de prueba limpiados")
    return True

def main():
    """Ejecuta todas las pruebas de requisitos"""
    print("🛡️  VALIDACIÓN DE REQUISITOS DEL SISTEMA DE BACKUP")
    print("=" * 60)
    print("Validando:")
    print("1. ✅ Selección de múltiples carpetas")
    print("2. ✅ Encriptación opcional con AES-256")
    print("=" * 60)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("src/main.py"):
        print("❌ ERROR: Ejecute este script desde el directorio raíz del proyecto")
        print("El archivo src/main.py debe existir")
        sys.exit(1)
    
    results = []
    
    # Ejecutar pruebas
    try:
        # Prueba 1: Múltiples carpetas
        result1 = test_multiple_folders_backup()
        results.append(("Selección de múltiples carpetas", result1))
        
        # Prueba 2: Encriptación
        result2 = test_encryption_backup()
        results.append(("Encriptación AES-256", result2))
        
        # Prueba 3: Contraseña incorrecta
        result3 = test_encryption_wrong_password()
        results.append(("Validación de contraseña", result3))
        
    except KeyboardInterrupt:
        print("\n⚠️  Pruebas interrumpidas por el usuario")
        sys.exit(1)
    
    # Mostrar resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE RESULTADOS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("\n🎉 ¡TODOS LOS REQUISITOS VALIDADOS EXITOSAMENTE!")
        print("✅ El sistema cumple con:")
        print("   📁 Selección de múltiples carpetas con escaneo recursivo")
        print("   🔒 Encriptación opcional con AES-256")
        print("   🔓 Validación correcta de contraseñas")
        return True
    else:
        print(f"\n⚠️  {total - passed} requisito(s) no se cumplieron")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)