test-verbose:
	@echo "$(BLUE)🔊 Ejecutando pruebas con salida detallada...$(NC)"
	$(PYTHON) run_tests.py --module scanner --verbose
	$(PYTHON) run_tests.py --module compressor --verbose
	@echo "$(GREEN)✅ Pruebas detalladas completadas$(NC)"

# ===========================
# PRUEBAS POR MÓDULO
# ===========================

test-scanner:
	@echo "$(BLUE)🔍 Ejecutando pruebas del scanner...$(NC)"
	@if [ -f "$(TESTS_DIR)/test_scanner.py" ]; then \
		$(PYTHON) run_tests.py --module scanner; \
		echo "$(GREEN)✅ Pruebas del scanner completadas$(NC)"; \
	else \
		echo "$(RED)❌ test_scanner.py no encontrado en $(TESTS_DIR)/$(NC)"; \
		exit 1; \
	fi

test-compressor:
	@echo "$(BLUE)🗜️  Ejecutando pruebas del compressor...$(NC)"
	@if [ -f "$(TESTS_DIR)/test_compressor.py" ]; then \
		$(PYTHON) run_tests.py --module compressor; \
		echo "$(GREEN)✅ Pruebas del compressor completadas$(NC)"; \
	else \
		echo "$(RED)❌ test_compressor.py no encontrado en $(TESTS_DIR)/$(NC)"; \
		exit 1; \
	fi

# ===========================
# PRUEBAS ESPECIALIZADAS
# ===========================

test-performance:
	@echo "$(BLUE)⚡ Ejecutando pruebas de rendimiento...$(NC)"
	@if [ -f "$(TESTS_DIR)/test_compressor.py" ]; then \
		echo "$(CYAN)Ejecutando pruebas de rendimiento del compressor...$(NC)"; \
		$(PYTHON) -m unittest $(TESTS_DIR).test_compressor.TestCompressor.test_parallel_vs_sequential_performance -v; \
		$(PYTHON) -m unittest $(TESTS_DIR).test_compressor.TestCompressor.test_large_file_compression -v; \
		$(PYTHON) -m unittest $(TESTS_DIR).test_compressor.TestCompressor.test_different_worker_counts -v; \
		echo "$(GREEN)✅ Pruebas de rendimiento completadas$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  test_compressor.py no encontrado, saltando pruebas de rendimiento$(NC)"; \
	fi

test-parallel:
	@echo "$(BLUE)⚡ Ejecutando pruebas específicas de paralelismo...$(NC)"
	@echo "$(CYAN)Pruebas de paralelismo en scanner...$(NC)"
	@if [ -f "$(TESTS_DIR)/test_scanner.py" ]; then \
		$(PYTHON) -m unittest $(TESTS_DIR).test_scanner.TestScanner.test_scan_multiple_directories_parallel -v; \
	fi
	@echo "$(CYAN)Pruebas de paralelismo en compressor...$(NC)"
	@if [ -f "$(TESTS_DIR)/test_compressor.py" ]; then \
		$(PYTHON) -m unittest $(TESTS_DIR).test_compressor.TestCompressor.test_parallel_vs_sequential_performance -v; \
		$(PYTHON) -m unittest $(TESTS_DIR).test_compressor.TestCompressor.test_concurrent_compression_operations -v; \
	fi
	@echo "$(GREEN)✅ Pruebas de paralelismo completadas$(NC)"

# ===========================
# CALIDAD DE CÓDIGO
# ===========================

lint:
	@echo "$(BLUE)🔍 Ejecutando linting con flake8...$(NC)"
	@if command -v flake8 >/dev/null 2>&1; then \
		echo "$(CYAN)Verificando errores críticos en $(SRC_DIR)/...$(NC)"; \
		flake8 $(SRC_DIR) --count --select=E9,F63,F7,F82 --show-source --statistics; \
		echo "$(CYAN)Verificando estilo en $(SRC_DIR)/...$(NC)"; \
		flake8 $(SRC_DIR) --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics; \
		echo "$(CYAN)Verificando archivos de prueba...$(NC)"; \
		flake8 $(TESTS_DIR)/test_scanner.py $(TESTS_DIR)/test_compressor.py --count --exit-zero --max-line-length=127 --statistics 2>/dev/null || true; \
		echo "$(GREEN)✅ Linting completado$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  flake8 no encontrado. Instala con: make -f test.mk install-test-deps$(NC)"; \
	fi

