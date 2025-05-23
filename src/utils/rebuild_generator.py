"""
Rebuild Generator - Módulo para generar scripts de reconstrucción de fragmentos
src/utils/rebuild_generator.py
"""

import os
import json
from pathlib import Path

def create_rebuild_scripts(output_dir, metadata):
    """
    Crea scripts para reconstruir el archivo desde fragmentos
    """
    output_dir = Path(output_dir)
    original_stem = Path(metadata['original_file']).stem
    
    # Crear script de Python
    _create_python_rebuild_script(output_dir, metadata, original_stem)
    
    # Crear script de Batch para Windows
    _create_batch_rebuild_script(output_dir, original_stem)
    
    # Crear script de Bash para Unix
    _create_bash_rebuild_script(output_dir, original_stem)
    
    # Crear README
    _create_readme_file(output_dir, metadata)

def _create_python_rebuild_script(output_dir, metadata, original_stem):
    """Crea el script principal de reconstrucción en Python"""
    
    script_content = f'''#!/usr/bin/env python3
"""
Script de reconstitución automática
Generado por Sistema de Backup Seguro
"""

import os
import json
import hashlib
from pathlib import Path

def rebuild_file():
    """Reconstruye el archivo original desde los fragmentos"""
    metadata_file = "{original_stem}.metadata.json"
    
    # Verificar que existe el archivo de metadatos
    if not os.path.exists(metadata_file):
        print(f"❌ Archivo de metadatos no encontrado: {{metadata_file}}")
        return False
    
    # Cargar metadatos
    try:
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
    except Exception as e:
        print(f"❌ Error leyendo metadatos: {{e}}")
        return False
    
    original_name = Path(metadata['original_file']).name
    fragments = metadata['fragments']
    expected_size = metadata['file_size']
    
    print(f"🔧 Reconstruyendo: {{original_name}}")
    print(f"📊 Fragmentos esperados: {{len(fragments)}}")
    print(f"📏 Tamaño esperado: {{expected_size / (1024*1024):.2f}} MB")
    print("-" * 50)
    
    # Verificar que todos los fragmentos existen
    missing = []
    for fragment_name in fragments.keys():
        if not os.path.exists(fragment_name):
            missing.append(fragment_name)
    
    if missing:
        print(f"❌ Fragmentos faltantes:")
        for frag in missing:
            print(f"   - {{frag}}")
        return False
    
    print("✅ Todos los fragmentos encontrados")
    
    # Verificar checksums antes de reconstruir
    print("🔍 Verificando integridad de fragmentos...")
    for fragment_name, frag_info in fragments.items():
        try:
            with open(fragment_name, 'rb') as f:
                data = f.read()
            
            actual_checksum = hashlib.md5(data).hexdigest()
            expected_checksum = frag_info['checksum']
            
            if actual_checksum != expected_checksum:
                print(f"❌ Error de integridad en {{fragment_name}}")
                print(f"   Esperado: {{expected_checksum}}")
                print(f"   Actual:   {{actual_checksum}}")
                return False
            else:
                print(f"✅ {{fragment_name}} - OK")
        
        except Exception as e:
            print(f"❌ Error verificando {{fragment_name}}: {{e}}")
            return False
    
    print("✅ Verificación de integridad completada")
    print()
    
    # Reconstruir archivo
    print(f"🔨 Reconstruyendo {{original_name}}...")
    try:
        with open(original_name, 'wb') as output_file:
            for i in range(len(fragments)):
                fragment_name = f"{{Path(metadata['original_file']).stem}}.part{{i:03d}}"
                
                if fragment_name not in fragments:
                    print(f"❌ Fragmento {{fragment_name}} no encontrado en metadatos")
                    return False
                
                print(f"📄 Procesando: {{fragment_name}}")
                
                with open(fragment_name, 'rb') as fragment_file:
                    data = fragment_file.read()
                    output_file.write(data)
        
        print(f"✅ Archivo reconstruido: {{original_name}}")
        
        # Verificar tamaño final
        final_size = os.path.getsize(original_name)
        
        if final_size == expected_size:
            print(f"✅ Verificación de tamaño exitosa: {{final_size:,}} bytes")
            print(f"📊 Tamaño final: {{final_size / (1024*1024):.2f}} MB")
            return True
        else:
            print(f"❌ Error de tamaño:")
            print(f"   Esperado: {{expected_size:,}} bytes")
            print(f"   Obtenido: {{final_size:,}} bytes")
            return False
    
    except Exception as e:
        print(f"❌ Error durante la reconstrucción: {{e}}")
        return False

def show_fragment_info():
    """Muestra información sobre los fragmentos disponibles"""
    metadata_file = "{original_stem}.metadata.json"
    
    if not os.path.exists(metadata_file):
        print(f"❌ Archivo de metadatos no encontrado: {{metadata_file}}")
        return
    
    try:
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
    except Exception as e:
        print(f"❌ Error leyendo metadatos: {{e}}")
        return
    
    print("📋 Información de Fragmentos")
    print("=" * 40)
    print(f"Archivo original: {{Path(metadata['original_file']).name}}")
    print(f"Tamaño original: {{metadata['file_size'] / (1024*1024):.2f}} MB")
    print(f"Tamaño de fragmento: {{metadata['fragment_size_mb']}} MB")
    print(f"Número de fragmentos: {{metadata['num_fragments']}}")
    print(f"Creado por: {{metadata.get('created_by', 'Desconocido')}}")
    print()
    
    fragments = metadata['fragments']
    total_size = 0
    
    print("Fragmentos:")
    for i, (fragment_name, frag_info) in enumerate(sorted(fragments.items())):
        exists = "✅" if os.path.exists(fragment_name) else "❌"
        size_mb = frag_info['size'] / (1024*1024)
        total_size += frag_info['size']
        print(f"  {{i+1:2d}}. {{exists}} {{fragment_name}} - {{size_mb:.2f}} MB")
    
    print(f"\\nTamaño total de fragmentos: {{total_size / (1024*1024):.2f}} MB")
    
    # Verificar fragmentos faltantes
    missing = [name for name in fragments.keys() if not os.path.exists(name)]
    if missing:
        print(f"\\n⚠️  Fragmentos faltantes: {{len(missing)}}")
        for frag in missing:
            print(f"   - {{frag}}")
    else:
        print("\\n✅ Todos los fragmentos están presentes")

if __name__ == "__main__":
    print("🔧 Script de Reconstitución - Sistema de Backup Seguro")
    print("=" * 60)
    print()
    
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "info":
            show_fragment_info()
            sys.exit(0)
        elif sys.argv[1] == "help":
            print("Uso:")
            print("  python rebuild.py        - Reconstruir archivo")
            print("  python rebuild.py info   - Mostrar información de fragmentos")
            print("  python rebuild.py help   - Mostrar esta ayuda")
            sys.exit(0)
    
    if rebuild_file():
        print()
        print("🎉 ¡Reconstitución exitosa!")
        print("💡 El archivo ha sido reconstruido correctamente.")
    else:
        print()
        print("💥 Error en la reconstitución")
        print("💡 Verifica que todos los fragmentos estén presentes e íntegros.")
        sys.exit(1)
'''
    
    script_path = output_dir / "rebuild.py"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # Hacer ejecutable en sistemas Unix
    try:
        os.chmod(script_path, 0o755)
    except:
        pass

