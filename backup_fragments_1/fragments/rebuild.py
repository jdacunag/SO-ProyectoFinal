#!/usr/bin/env python3
"""
Script básico de reconstitución
Generado por Sistema de Backup Seguro
"""

import os
import json
from pathlib import Path

def rebuild_file():
    metadata_file = "backup.metadata.json"
    
    if not os.path.exists(metadata_file):
        print(f"❌ Archivo de metadatos no encontrado: {metadata_file}")
        return False
    
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    
    original_name = Path(metadata['original_file']).name
    fragments = metadata['fragments']
    
    print(f"🔧 Reconstruyendo: {original_name}")
    print(f"📊 Fragmentos: {len(fragments)}")
    
    # Verificar fragmentos
    missing = [name for name in fragments.keys() if not os.path.exists(name)]
    if missing:
        print(f"❌ Fragmentos faltantes: {missing}")
        return False
    
    # Reconstruir
    with open(original_name, 'wb') as output_file:
        for i in range(len(fragments)):
            fragment_name = f"{Path(metadata['original_file']).stem}.part{i:03d}"
            print(f"📄 Procesando: {fragment_name}")
            
            with open(fragment_name, 'rb') as fragment_file:
                output_file.write(fragment_file.read())
    
    print(f"✅ Archivo reconstruido: {original_name}")
    return True

if __name__ == "__main__":
    print("🔧 Script de Reconstitución Básico")
    print("=" * 40)
    if rebuild_file():
        print("🎉 ¡Reconstitución exitosa!")
    else:
        print("💥 Error en la reconstitución")
