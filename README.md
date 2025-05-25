# Sistema de Backup Seguro con Dask

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-Educational-green.svg)](LICENSE)
[![Dask](https://img.shields.io/badge/Dask-Parallel-orange.svg)](https://dask.org)
[![AES](https://img.shields.io/badge/Encryption-AES--256-red.svg)](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard)

Un sistema completo de backup con compresión, encriptación y paralelización desarrollado para la asignatura **Sistemas Operativos (ST0257)** de la Universidad EAFIT.

## 👥 Integrantes del Equipo

* David Lopera Londoño
*  Verónica Zapata Vargas
*  Juan Diego Acuña Giraldo

## 🎥 Vídeo de Sustentación
El vídeo de la sustentación del proyecto se encuentra adjunto en el repositorio.

## 📋 Documento Técnico
El documento técnico se encuentra adjunto en el repositorio como un archivo .PDF

## ⚙️ Estructura del Proyecto 

```
SO-ProyectoFinal/                  
├── src/                         # Código fuente principal
│   ├── core/                    # Módulos principales
│   │   ├── scanner.py           # Escaneo de directorios
│   │   ├── compressor.py        # Algoritmos de compresión
│   │   ├── encryptor.py         # Encriptación AES-256
│   │   ├── storage.py           # Gestión de almacenamiento
│   │   └── restore.py           # Restauración de backups
│   ├── utils/                   # Utilidades y helpers
│   │   ├── logger.py            # Sistema de logging
│   │   ├── error_handler.py     # Manejo de errores
│   │   ├── parallel.py          # Utilidades de paralelismo
│   │   └── rebuild_generator.py # Generación de scripts
│   └── main.py                  # Punto de entrada principal
├── tests/                       # Suite de testing
│   ├── test_scanner.py          # Tests del scanner
│   ├── test_compressor.py       # Tests del compressor
│   └── test_requirements.py     # Tests de requisitos
├── backups/                     # Directorio de backups
├── restored/                    # Directorio de restauración
├── logs/                        # Archivos de log
├── run_tests.py                 # Ejecutor de tests
├── test.mk                      # Makefile de testing
├── requirements.txt             # Dependencias
└── README.md                    # Documentación principal
```

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

### Rebuild de Backup Fragmentado

```bash
cd backups/backup_fragments/fragments

python rebuild.py 
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

## 🤖 Tests Unitarios

### 🔍 Tests del Scanner (test_scanner.py)

* Escaneo de directorios únicos
* Escaneo de múltiples directorios
* Procesamiento paralelo vs secuencial
* Manejo de directorios inexistentes
* Directorios vacíos
* Archivos con nombres Unicode
* Estructuras grandes de directorios

```bash
python# Ejemplo de test unitario
def test_scan_single_directory(self):
    """Prueba el escaneo de un solo directorio"""
    files = scanner.scan_directory(self.test_dir)
    self.assertGreater(len(files), 0)
```
### 🗜️ Tests del Compressor (test_compressor.py)

* Compresión con algoritmos ZIP, GZIP, BZIP2
* Archivos únicos vs múltiples archivos
* Comparación de ratios de compresión
* Rendimiento paralelo vs secuencial
* Manejo de archivos grandes
* Operaciones concurrentes
* Manejo de errores

```bash
python# Ejemplo de test de rendimiento
def test_parallel_vs_sequential_performance(self):
    """Compara rendimiento paralelo vs secuencial"""
    # Mide tiempos y calcula speedup
```

### 🚀 Ejecución de Tests

##### Métodos de Ejecución

**1. Script Principal**:

```bash
# Ejecutar todas las pruebas
python run_tests.py

# Ejecutar módulo específico
python run_tests.py --module scanner
python run_tests.py --module compressor

# Solo pruebas de rendimiento
python run_tests.py --performance

# Modo verboso
python run_tests.py --verbose
```

**2. Pipeline de Calidad con Makefile:**

```bash
# Tests básicos
make -f test.mk test

# Tests con formato y linting
make -f test.mk quality

# Solo pruebas de rendimiento
make -f test.mk test-performance

# Limpieza
make -f test.mk clean-test
```

### ⚠️ Gestión de Errores

El sistema implementa un manejo robusto de errores mediante múltiples capas de protección. Se utilizan decoradores especializados como @retry para operaciones de red con reintentos automáticos, y @safe_file_operation para operaciones de archivo que manejan errores de permisos y espacio insuficiente.

Las excepciones personalizadas (BackupError, CompressionError, EncryptionError, StorageError) proporcionan contexto específico sobre el tipo de fallo, facilitando el debugging y la recuperación. Cada módulo implementa fallback automático: si Dask falla, el sistema cambia transparentemente a procesamiento secuencial; si una operación de red falla, se reintenta con delay exponencial.

El sistema de logging contextual registra todos los errores con timestamps y trazabilidad completa, mientras que la limpieza automática de archivos temporales garantiza que no queden residuos tras un error. Esta arquitectura asegura que el sistema sea resiliente y proporcione información útil para diagnóstico sin comprometer la integridad de los datos.

## Conclusiones

onclusiones
El Sistema de Backup Seguro cumple exitosamente con todos los requisitos establecidos, implementando selección de múltiples carpetas con escaneo recursivo paralelo y encriptación AES-256 opcional con validación robusta. El proyecto incorpora tres algoritmos de compresión (ZIP, GZIP, BZIP2) optimizados con paralelismo Dask y una interfaz CLI completa.

Los aprendizajes técnicos clave abarcan implementación práctica de paralelismo con Dask, aplicación correcta de criptografía AES-256 y PBKDF2, diseño de arquitectura modular que facilita mantenimiento, y manejo eficiente de operaciones de archivo a gran escala con gestión inteligente de recursos del sistema.
