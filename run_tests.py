#!/usr/bin/env python3
"""
Script para ejecutar todas las pruebas del sistema de backup
"""

import unittest
import sys
import os
from pathlib import Path

# Añadir el directorio src al path
project_root = Path(__file__).parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

# Importar módulos de prueba
from tests import test_scanner, test_compressor

def run_specific_test(test_module_name):
    """
    Ejecuta un módulo de pruebas específico
    """
    print(f"\n{'='*60}")
    print(f"EJECUTANDO PRUEBAS: {test_module_name}")
    print(f"{'='*60}")
    
    if test_module_name == 'scanner':
        suite = unittest.TestLoader().loadTestsFromModule(test_scanner)
    elif test_module_name == 'compressor':
        suite = unittest.TestLoader().loadTestsFromModule(test_compressor)
    else:
        print(f"Módulo de prueba desconocido: {test_module_name}")
        return False
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_all_tests():
    """
    Ejecuta todas las pruebas disponibles
    """
    print("\n" + "="*80)
    print("INICIANDO SUITE COMPLETA DE PRUEBAS - SISTEMA DE BACKUP SEGURO")
    print("="*80)
    
    # Lista de módulos de prueba
    test_modules = ['scanner', 'compressor']
    results = {}
    
    for module in test_modules:
        success = run_specific_test(module)
        results[module] = success
    
    # Resumen final
    print("\n" + "="*80)
    print("RESUMEN DE RESULTADOS")
    print("="*80)
    
    total_tests = len(test_modules)
    passed_tests = sum(1 for success in results.values() if success)
    
    for module, success in results.items():
        status = "✅ PASÓ" if success else "❌ FALLÓ"
        print(f"{module.capitalize():.<20} {status}")
    
    print(f"\nTotal: {passed_tests}/{total_tests} módulos pasaron todas las pruebas")
    
    if passed_tests == total_tests:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
        return True
    else:
        print(f"\n⚠️  {total_tests - passed_tests} módulo(s) tienen pruebas fallidas")
        return False

def run_performance_tests():
    """
    Ejecuta solo las pruebas de rendimiento
    """
    print("\n" + "="*60)
    print("EJECUTANDO PRUEBAS DE RENDIMIENTO")
    print("="*60)
    
    # Crear suite personalizada con pruebas de rendimiento
    suite = unittest.TestSuite()
    
    # Agregar pruebas específicas de rendimiento
    suite.addTest(test_compressor.TestCompressor('test_parallel_vs_sequential_performance'))
    suite.addTest(test_compressor.TestCompressor('test_large_file_compression'))
    suite.addTest(test_compressor.TestCompressor('test_different_worker_counts'))
    suite.addTest(test_compressor.TestCompressor('test_memory_usage_with_large_files'))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def main():
    """
    Función principal que maneja argumentos de línea de comandos
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Ejecutor de pruebas para Sistema de Backup Seguro')
    parser.add_argument('--module', '-m', 
                       choices=['scanner', 'compressor', 'all'], 
                       default='all',
                       help='Módulo específico a probar (default: all)')
    parser.add_argument('--performance', '-p', 
                       action='store_true',
                       help='Ejecutar solo pruebas de rendimiento')
    parser.add_argument('--verbose', '-v', 
                       action='store_true',
                       help='Salida verbosa')
    
    args = parser.parse_args()
    
    # Configurar verbosidad si se solicita
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    success = True
    
    try:
        if args.performance:
            success = run_performance_tests()
        elif args.module == 'all':
            success = run_all_tests()
        else:
            success = run_specific_test(args.module)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Pruebas interrumpidas por el usuario")
        success = False
    
    except Exception as e:
        print(f"\n\n❌ Error inesperado durante las pruebas: {e}")
        success = False
    
    # Código de salida
    exit_code = 0 if success else 1
    
    if success:
        print(f"\n✅ Pruebas completadas exitosamente")
    else:
        print(f"\n❌ Algunas pruebas fallaron")
    
    sys.exit(exit_code)

if __name__ == '__main__':
    main()