def _create_batch_rebuild_script(output_dir, original_stem):
    """Crea script batch para Windows"""
    
    batch_content = '''@echo off
title Sistema de Backup Seguro - Reconstitución
echo.
echo ========================================
echo   Script de Reconstitución - Windows
echo ========================================
echo.

REM Verificar que Python está disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado o no está en el PATH
    echo 💡 Instala Python desde https://python.org
    pause
    exit /b 1
)

REM Verificar que existe el script de Python
if not exist "rebuild.py" (
    echo ❌ Script rebuild.py no encontrado
    echo 💡 Asegúrate de ejecutar este script en el directorio correcto
    pause
    exit /b 1
)

REM Mostrar menú
echo Opciones disponibles:
echo 1. Reconstruir archivo
echo 2. Mostrar información de fragmentos
echo 3. Salir
echo.
set /p choice="Selecciona una opción (1-3): "

if "%choice%"=="1" (
    echo.
    echo 🔧 Iniciando reconstrucción...
    python rebuild.py
) else if "%choice%"=="2" (
    echo.
    echo 📋 Mostrando información...
    python rebuild.py info
) else if "%choice%"=="3" (
    echo.
    echo 👋 ¡Hasta luego!
    exit /b 0
) else (
    echo.
    echo ❌ Opción inválida
)

echo.
pause
'''
    
    batch_path = output_dir / "rebuild.bat"
    with open(batch_path, 'w', encoding='cp1252') as f:
        f.write(batch_content)