format:
	@echo "$(BLUE)🎨 Formateando código con black...$(NC)"
	@if command -v black >/dev/null 2>&1; then \
		echo "$(CYAN)Formateando código fuente...$(NC)"; \
		black $(SRC_DIR) --line-length 100; \
		echo "$(CYAN)Formateando archivos de prueba...$(NC)"; \
		black $(TESTS_DIR)/test_scanner.py $(TESTS_DIR)/test_compressor.py --line-length 100 2>/dev/null || true; \
		echo "$(GREEN)✅ Código formateado$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  black no encontrado. Instala con: make -f test.mk install-test-deps$(NC)"; \
	fi

check-style:
	@echo "$(BLUE)📏 Verificación completa de estilo...$(NC)"
	@$(MAKE) -f test.mk format
	@$(MAKE) -f test.mk lint
	@echo "$(GREEN)✅ Verificación de estilo completada$(NC)"

quality: check-style test
	@echo "$(PURPLE)🏆 PIPELINE DE CALIDAD COMPLETADO$(NC)"
	@echo "$(GREEN)✅ Código formateado, linting pasado, y pruebas exitosas$(NC)"

# ===========================
# UTILIDADES Y LIMPIEZA
# ===========================

clean-test:
	@echo "$(BLUE)🧹 Limpiando archivos de pruebas...$(NC)"
	find . -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.zip" -delete 2>/dev/null || true
	find . -name "*.gz" -delete 2>/dev/null || true
	find . -name "*.bz2" -delete 2>/dev/null || true
	find . -name "*.enc" -delete 2>/dev/null || true
	rm -rf demo_data/ restored_data/ backup_demo.zip
	rm -rf $(TESTS_DIR)/__pycache__/ 2>/dev/null || true
	@echo "$(GREEN)✅ Archivos de pruebas limpiados$(NC)"

# Verificar que los archivos de prueba existen
check-test-files:
	@echo "$(BLUE)📋 Verificando archivos de prueba...$(NC)"
	@if [ -f "$(TESTS_DIR)/test_scanner.py" ]; then \
		echo "$(GREEN)✅ test_scanner.py encontrado$(NC)"; \
	else \
		echo "$(RED)❌ test_scanner.py no encontrado$(NC)"; \
	fi
	@if [ -f "$(TESTS_DIR)/test_compressor.py" ]; then \
		echo "$(GREEN)✅ test_compressor.py encontrado$(NC)"; \
	else \
		echo "$(RED)❌ test_compressor.py no encontrado$(NC)"; \
	fi
	@if [ -f "run_tests.py" ]; then \
		echo "$(GREEN)✅ run_tests.py encontrado$(NC)"; \
	else \
		echo "$(RED)❌ run_tests.py no encontrado en la raíz$(NC)"; \
	fi

# Información sobre las pruebas disponibles
test-info:
	@echo "$(BLUE)ℹ️  Información de Testing Disponible:$(NC)"
	@echo ""
	@echo "$(YELLOW)📄 Archivos de prueba:$(NC)"
	@if [ -f "$(TESTS_DIR)/test_scanner.py" ]; then \
		echo "  📄 test_scanner.py"; \
		grep -c "def test_" "$(TESTS_DIR)/test_scanner.py" | while read count; do \
			echo "     └─ $$count pruebas de scanner"; \
		done 2>/dev/null || echo "     └─ Archivo encontrado"; \
	else \
		echo "  ❌ test_scanner.py - NO ENCONTRADO"; \
	fi
	@if [ -f "$(TESTS_DIR)/test_compressor.py" ]; then \
		echo "  📄 test_compressor.py"; \
		grep -c "def test_" "$(TESTS_DIR)/test_compressor.py" | while read count; do \
			echo "     └─ $$count pruebas de compressor"; \
		done 2>/dev/null || echo "     └─ Archivo encontrado"; \
	else \
		echo "  ❌ test_compressor.py - NO ENCONTRADO"; \
	fi
	@echo ""
	@echo "$(YELLOW)⚙️  Configuración:$(NC)"
	@echo "  Python: $$($(PYTHON) --version 2>/dev/null || echo 'No encontrado')"
	@echo "  Directorio fuente: $(SRC_DIR)"
	@echo "  Directorio pruebas: $(TESTS_DIR)"

# Ejecución rápida para desarrollo
quick: format lint test
	@echo "$(GREEN)⚡ Verificación rápida completada$(NC)"
	@echo "$(CYAN)✅ Formato aplicado$(NC)"
	@echo "$(CYAN)✅ Linting pasado$(NC)"
	@echo "$(CYAN)✅ Pruebas ejecutadas$(NC)"

# Pipeline de CI simplificado
ci: clean-test check-test-files quality
	@echo "$(GREEN)🚀 Pipeline de CI simplificado completado$(NC)"