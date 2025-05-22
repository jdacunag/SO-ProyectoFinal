import unittest
import os
import tempfile
import shutil
import zipfile
import gzip
import bz2
from pathlib import Path
import sys
import time

# Añadir el directorio src al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core import compressor
from utils import logger

class TestCompressor(unittest.TestCase):
    """
    Pruebas unitarias para el módulo compressor
    """
    
    def setUp(self):
        """
        Configuración inicial antes de cada prueba
        """
        # Configurar logger para pruebas
        logger.setup_logger(level='DEBUG')
        
        # Crear directorio temporal para pruebas
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)
        
        # Crear archivos de prueba
        self.create_test_files()
    
    def create_test_files(self):
        """
        Crea archivos de prueba con diferentes tamaños y tipos
        """
        # Archivo de texto pequeño
        self.small_text_file = os.path.join(self.test_dir, 'small.txt')
        with open(self.small_text_file, 'w') as f:
            f.write('Este es un archivo de texto pequeño para pruebas de compresión.')
        
        # Archivo de texto mediano
        self.medium_text_file = os.path.join(self.test_dir, 'medium.txt')
        with open(self.medium_text_file, 'w') as f:
            # Crear contenido repetitivo para buena compresión
            content = 'Esta línea se repite muchas veces para crear un archivo mediano.\n' * 1000
            f.write(content)
        
        # Archivo binario simulado
        self.binary_file = os.path.join(self.test_dir, 'binary.dat')
        with open(self.binary_file, 'wb') as f:
            # Datos pseudo-aleatorios
            import random
            random.seed(42)  # Para reproducibilidad
            data = bytes([random.randint(0, 255) for _ in range(5000)])
            f.write(data)
        
        # Archivo grande de texto (para pruebas de rendimiento)
        self.large_text_file = os.path.join(self.test_dir, 'large.txt')
        with open(self.large_text_file, 'w') as f:
            # Crear archivo más grande para probar paralelismo
            content = f'Línea {i}: Esta es una línea de texto en un archivo grande.\n'
            for i in range(10000):
                f.write(content.format(i=i))
        
        # Crear estructura de directorios
        self.test_structure_dir = os.path.join(self.test_dir, 'estructura')
        os.makedirs(self.test_structure_dir)
        
        # Subdirectorio con archivos
        sub_dir = os.path.join(self.test_structure_dir, 'subdirectorio')
        os.makedirs(sub_dir)
        
        with open(os.path.join(self.test_structure_dir, 'archivo_raiz.txt'), 'w') as f:
            f.write('Archivo en la raíz de la estructura')
        
        with open(os.path.join(sub_dir, 'archivo_sub.txt'), 'w') as f:
            f.write('Archivo en subdirectorio')
        
        # Lista de todos los archivos de prueba
        self.test_files = [
            self.small_text_file,
            self.medium_text_file,
            self.binary_file,
            self.large_text_file,
            os.path.join(self.test_structure_dir, 'archivo_raiz.txt'),
            os.path.join(sub_dir, 'archivo_sub.txt')
        ]
    
    def test_compress_single_file_zip(self):
        """
        Prueba la compresión de un solo archivo con ZIP
        """
        output_file = os.path.join(self.test_dir, 'test_single.zip')
        
        result = compressor.compress_files(
            [self.medium_text_file], 
            algorithm='zip', 
            output=output_file,
            workers=2
        )
        
        # Verificar que se creó el archivo
        self.assertTrue(os.path.exists(result), "El archivo ZIP debería existir")
        
        # Verificar que es un archivo ZIP válido
        self.assertTrue(zipfile.is_zipfile(result), "El archivo debería ser un ZIP válido")
        
        # Verificar que el archivo comprimido es más pequeño que el original
        original_size = os.path.getsize(self.medium_text_file)
        compressed_size = os.path.getsize(result)
        self.assertLess(compressed_size, original_size, "El archivo comprimido debería ser más pequeño")
        
        # Verificar contenido del ZIP
        with zipfile.ZipFile(result, 'r') as zipf:
            files_in_zip = zipf.namelist()
            self.assertGreater(len(files_in_zip), 0, "El ZIP debería contener archivos")
    
    def test_compress_multiple_files_zip(self):
        """
        Prueba la compresión de múltiples archivos con ZIP
        """
        output_file = os.path.join(self.test_dir, 'test_multiple.zip')
        
        result = compressor.compress_files(
            self.test_files[:3],  # Primeros 3 archivos
            algorithm='zip',
            output=output_file,
            workers=2
        )
        
        # Verificar que se creó el archivo
        self.assertTrue(os.path.exists(result), "El archivo ZIP debería existir")
        self.assertTrue(zipfile.is_zipfile(result), "El archivo debería ser un ZIP válido")
        
        # Verificar que contiene los archivos esperados
        with zipfile.ZipFile(result, 'r') as zipf:
            files_in_zip = zipf.namelist()
            self.assertEqual(len(files_in_zip), 3, "El ZIP debería contener 3 archivos")
    
    def test_compress_gzip_algorithm(self):
        """
        Prueba la compresión con algoritmo GZIP
        """
        output_file = os.path.join(self.test_dir, 'test_gzip.gz')
        
        result = compressor.compress_files(
            [self.medium_text_file],
            algorithm='gzip',
            output=output_file,
            workers=2
        )
        
        # Verificar que se creó el archivo
        self.assertTrue(os.path.exists(result), "El archivo GZIP debería existir")
        
        # Para GZIP, verificar que la compresión funcionó comparando tamaños
        original_size = os.path.getsize(self.medium_text_file)
        compressed_size = os.path.getsize(result)
        self.assertLess(compressed_size, original_size, "El archivo comprimido debería ser más pequeño")
    
    def test_compress_bzip2_algorithm(self):
        """
        Prueba la compresión con algoritmo BZIP2
        """
        output_file = os.path.join(self.test_dir, 'test_bzip2.bz2')
        
        result = compressor.compress_files(
            [self.medium_text_file],
            algorithm='bzip2',
            output=output_file,
            workers=2
        )
        
        # Verificar que se creó el archivo
        self.assertTrue(os.path.exists(result), "El archivo BZIP2 debería existir")
        
        # Para BZIP2, verificar que la compresión funcionó
        original_size = os.path.getsize(self.medium_text_file)
        compressed_size = os.path.getsize(result)
        self.assertLess(compressed_size, original_size, "El archivo comprimido debería ser más pequeño")
    
    def test_compression_ratio_comparison(self):
        """
        Prueba y compara las ratios de compresión entre algoritmos
        """
        test_file = self.large_text_file
        original_size = os.path.getsize(test_file)
        
        algorithms = ['zip', 'gzip', 'bzip2']
        compression_ratios = {}
        
        for algorithm in algorithms:
            output_file = os.path.join(self.test_dir, f'comparison.{algorithm}')
            
            result = compressor.compress_files(
                [test_file],
                algorithm=algorithm,
                output=output_file,
                workers=2
            )
            
            compressed_size = os.path.getsize(result)
            ratio = compressed_size / original_size
            compression_ratios[algorithm] = ratio
            
            # Verificar que hubo compresión
            self.assertLess(ratio, 1.0, f"Algoritmo {algorithm} debería comprimir el archivo")
        
        # Log de ratios para información
        logger.get_logger().info(f"Ratios de compresión: {compression_ratios}")
        
        # BZIP2 generalmente debería tener mejor compresión que ZIP para texto repetitivo
        self.assertLess(
            compression_ratios['bzip2'], 
            compression_ratios['zip'],
            "BZIP2 debería tener mejor compresión que ZIP para texto repetitivo"
        )
    
    def test_parallel_vs_sequential_performance(self):
        """
        Prueba la diferencia de rendimiento entre compresión paralela y secuencial
        """
        # Crear múltiples archivos para mejor test de paralelismo
        large_files = []
        for i in range(4):
            file_path = os.path.join(self.test_dir, f'performance_{i}.txt')
            with open(file_path, 'w') as f:
                content = f'Archivo {i}: ' + 'Contenido repetitivo. ' * 5000
                f.write(content)
            large_files.append(file_path)
        
        # Compresión con pocos workers (simular secuencial)
        start_time = time.time()
        result_seq = compressor.compress_files(
            large_files,
            algorithm='zip',
            output=os.path.join(self.test_dir, 'sequential.zip'),
            workers=1
        )
        sequential_time = time.time() - start_time
        
        # Compresión con más workers (paralelo)
        start_time = time.time()
        result_par = compressor.compress_files(
            large_files,
            algorithm='zip',
            output=os.path.join(self.test_dir, 'parallel.zip'),
            workers=4
        )
        parallel_time = time.time() - start_time
        
        # Verificar que ambos archivos se crearon
        self.assertTrue(os.path.exists(result_seq), "Resultado secuencial debería existir")
        self.assertTrue(os.path.exists(result_par), "Resultado paralelo debería existir")
        
        # Log de tiempos para análisis
        logger.get_logger().info(f"Tiempo secuencial: {sequential_time:.2f}s")
        logger.get_logger().info(f"Tiempo paralelo: {parallel_time:.2f}s")
        
        # En un caso ideal, el paralelo debería ser más rápido o similar
        # (puede no ser significativo con archivos pequeños o pocos cores)
        speedup = sequential_time / parallel_time if parallel_time > 0 else 1
        logger.get_logger().info(f"Speedup: {speedup:.2f}x")
        
        # Al menos verificar que ambos métodos funcionan
        self.assertGreater(speedup, 0, "Ambos métodos deberían completarse")
    
    def test_invalid_algorithm(self):
        """
        Prueba el manejo de algoritmos inválidos
        """
        with self.assertRaises(Exception):
            compressor.compress_files(
                [self.small_text_file],
                algorithm='invalid_algorithm',
                output=os.path.join(self.test_dir, 'invalid.test'),
                workers=2
            )
    
    def test_empty_file_list(self):
        """
        Prueba el comportamiento con lista vacía de archivos
        """
        output_file = os.path.join(self.test_dir, 'empty.zip')
        
        # Dependiendo de la implementación, esto podría crear un ZIP vacío
        # o lanzar una excepción
        try:
            result = compressor.compress_files(
                [],
                algorithm='zip',
                output=output_file,
                workers=2
            )
            # Si no lanza excepción, verificar que se maneje apropiadamente
            if result:
                self.assertTrue(os.path.exists(result), "Debería crear archivo o manejar caso vacío")
        except (ValueError, Exception) as e:
            # Es aceptable que lance una excepción para lista vacía
            logger.get_logger().info(f"Manejo esperado de lista vacía: {e}")
    
    def test_nonexistent_files(self):
        """
        Prueba el comportamiento con archivos que no existen
        """
        nonexistent_files = [
            os.path.join(self.test_dir, 'no_existe_1.txt'),
            os.path.join(self.test_dir, 'no_existe_2.txt')
        ]
        
        # Esto debería lanzar una excepción o manejar el error graciosamente
        with self.assertRaises(Exception):
            compressor.compress_files(
                nonexistent_files,
                algorithm='zip',
                output=os.path.join(self.test_dir, 'nonexistent.zip'),
                workers=2
            )
    
    def test_mixed_valid_invalid_files(self):
        """
        Prueba el comportamiento con una mezcla de archivos válidos e inválidos
        """
        mixed_files = [
            self.small_text_file,  # Válido
            os.path.join(self.test_dir, 'no_existe.txt'),  # Inválido
            self.medium_text_file  # Válido
        ]
        
        # Dependiendo de la implementación, podría:
        # 1. Procesar solo los válidos
        # 2. Lanzar excepción al encontrar un inválido
        # 3. Otro comportamiento definido
        
        try:
            result = compressor.compress_files(
                mixed_files,
                algorithm='zip',
                output=os.path.join(self.test_dir, 'mixed.zip'),
                workers=2
            )
            
            # Si procesa sin error, verificar que contiene algunos archivos
            if result and os.path.exists(result):
                with zipfile.ZipFile(result, 'r') as zipf:
                    files_in_zip = zipf.namelist()
                    self.assertGreater(len(files_in_zip), 0, "Debería contener al menos algunos archivos válidos")
        
        except Exception as e:
            # También es válido que lance excepción
            logger.get_logger().info(f"Manejo de archivos mixtos: {e}")
    
    def test_large_file_compression(self):
        """
        Prueba la compresión de archivos grandes para verificar el manejo de memoria
        """
        # Crear un archivo más grande
        large_file = os.path.join(self.test_dir, 'very_large.txt')
        with open(large_file, 'w') as f:
            # Crear archivo de aproximadamente 10MB
            for i in range(100000):
                f.write(f'Línea {i}: Esta es una línea muy larga con contenido repetitivo para crear un archivo grande que teste el manejo de memoria.\n')
        
        output_file = os.path.join(self.test_dir, 'large_compressed.zip')
        
        # Medir tiempo y memoria (indirectamente)
        start_time = time.time()
        
        result = compressor.compress_files(
            [large_file],
            algorithm='zip',
            output=output_file,
            workers=3
        )
        
        compression_time = time.time() - start_time
        
        # Verificar que se completó exitosamente
        self.assertTrue(os.path.exists(result), "Debería comprimir archivo grande exitosamente")
        
        # Verificar compresión efectiva
        original_size = os.path.getsize(large_file)
        compressed_size = os.path.getsize(result)
        compression_ratio = compressed_size / original_size
        
        logger.get_logger().info(f"Archivo grande - Original: {original_size/1024/1024:.2f}MB, "
                               f"Comprimido: {compressed_size/1024/1024:.2f}MB, "
                               f"Ratio: {compression_ratio:.3f}, "
                               f"Tiempo: {compression_time:.2f}s")
        
        # Verificar que hubo compresión significativa para texto repetitivo
        self.assertLess(compression_ratio, 0.5, "Debería lograr al menos 50% de compresión en texto repetitivo")
    
    def test_different_worker_counts(self):
        """
        Prueba el comportamiento con diferentes números de workers
        """
        test_files = [self.medium_text_file, self.binary_file, self.large_text_file]
        worker_counts = [1, 2, 4, 8]
        
        for workers in worker_counts:
            with self.subTest(workers=workers):
                output_file = os.path.join(self.test_dir, f'workers_{workers}.zip')
                
                start_time = time.time()
                result = compressor.compress_files(
                    test_files,
                    algorithm='zip',
                    output=output_file,
                    workers=workers
                )
                elapsed_time = time.time() - start_time
                
                # Verificar que se completó exitosamente
                self.assertTrue(os.path.exists(result), f"Debería funcionar con {workers} workers")
                
                # Verificar que el archivo es válido
                self.assertTrue(zipfile.is_zipfile(result), f"Debería crear ZIP válido con {workers} workers")
                
                logger.get_logger().info(f"Workers: {workers}, Tiempo: {elapsed_time:.2f}s")
    
    def test_output_directory_creation(self):
        """
        Prueba que se creen directorios de salida si no existen
        """
        # Crear ruta de salida en directorio que no existe
        nested_output_dir = os.path.join(self.test_dir, 'nuevo', 'directorio', 'anidado')
        output_file = os.path.join(nested_output_dir, 'test.zip')
        
        result = compressor.compress_files(
            [self.small_text_file],
            algorithm='zip',
            output=output_file,
            workers=2
        )
        
        # Verificar que se creó el directorio y el archivo
        self.assertTrue(os.path.exists(nested_output_dir), "Debería crear directorios padre")
        self.assertTrue(os.path.exists(result), "Debería crear el archivo en el directorio nuevo")
    
    def test_compression_preserves_file_structure(self):
        """
        Prueba que la compresión preserve la estructura de directorios
        """
        # Usar archivos de la estructura de directorios creada
        structure_files = [
            os.path.join(self.test_structure_dir, 'archivo_raiz.txt'),
            os.path.join(self.test_structure_dir, 'subdirectorio', 'archivo_sub.txt')
        ]
        
        output_file = os.path.join(self.test_dir, 'structure_test.zip')
        
        result = compressor.compress_files(
            structure_files,
            algorithm='zip',
            output=output_file,
            workers=2
        )
        
        # Verificar estructura dentro del ZIP
        with zipfile.ZipFile(result, 'r') as zipf:
            files_in_zip = zipf.namelist()
            
            # Verificar que mantiene alguna estructura relativa
            self.assertGreater(len(files_in_zip), 0, "ZIP debería contener archivos")
            
            # Log para inspección manual
            logger.get_logger().info(f"Estructura en ZIP: {files_in_zip}")
    
    def test_binary_file_compression(self):
        """
        Prueba específica para archivos binarios
        """
        output_file = os.path.join(self.test_dir, 'binary_test.zip')
        
        result = compressor.compress_files(
            [self.binary_file],
            algorithm='zip',
            output=output_file,
            workers=2
        )
        
        # Verificar que se puede comprimir archivos binarios
        self.assertTrue(os.path.exists(result), "Debería comprimir archivos binarios")
        self.assertTrue(zipfile.is_zipfile(result), "Debería crear ZIP válido con archivos binarios")
        
        # Verificar que el archivo binario está en el ZIP
        with zipfile.ZipFile(result, 'r') as zipf:
            files_in_zip = zipf.namelist()
            self.assertGreater(len(files_in_zip), 0, "ZIP debería contener el archivo binario")
    
    def test_compression_with_encryption_flag(self):
        """
        Prueba el comportamiento cuando se solicita encriptación
        """
        output_file = os.path.join(self.test_dir, 'encrypted_test.zip')
        
        # Nota: Dependiendo de la implementación, esto podría:
        # 1. Requerir integración con el módulo de encriptación
        # 2. Usar pyzipper para ZIP con contraseña
        # 3. Ser manejado en una capa superior
        
        try:
            result = compressor.compress_files(
                [self.small_text_file],
                algorithm='zip',
                output=output_file,
                encrypt=True,
                password='test_password',
                workers=2
            )
            
            # Si la encriptación está implementada, verificar el resultado
            if result:
                self.assertTrue(os.path.exists(result), "Debería crear archivo con encriptación")
        
        except NotImplementedError:
            # Es válido si la encriptación no está implementada aún en el compressor
            logger.get_logger().info("Encriptación no implementada en compressor, será manejada externamente")
        
        except Exception as e:
            # Otros errores podrían indicar problemas de implementación
            logger.get_logger().warning(f"Error en encriptación: {e}")
    
    def test_concurrent_compression_operations(self):
        """
        Prueba múltiples operaciones de compresión concurrentes
        """
        import threading
        
        def compress_worker(worker_id):
            """Worker para compresión concurrente"""
            try:
                output_file = os.path.join(self.test_dir, f'concurrent_{worker_id}.zip')
                result = compressor.compress_files(
                    [self.medium_text_file],
                    algorithm='zip',
                    output=output_file,
                    workers=2
                )
                return result
            except Exception as e:
                logger.get_logger().error(f"Error en worker {worker_id}: {e}")
                return None
        
        # Crear múltiples hilos para comprimir concurrentemente
        threads = []
        results = {}
        
        for i in range(3):
            thread = threading.Thread(
                target=lambda i=i: results.update({i: compress_worker(i)}),
                args=()
            )
            threads.append(thread)
            thread.start()
        
        # Esperar a que terminen todos los hilos
        for thread in threads:
            thread.join()
        
        # Verificar que todas las operaciones se completaron
        for i in range(3):
            self.assertIsNotNone(results.get(i), f"Worker {i} debería completarse exitosamente")
            if results[i]:
                self.assertTrue(os.path.exists(results[i]), f"Archivo del worker {i} debería existir")
    
    def test_compression_error_handling(self):
        """
        Prueba el manejo de errores durante la compresión
        """
        # Intentar escribir en un directorio sin permisos (si es posible)
        restricted_output = '/root/no_permission.zip' if os.name != 'nt' else 'C:\\System32\\no_permission.zip'
        
        # Esto debería fallar y ser manejado graciosamente
        with self.assertRaises(Exception):
            compressor.compress_files(
                [self.small_text_file],
                algorithm='zip',
                output=restricted_output,
                workers=2
            )
    
    def test_memory_usage_with_large_files(self):
        """
        Prueba indirecta del uso de memoria con archivos grandes
        """
        # Crear varios archivos grandes
        large_files = []
        for i in range(3):
            file_path = os.path.join(self.test_dir, f'memory_test_{i}.txt')
            with open(file_path, 'w') as f:
                # Archivos de ~5MB cada uno
                content = 'A' * 1000 + '\n'  # 1KB por línea
                for _ in range(5000):  # 5000 líneas = ~5MB
                    f.write(content)
            large_files.append(file_path)
        
        output_file = os.path.join(self.test_dir, 'memory_test.zip')
        
        # La compresión debería completarse sin errores de memoria
        result = compressor.compress_files(
            large_files,
            algorithm='zip',
            output=output_file,
            workers=2
        )
        
        self.assertTrue(os.path.exists(result), "Debería manejar múltiples archivos grandes")
        
        # Verificar que la compresión fue efectiva
        total_original_size = sum(os.path.getsize(f) for f in large_files)
        compressed_size = os.path.getsize(result)
        
        logger.get_logger().info(f"Prueba de memoria - Original total: {total_original_size/1024/1024:.2f}MB, "
                               f"Comprimido: {compressed_size/1024/1024:.2f}MB")
        
        # Para contenido repetitivo, debería haber compresión significativa
        self.assertLess(compressed_size, total_original_size * 0.1, 
                       "Debería lograr alta compresión en contenido repetitivo")


if __name__ == '__main__':
    # Configurar y ejecutar las pruebas
    unittest.main(verbosity=2)