def _create_bash_rebuild_script(output_dir, original_stem):
    """Crea script bash para Unix/Linux/macOS"""
    
    bash_content = '''#!/bin/bash

# Script de Reconstitución - Sistema de Backup Seguro
# Para sistemas Unix/Linux/macOS

echo "========================================"
echo "  Script de Reconstitución - Unix/Linux"
echo "========================================"
echo

# Verificar que Python está disponible
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ Python no está instalado"
        echo "💡 Instala Python 3 usando tu gestor de paquetes"
        exit 1
    else
        PYTHON="python"
    fi
else
    PYTHON="python3"
fi

# Verificar que existe el script de Python
if [ ! -f "rebuild.py" ]; then
    echo "❌ Script rebuild.py no encontrado"
    echo "💡 Asegúrate de ejecutar este script en el directorio correcto"
    exit 1
fi

# Mostrar menú
echo "Opciones disponibles:"
echo "1. Reconstruir archivo"
echo "2. Mostrar información de fragmentos"
echo "3. Salir"
echo
read -p "Selecciona una opción (1-3): " choice

case $choice in
    1)
        echo
        echo "🔧 Iniciando reconstrucción..."
        $PYTHON rebuild.py
        ;;
    2)
        echo
        echo "📋 Mostrando información..."
        $PYTHON rebuild.py info
        ;;
    3)
        echo
        echo "👋 ¡Hasta luego!"
        exit 0
        ;;
    *)
        echo
        echo "❌ Opción inválida"
        ;;
esac

echo
read -p "Presiona Enter para continuar..."
'''
    
    bash_path = output_dir / "rebuild.sh"
    with open(bash_path, 'w', encoding='utf-8') as f:
        f.write(bash_content)
    
    # Hacer ejecutable
    try:
        os.chmod(bash_path, 0o755)
    except:
        pass

def _create_readme_file(output_dir, metadata):
    """Crea un archivo README con instrucciones"""
    
    readme_content = f'''# Fragmentos de Backup - Sistema de Backup Seguro

## Información del Backup

- **Archivo original:** {Path(metadata['original_file']).name}
- **Tamaño original:** {metadata['file_size'] / (1024*1024):.2f} MB
- **Número de fragmentos:** {metadata['num_fragments']}
- **Tamaño por fragmento:** {metadata['fragment_size_mb']} MB

## Cómo Reconstruir el Archivo

### Opción 1: Script Automático (Recomendado)

**En Windows:**
```
Doble clic en: rebuild.bat
```

**En Linux/macOS:**
```bash
chmod +x rebuild.sh
./rebuild.sh
```

### Opción 2: Script de Python Directo

```bash
python rebuild.py
```

**Comandos adicionales:**
```bash
python rebuild.py info    # Ver información de fragmentos
python rebuild.py help    # Ver ayuda
```

## Archivos Incluidos

- `{Path(metadata['original_file']).stem}.part000, .part001, ...` - Fragmentos del archivo
- `{Path(metadata['original_file']).stem}.metadata.json` - Metadatos del backup
- `rebuild.py` - Script principal de reconstrucción
- `rebuild.bat` - Script para Windows
- `rebuild.sh` - Script para Unix/Linux/macOS
- `README.md` - Este archivo

## Verificación de Integridad

El script de reconstrucción verifica automáticamente:
- ✅ Presencia de todos los fragmentos
- ✅ Integridad de cada fragmento (checksums MD5)
- ✅ Tamaño final del archivo reconstruido

## Solución de Problemas

**Error: "Fragmentos faltantes"**
- Asegúrate de que todos los archivos .part??? están en el directorio
- Verifica que no se hayan dañado durante la transferencia

**Error: "Error de integridad"**
- Algún fragmento se ha dañado
- Intenta copiar nuevamente los fragmentos desde el backup original

**Error: "Python no encontrado"**
- Instala Python 3.x desde https://python.org
- En Linux: `sudo apt install python3` o equivalente

## Soporte

Este backup fue creado con el Sistema de Backup Seguro v1.0
Para más información, consulta la documentación del proyecto.
'''
    
    readme_path = output_dir / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)