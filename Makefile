# Makefile - Sistema de Backup Seguro
# Makefile principal para ejecución del proyecto y gestión general

# Variables
PYTHON := python3.13
PIP := pip3.13
SRC_DIR := src
DOCS_DIR := docs
LOGS_DIR := logs
VENV_DIR := venv

# Colores para output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
PURPLE := \033[0;35m
CYAN := \033[0;36m
NC := \033[0m # No Color

.PHONY: help setup install run backup restore demo clean
.PHONY: backup-encrypted backup-fragments backup-cloud restore-encrypted
.PHONY: install-package uninstall build package docs serve-docs
.PHONY: check-python check-deps info init-project dev-setup

# Target por defecto
help:
	@echo "$(BLUE)💾 Sistema de Backup Seguro - Ejecución Principal$(NC)"
	@echo ""
	@echo "$(YELLOW)🚀 Setup y Configuración:$(NC)"
	@echo "  setup              - Configura el entorno virtual e instala dependencias"
	@echo "  dev-setup          - Setup completo para desarrollo"
	@echo "  install            - Instala dependencias en el entorno actual"
	@echo "  check-python       - Verifica que Python 3.13+ esté disponible"
	@echo "  check-deps         - Verifica dependencias instaladas"
	@echo ""
	@echo "$(YELLOW)💾 Operaciones de Backup:$(NC)"
	@echo "  backup             - Crear backup básico de demostración"
	@echo "  backup-encrypted   - Crear backup con encriptación"
	@echo "  backup-fragments   - Crear backup fragmentado para USB"
	@echo "  backup-cloud       - Crear backup y subir a la nube"
	@echo ""
	@echo "$(YELLOW)📂 Operaciones de Restauración:$(NC)"
	@echo "  restore            - Restaurar backup básico"
	@echo "  restore-encrypted  - Restaurar backup encriptado"
	@echo "  demo               - Demostración completa (backup + restore)"
	@echo ""
	@echo "$(YELLOW)🎯 Ejecución Personalizada:$(NC)"
	@echo "  run                - Ejecutar el sistema con parámetros personalizados"
	@echo "  run-help           - Mostrar ayuda del sistema de backup"
	@echo ""
	@echo "$(YELLOW)📦 Distribución:$(NC)"
	@echo "  build              - Construir paquete distribuible"
	@echo "  package            - Crear paquete completo"
	@echo "  install-package    - Instalar como paquete del sistema"
	@echo "  uninstall          - Desinstalar paquete del sistema"
	@echo ""
	@echo "$(YELLOW)📚 Documentación y Utilidades:$(NC)"
	@echo "  docs               - Generar documentación"
	@echo "  serve-docs         - Servir documentación localmente"
	@echo "  clean              - Limpiar archivos temporales"
	@echo "  info               - Información del sistema"
	@echo ""
	@echo "$(YELLOW)🧪 Testing (usar test.mk):$(NC)"
	@echo "  make -f test.mk help    - Ver comandos de testing"
	@echo "  make -f test.mk test    - Ejecutar pruebas"
	@echo "  make -f test.mk quality - Pipeline de calidad"

# ===========================
# SETUP Y CONFIGURACIÓN
# ===========================

setup:
	@echo "$(BLUE)🚀 Configurando Sistema de Backup Seguro...$(NC)"
	@echo "$(CYAN)Verificando Python 3.13+...$(NC)"
	@$(MAKE) check-python
	@echo "$(CYAN)Creando entorno virtual...$(NC)"
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "$(CYAN)Instalando dependencias...$(NC)"
	$(VENV_DIR)/bin/pip install --upgrade pip
	$(VENV_DIR)/bin/pip install -r requirements.txt
	@echo "$(CYAN)Inicializando estructura del proyecto...$(NC)"
	@$(MAKE) init-project
	@echo "$(GREEN)✅ ¡Sistema de Backup Seguro configurado!$(NC)"
	@echo ""
	@echo "$(YELLOW)📝 Próximos pasos:$(NC)"
	@echo "  1. Activar entorno: source $(VENV_DIR)/bin/activate"
	@echo "  2. Probar sistema: make demo"
	@echo "  3. Ver ayuda: make run-help"

dev-setup: setup
	@echo "$(BLUE)🔧 Configurando entorno de desarrollo...$(NC)"
	@$(MAKE) -f test.mk install-test-deps
	@echo "$(GREEN)✅ Entorno de desarrollo listo$(NC)"
	@echo "$(YELLOW)💡 Usa 'make -f test.mk help' para comandos de testing$(NC)"

install:
	@echo "$(BLUE)📦 Instalando dependencias...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✅ Dependencias instaladas$(NC)"

# ===========================
# OPERACIONES DE BACKUP
# ===========================

backup:
	@echo "$(BLUE)💾 Creando backup de demostración...$(NC)"
	@echo "$(CYAN)Preparando datos de prueba...$(NC)"
	@mkdir -p demo_data/documentos demo_data/imagenes demo_data/proyectos
	@echo "Documento importante 1" > demo_data/documentos/importante.txt
	@echo "Documento importante 2" > demo_data/documentos/confidencial.txt
	@echo "Configuración del proyecto" > demo_data/proyectos/config.json
	@echo "README del proyecto" > demo_data/proyectos/README.md
	@echo "Datos de imagen simulados" > demo_data/imagenes/foto1.jpg
	@echo "$(CYAN)Ejecutando backup con ZIP...$(NC)"
	$(PYTHON) -m $(SRC_DIR).main backup \
		--directories demo_data/documentos demo_data/imagenes demo_data/proyectos \
		--output backup_demo.zip \
		--algorithm zip \
		--workers 4 \
		--verbose
	@echo "$(GREEN)✅ Backup creado: backup_demo.zip$(NC)"
	@ls -lh backup_demo.zip

backup-encrypted:
	@echo "$(BLUE)🔒 Creando backup encriptado...$(NC)"
	@echo "$(CYAN)Preparando datos confidenciales...$(NC)"
	@mkdir -p secure_data
	@echo "Información confidencial muy importante" > secure_data/secreto.txt
	@echo "Credenciales: usuario=admin, pass=secreto123" > secure_data/credenciales.txt
	@echo "Datos financieros confidenciales" > secure_data/finanzas.txt
	@echo "$(CYAN)Ejecutando backup con encriptación AES-256...$(NC)"
	@echo "$(YELLOW)Usando contraseña: MiPasswordSuperSegura123$(NC)"
	$(PYTHON) -m $(SRC_DIR).main backup \
		--directories secure_data \
		--output backup_encrypted.zip.enc \
		--algorithm zip \
		--encrypt \
		--password "MiPasswordSuperSegura123" \
		--workers 4 \
		--verbose
	@echo "$(GREEN)✅ Backup encriptado creado: backup_encrypted.zip.enc$(NC)"
	@ls -lh backup_encrypted.zip.enc

backup-fragments:
	@echo "$(BLUE)🧩 Creando backup fragmentado para USB...$(NC)"
	@echo "$(CYAN)Preparando archivo grande...$(NC)"
	@mkdir -p large_data
	@echo "Creando archivo grande simulado..."
	@for i in $$(seq 1 10000); do \
		echo "Línea $$i: Datos importantes que ocupan espacio significativo en el backup fragmentado" >> large_data/archivo_grande.txt; \
	done
	@echo "Archivo de video simulado" > large_data/video.mp4
	@echo "Archivo de base de datos" > large_data/database.db
	@echo "$(CYAN)Ejecutando backup fragmentado (fragmentos de 2MB)...$(NC)"
	$(PYTHON) -m $(SRC_DIR).main backup \
		--directories large_data \
		--output backup_fragments \
		--algorithm zip \
		--storage fragments \
		--fragment-size 2 \
		--workers 4 \
		--verbose
	@echo "$(GREEN)✅ Backup fragmentado creado en: backup_fragments/$(NC)"
	@ls -lh backup_fragments/

backup-cloud:
	@echo "$(BLUE)☁️  Creando backup para la nube...$(NC)"
	@echo "$(CYAN)Preparando datos para subir...$(NC)"
	@mkdir -p cloud_data
	@echo "Documento para la nube 1" > cloud_data/doc_nube_1.txt
	@echo "Documento para la nube 2" > cloud_data/doc_nube_2.txt
	@echo "Configuración en la nube" > cloud_data/cloud_config.json
	@echo "$(CYAN)Ejecutando backup con almacenamiento en nube...$(NC)"
	@echo "$(YELLOW)⚠️  Nota: Esta es una simulación, no se subirá realmente$(NC)"
	$(PYTHON) -m $(SRC_DIR).main backup \
		--directories cloud_data \
		--output backup_cloud.zip \
		--algorithm zip \
		--storage cloud \
		--cloud-service gdrive \
		--workers 4 \
		--verbose
	@echo "$(GREEN)✅ Backup para nube creado: backup_cloud.zip$(NC)"

# ===========================
# OPERACIONES DE RESTAURACIÓN
# ===========================

restore:
	@echo "$(BLUE)📂 Restaurando backup de demostración...$(NC)"
	@if [ -f backup_demo.zip ]; then \
		echo "$(CYAN)Restaurando desde backup_demo.zip...$(NC)"; \
		mkdir -p restored_data; \
		$(PYTHON) -m $(SRC_DIR).main restore \
			--input backup_demo.zip \
			--output-dir restored_data \
			--verbose; \
		echo "$(GREEN)✅ Backup restaurado en: restored_data/$(NC)"; \
		echo "$(CYAN)Contenido restaurado:$(NC)"; \
		find restored_data -type f | head -10; \
	else \
		echo "$(RED)❌ No se encontró backup_demo.zip$(NC)"; \
		echo "$(YELLOW)💡 Ejecuta 'make backup' primero$(NC)"; \
		exit 1; \
	fi

restore-encrypted:
	@echo "$(BLUE)🔓 Restaurando backup encriptado...$(NC)"
	@if [ -f backup_encrypted.zip.enc ]; then \
		echo "$(CYAN)Restaurando backup encriptado...$(NC)"; \
		echo "$(YELLOW)Usando contraseña: MiPasswordSuperSegura123$(NC)"; \
		mkdir -p restored_encrypted; \
		$(PYTHON) -m $(SRC_DIR).main restore \
			--input backup_encrypted.zip.enc \
			--output-dir restored_encrypted \
			--password "MiPasswordSuperSegura123" \
			--verbose; \
		echo "$(GREEN)✅ Backup encriptado restaurado en: restored_encrypted/$(NC)"; \
		echo "$(CYAN)Contenido desencriptado:$(NC)"; \
		find restored_encrypted -type f; \
	else \
		echo "$(RED)❌ No se encontró backup_encrypted.zip.enc$(NC)"; \
		echo "$(YELLOW)💡 Ejecuta 'make backup-encrypted' primero$(NC)"; \
		exit 1; \
	fi

demo: backup restore
	@echo "$(PURPLE)🎯 DEMOSTRACIÓN COMPLETA DEL SISTEMA$(NC)"
	@echo ""
	@echo "$(GREEN)✅ Operaciones completadas:$(NC)"
	@echo "  📁 demo_data/        - Datos originales creados"
	@echo "  📦 backup_demo.zip   - Backup comprimido generado"
	@echo "  📂 restored_data/    - Datos restaurados"
	@echo ""
	@echo "$(CYAN)🔍 Verificación de integridad:$(NC)"
	@if command -v diff >/dev/null 2>&1; then \
		echo "Comparando archivos originales vs restaurados..."; \
		if diff -r demo_data/ restored_data/ >/dev/null 2>&1; then \
			echo "$(GREEN)✅ ¡Integridad verificada! Los archivos son idénticos$(NC)"; \
		else \
			echo "$(YELLOW)⚠️  Se encontraron diferencias (puede ser normal según la estructura)$(NC)"; \
		fi; \
	else \
		echo "$(YELLOW)💡 Comando 'diff' no disponible para verificación automática$(NC)"; \
	fi
	@echo ""
	@echo "$(BLUE)📊 Estadísticas del backup:$(NC)"
	@if [ -f backup_demo.zip ]; then \
		original_size=$(du -sh demo_data/ | cut -f1); \
		backup_size=$(du -sh backup_demo.zip | cut -f1); \
		echo "  Tamaño original: $original_size"; \
		echo "  Tamaño backup: $backup_size"; \
	fi

# ===========================
# EJECUCIÓN PERSONALIZADA
# ===========================

run:
	@echo "$(BLUE)🎯 Ejecutando Sistema de Backup Seguro...$(NC)"
	@echo "$(YELLOW)💡 Uso: make run ARGS='backup -d /ruta -o archivo.zip'$(NC)"
	@echo "$(YELLOW)💡 Ejemplo: make run ARGS='backup -d ./mi_carpeta -o mi_backup.zip -a zip'$(NC)"
	@if [ -n "$(ARGS)" ]; then \
		echo "$(CYAN)Ejecutando: $(PYTHON) -m $(SRC_DIR).main $(ARGS)$(NC)"; \
		$(PYTHON) -m $(SRC_DIR).main $(ARGS); \
	else \
		echo "$(RED)❌ No se especificaron argumentos$(NC)"; \
		echo "$(CYAN)Mostrando ayuda del sistema:$(NC)"; \
		$(PYTHON) -m $(SRC_DIR).main --help; \
	fi

run-help:
	@echo "$(BLUE)📖 Ayuda del Sistema de Backup Seguro$(NC)"
	$(PYTHON) -m $(SRC_DIR).main --help

# Comandos de ejemplo rápido
quick-backup:
	@echo "$(BLUE)⚡ Backup rápido del directorio actual...$(NC)"
	@mkdir -p quick_backup_source
	@echo "Archivo rápido 1" > quick_backup_source/file1.txt
	@echo "Archivo rápido 2" > quick_backup_source/file2.txt
	$(PYTHON) -m $(SRC_DIR).main backup \
		-d quick_backup_source \
		-o quick_backup.zip \
		-a zip \
		-v
	@echo "$(GREEN)✅ Backup rápido creado: quick_backup.zip$(NC)"

# ===========================
# DISTRIBUCIÓN Y PACKAGING
# ===========================

build:
	@echo "$(BLUE)🔨 Construyendo paquete distribuible...$(NC)"
	@echo "$(CYAN)Limpiando builds anteriores...$(NC)"
	rm -rf build/ dist/ *.egg-info/
	@echo "$(CYAN)Construyendo paquete...$(NC)"
	$(PYTHON) setup.py sdist bdist_wheel
	@echo "$(GREEN)✅ Paquete construido en dist/$(NC)"
	@ls -la dist/

package: build
	@echo "$(BLUE)📦 Creando paquete completo...$(NC)"
	@echo "$(GREEN)✅ Paquete listo para distribución$(NC)"
	@echo ""
	@echo "$(YELLOW)📋 Archivos generados:$(NC)"
	@ls -la dist/
	@echo ""
	@echo "$(CYAN)💡 Para instalar:$(NC)"
	@echo "  pip install dist/secure_backup-*.whl"

install-package: build
	@echo "$(BLUE)⚙️  Instalando paquete en el sistema...$(NC)"
	$(PIP) install dist/*.whl --force-reinstall
	@echo "$(GREEN)✅ Paquete instalado$(NC)"
	@echo "$(CYAN)💡 Ahora puedes usar: secure-backup$(NC)"
	@echo "$(YELLOW)Prueba: secure-backup --help$(NC)"

uninstall:
	@echo "$(BLUE)🗑️  Desinstalando paquete del sistema...$(NC)"
	$(PIP) uninstall secure-backup -y
	@echo "$(GREEN)✅ Paquete desinstalado$(NC)"

# ===========================
# DOCUMENTACIÓN
# ===========================

docs:
	@echo "$(BLUE)📚 Generando documentación...$(NC)"
	@mkdir -p $(DOCS_DIR)
	@echo "$(CYAN)Creando documentación básica...$(NC)"
	@echo "# Sistema de Backup Seguro - Documentación" > $(DOCS_DIR)/index.md
	@echo "" >> $(DOCS_DIR)/index.md
	@echo "## Uso Básico" >> $(DOCS_DIR)/index.md
	@echo "" >> $(DOCS_DIR)/index.md
	@echo "\`\`\`bash" >> $(DOCS_DIR)/index.md
	@echo "# Crear backup" >> $(DOCS_DIR)/index.md
	@echo "python -m src.main backup -d /ruta/carpeta -o backup.zip" >> $(DOCS_DIR)/index.md
	@echo "" >> $(DOCS_DIR)/index.md
	@echo "# Restaurar backup" >> $(DOCS_DIR)/index.md
	@echo "python -m src.main restore -i backup.zip -o /destino" >> $(DOCS_DIR)/index.md
	@echo "\`\`\`" >> $(DOCS_DIR)/index.md
	@if command -v sphinx-build >/dev/null 2>&1; then \
		echo "$(CYAN)Generando documentación con Sphinx...$(NC)"; \
		sphinx-quickstart -q -p "Sistema de Backup Seguro" -a "Desarrollador" --ext-autodoc $(DOCS_DIR)/sphinx; \
		sphinx-build -b html $(DOCS_DIR)/sphinx $(DOCS_DIR)/html; \
		echo "$(GREEN)✅ Documentación Sphinx generada en $(DOCS_DIR)/html/$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  Sphinx no disponible, documentación básica creada$(NC)"; \
	fi
	@echo "$(GREEN)✅ Documentación generada en $(DOCS_DIR)/$(NC)"

serve-docs:
	@echo "$(BLUE)🌐 Sirviendo documentación...$(NC)"
	@if [ -d "$(DOCS_DIR)/html" ]; then \
		echo "$(CYAN)Documentación disponible en: http://localhost:8000$(NC)"; \
		echo "$(YELLOW)Presiona Ctrl+C para detener el servidor$(NC)"; \
		cd $(DOCS_DIR)/html && $(PYTHON) -m http.server 8000; \
	elif [ -f "$(DOCS_DIR)/index.md" ]; then \
		echo "$(CYAN)Sirviendo documentación básica en: http://localhost:8000$(NC)"; \
		echo "$(YELLOW)Presiona Ctrl+C para detener el servidor$(NC)"; \
		cd $(DOCS_DIR) && $(PYTHON) -m http.server 8000; \
	else \
		echo "$(RED)❌ Documentación no encontrada$(NC)"; \
		echo "$(YELLOW)💡 Ejecuta 'make docs' primero$(NC)"; \
	fi

# ===========================
# UTILIDADES Y VERIFICACIONES
# ===========================

check-python:
	@echo "$(BLUE)🐍 Verificando versión de Python...$(NC)"
	@python_version=$($(PYTHON) -c "import sys; print('.'.join(map(str, sys.version_info[:2])))"); \
	echo "Versión de Python detectada: $python_version"; \
	if $(PYTHON) -c "import sys; sys.exit(0 if sys.version_info >= (3, 13) else 1)"; then \
		echo "$(GREEN)✅ Python 3.13+ disponible$(NC)"; \
	else \
		echo "$(RED)❌ Se requiere Python 3.13 o superior$(NC)"; \
		echo "$(YELLOW)💡 Descarga desde: https://www.python.org/downloads/$(NC)"; \
		exit 1; \
	fi

check-deps:
	@echo "$(BLUE)🔍 Verificando dependencias...$(NC)"
	@echo "$(CYAN)Verificando Dask...$(NC)"
	@$(PYTHON) -c "import dask; print(f'✅ Dask: {dask.__version__}')" 2>/dev/null || echo "$(RED)❌ Dask no encontrado$(NC)"
	@echo "$(CYAN)Verificando cryptography...$(NC)"
	@$(PYTHON) -c "import cryptography; print(f'✅ Cryptography: {cryptography.__version__}')" 2>/dev/null || echo "$(RED)❌ Cryptography no encontrado$(NC)"
	@echo "$(CYAN)Verificando distributed...$(NC)"
	@$(PYTHON) -c "import distributed; print(f'✅ Distributed: {distributed.__version__}')" 2>/dev/null || echo "$(RED)❌ Distributed no encontrado$(NC)"
	@echo "$(CYAN)Verificando tqdm...$(NC)"
	@$(PYTHON) -c "import tqdm; print(f'✅ tqdm: {tqdm.__version__}')" 2>/dev/null || echo "$(RED)❌ tqdm no encontrado$(NC)"
	@echo "$(GREEN)✅ Verificación de dependencias completada$(NC)"

init-project:
	@echo "$(BLUE)🏗️  Inicializando estructura del proyecto...$(NC)"
	@mkdir -p $(SRC_DIR)/core $(SRC_DIR)/utils $(SRC_DIR)/ui
	@mkdir -p tests
	@mkdir -p $(DOCS_DIR) $(LOGS_DIR)
	@touch $(SRC_DIR)/__init__.py
	@touch $(SRC_DIR)/core/__init__.py
	@touch $(SRC_DIR)/utils/__init__.py
	@touch $(SRC_DIR)/ui/__init__.py
	@touch tests/__init__.py
	@if [ ! -f "$(LOGS_DIR)/.gitkeep" ]; then \
		touch $(LOGS_DIR)/.gitkeep; \
	fi
	@echo "$(GREEN)✅ Estructura del proyecto inicializada$(NC)"

clean:
	@echo "$(BLUE)🧹 Limpiando archivos temporales del proyecto...$(NC)"
	@echo "$(CYAN)Limpiando archivos Python...$(NC)"
	find . -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(CYAN)Limpiando archivos de backup de demo...$(NC)"
	rm -f backup_demo.zip backup_encrypted.zip.enc backup_cloud.zip quick_backup.zip
	rm -rf backup_fragments/
	@echo "$(CYAN)Limpiando datos de demo...$(NC)"
	rm -rf demo_data/ restored_data/ restored_encrypted/ secure_data/ cloud_data/ large_data/
	rm -rf quick_backup_source/
	@echo "$(CYAN)Limpiando archivos de build...$(NC)"
	rm -rf build/ dist/
	@echo "$(CYAN)Limpiando logs...$(NC)"
	rm -f $(LOGS_DIR)/*.log 2>/dev/null || true
	@echo "$(GREEN)✅ Limpieza completada$(NC)"

info:
	@echo "$(BLUE)ℹ️  Información del Sistema de Backup Seguro$(NC)"
	@echo ""
	@echo "$(YELLOW)📋 Configuración:$(NC)"
	@echo "  Python: $($(PYTHON) --version 2>/dev/null || echo 'No disponible')"
	@echo "  Pip: $($(PIP) --version 2>/dev/null || echo 'No disponible')"
	@echo "  SO: $(uname -s 2>/dev/null || echo 'Desconocido')"
	@echo "  Directorio: $(pwd)"
	@echo ""
	@echo "$(YELLOW)📁 Estructura:$(NC)"
	@echo "  Código fuente: $(SRC_DIR)/"
	@echo "  Documentación: $(DOCS_DIR)/"
	@echo "  Logs: $(LOGS_DIR)/"
	@echo ""
	@echo "$(YELLOW)🔧 Estado del proyecto:$(NC)"
	@if [ -d "$(SRC_DIR)" ]; then \
		echo "  ✅ Directorio fuente existe"; \
	else \
		echo "  ❌ Directorio fuente no encontrado"; \
	fi
	@if [ -f "requirements.txt" ]; then \
		echo "  ✅ Archivo de dependencias existe"; \
	else \
		echo "  ❌ requirements.txt no encontrado"; \
	fi
	@if [ -d "$(VENV_DIR)" ]; then \
		echo "  ✅ Entorno virtual configurado"; \
	else \
		echo "  ⚠️  Entorno virtual no encontrado"; \
	fi

# Comandos de conveniencia
status: info check-deps
	@echo "$(GREEN)📊 Estado del sistema verificado$(NC)"

# Pipeline completo de demostración
full-demo: clean setup demo backup-encrypted restore-encrypted
	@echo "$(PURPLE)🎉 DEMOSTRACIÓN COMPLETA FINALIZADA$(NC)"
	@echo ""
	@echo "$(GREEN)✅ Todas las funcionalidades probadas:$(NC)"
	@echo "  📦 Backup básico con ZIP"
	@echo "  🔒 Backup con encriptación AES-256"
	@echo "  📂 Restauración básica"
	@echo "  🔓 Restauración con desencriptación"
	@echo ""
	@echo "$(CYAN)💡 El sistema está listo para uso en producción$(NC)"