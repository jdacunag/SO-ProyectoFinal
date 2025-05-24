# Sistema de Backup Seguro con Dask

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-Educational-green.svg)](LICENSE)
[![Dask](https://img.shields.io/badge/Dask-Parallel-orange.svg)](https://dask.org)
[![AES](https://img.shields.io/badge/Encryption-AES--256-red.svg)](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard)

Un sistema completo de backup con compresión, encriptación y paralelización desarrollado para la asignatura **Sistemas Operativos (ST0257)** de la Universidad EAFIT.

## 🎯 Características Principales

### 🚀 Algoritmos de Compresión Clásicos
- **ZIP**: Rápido y compatible universalmente
- **GZIP**: Balance óptimo velocidad/compresión  
- **BZIP2**: Máxima compresión para archivos grandes

### 🔒 Seguridad Robusta
- **Encriptación AES-256**: Estándar militar con claves de 256 bits
- **PBKDF2**: Derivación segura de claves con 100,000 iteraciones
- **Validación de integridad**: Verificación automática con checksums MD5

### 🧩 Almacenamiento Flexible
- **Local/Disco Externo**: Copia directa con verificación de integridad
- **Fragmentación USB**: División automática para múltiples dispositivos
- **Nube Simulada**: Soporte para Google Drive y Dropbox (modo demo)

### ⚡ Paralelismo con Dask
- **Compresión paralela**: Procesamiento simultáneo de múltiples archivos
- **Escalabilidad**: Configuración automática de workers según CPU disponible
- **Optimización I/O**: Operaciones de lectura/escritura paralelas

## 🛠️ Tecnologías Utilizadas

| Componente | Tecnología | Versión | Propósito |
|------------|------------|---------|-----------|
| **Paralelismo** | Dask | 2023.5.0+ | Procesamiento distribuido |
| **Encriptación** | Cryptography | 41.0.0+ | Seguridad AES-256 |
| **Interfaz** | Click/Argparse | Nativo | CLI intuitiva |
| **Progreso** | tqdm | 4.64.0+ | Barras de progreso |
| **Logs** | Logging | Nativo | Trazabilidad completa |

## 📦 Instalación

### Prerrequisitos
- Python 3.13 o superior
- pip (gestor de paquetes)
- 4GB RAM mínimo (8GB recomendado)

### Instalación Rápida

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/SO-ProyectoFinal.git
cd SO-ProyectoFinal

# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación
python -m src.main --help
```

## 🚀 Uso Rápido

### Backup Básico (Múltiples Carpetas)
```bash
# Comprimir varias carpetas
python -m src.main backup \
   -d ./documentos ./proyectos ./fotos \
   -o backup_completo.zip \
   -a zip
```

### Backup con Encriptación AES-256

```bash
# Backup encriptado y seguro
python -m src.main backup \
    -d ./datos_importantes \
    -o backup_seguro.zip.enc \
    -e --password mi_clave_segura \
    -a bzip2
```

### Backup Fragmentado para USB

```bash
# Fragmentar en archivos de 1GB para múltiples USB
python -m src.main backup \
    -d ./archivo_grande \
    -o backup_usb \
    -s fragments \
    --fragment-size 1024
```

### Backup a la Nube (Simulado)

```bash
# Subir a Google Drive (modo demo)
python -m src.main backup \
    -d ./mi_proyecto \
    -o backup_nube.zip \
    -s cloud \
    --cloud-service gdrive
```

### Restauración

```
# Restaurar backup normal
python -m src.main restore \
    -i backup_completo.zip \
    -o ./restaurado

# Restaurar backup encriptado
python -m src.main restore \
    -i backup_seguro.zip.enc \
    -o ./restaurado \
    --password mi_clave_segura
```
