import unittest
import os
import tempfile
import shutil
from pathlib import Path
import sys

# Añadir el directorio src al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core import scanner
from utils import logger

class TestScanner(unittest.TestCase):
    """
    Pruebas unitarias para el módulo scanner
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
        
        # Crear estructura de archivos de prueba
        self.create_test_structure()
    
    def create_test_structure(self):
        """
        Crea una estructura de directorios y archivos de prueba
        """
        # Directorio principal con archivos
        main_dir = os.path.join(self.test_dir, 'main')
        os.makedirs(main_dir)
        
        # Archivos en directorio principal
        with open(os.path.join(main_dir, 'file1.txt'), 'w') as f:
            f.write('Contenido del archivo 1')
        
        with open(os.path.join(main_dir, 'file2.py'), 'w') as f:
            f.write('print("Hola mundo")')
        
        # Subdirectorio con más archivos
        sub_dir = os.path.join(main_dir, 'subdirectorio')
        os.makedirs(sub_dir)
        
        with open(os.path.join(sub_dir, 'archivo_sub.md'), 'w') as f:
            f.write('# Documentación\nEste es un archivo markdown')
        
        with open(os.path.join(sub_dir, 'datos.json'), 'w') as f:
            f.write('{"nombre": "prueba", "valor": 123}')
        
        # Subdirectorio anidado
        nested_dir = os.path.join(sub_dir, 'anidado')
        os.makedirs(nested_dir)
        
        with open(os.path.join(nested_dir, 'profundo.txt'), 'w') as f:
            f.write('Archivo en directorio anidado')
        
        # Directorio vacío
        empty_dir = os.path.join(self.test_dir, 'vacio')
        os.makedirs(empty_dir)
        
        # Directorio con archivos binarios simulados
        binary_dir = os.path.join(self.test_dir, 'binarios')
        os.makedirs(binary_dir)
        
        with open(os.path.join(binary_dir, 'imagen.jpg'), 'wb') as f:
            f.write(b'\x89PNG\r\n\x1a\n' + b'a' * 1000)  # Simular imagen
        
        with open(os.path.join(binary_dir, 'documento.pdf'), 'wb') as f:
            f.write(b'%PDF-1.4' + b'b' * 2000)  # Simular PDF
    
    def test_scan_single_directory(self):
        """
        Prueba el escaneo de un solo directorio
        """
        main_dir = os.path.join(self.test_dir, 'main')
        files = scanner.scan_directory(main_dir)
        
        # Verificar que se encontraron archivos
        self.assertGreater(len(files), 0, "Debería encontrar archivos en el directorio")
        
        # Verificar que incluye archivos del subdirectorio (escaneo recursivo)
        file_names = [os.path.basename(f) for f in files]
        self.assertIn('file1.txt', file_names)
        self.assertIn('file2.py', file_names)
        self.assertIn('archivo_sub.md', file_names)
        self.assertIn('datos.json', file_names)
        self.assertIn('profundo.txt', file_names)
        
        # Verificar que todos los archivos existen
        for file_path in files:
            self.assertTrue(os.path.isfile(file_path), f"El archivo {file_path} debería existir")
    
    def test_scan_nonexistent_directory(self):
        """
        Prueba el comportamiento al escanear un directorio inexistente
        """
        nonexistent_dir = os.path.join(self.test_dir, 'no_existe')
        files = scanner.scan_directory(nonexistent_dir)
        
        # Debería retornar una lista vacía
        self.assertEqual(len(files), 0, "Directorio inexistente debería retornar lista vacía")
    
    def test_scan_empty_directory(self):
        """
        Prueba el escaneo de un directorio vacío
        """
        empty_dir = os.path.join(self.test_dir, 'vacio')
        files = scanner.scan_directory(empty_dir)
        
        # Debería retornar una lista vacía
        self.assertEqual(len(files), 0, "Directorio vacío debería retornar lista vacía")
    
    def test_scan_multiple_directories_sequential(self):
        """
        Prueba el escaneo de múltiples directorios de forma secuencial
        """
        directories = [
            os.path.join(self.test_dir, 'main'),
            os.path.join(self.test_dir, 'binarios')
        ]
        
        files = scanner.scan_directories(directories, parallel=False)
        
        # Verificar que se encontraron archivos de ambos directorios
        self.assertGreater(len(files), 0, "Debería encontrar archivos en múltiples directorios")
        
        # Verificar que incluye archivos de ambos directorios
        file_names = [os.path.basename(f) for f in files]
        self.assertIn('file1.txt', file_names)  # Del directorio main
        self.assertIn('imagen.jpg', file_names)  # Del directorio binarios
        self.assertIn('documento.pdf', file_names)  # Del directorio binarios
    
    def test_scan_multiple_directories_parallel(self):
        """
        Prueba el escaneo de múltiples directorios de forma paralela con Dask
        """
        directories = [
            os.path.join(self.test_dir, 'main'),
            os.path.join(self.test_dir, 'binarios')
        ]
        
        files = scanner.scan_directories(directories, parallel=True)
        
        # Verificar que se encontraron archivos
        self.assertGreater(len(files), 0, "Debería encontrar archivos con escaneo paralelo")
        
        # Verificar que incluye archivos de ambos directorios
        file_names = [os.path.basename(f) for f in files]
        self.assertIn('file1.txt', file_names)
        self.assertIn('imagen.jpg', file_names)
        
        # Comparar con resultado secuencial para verificar consistencia
        files_sequential = scanner.scan_directories(directories, parallel=False)
        self.assertEqual(
            sorted(files), 
            sorted(files_sequential), 
            "Resultado paralelo debería ser igual al secuencial"
        )
    
    def test_scan_mixed_directories(self):
        """
        Prueba el escaneo con una mezcla de directorios (existentes y no existentes)
        """
        directories = [
            os.path.join(self.test_dir, 'main'),
            os.path.join(self.test_dir, 'no_existe'),
            os.path.join(self.test_dir, 'binarios'),
            os.path.join(self.test_dir, 'vacio')
        ]
        
        files = scanner.scan_directories(directories, parallel=False)
        
        # Debería encontrar archivos solo de los directorios existentes con contenido
        self.assertGreater(len(files), 0, "Debería encontrar archivos de directorios válidos")
        
        # Verificar que no incluye archivos de directorios inexistentes o vacíos
        file_names = [os.path.basename(f) for f in files]
        self.assertIn('file1.txt', file_names)  # Del directorio main
        self.assertIn('imagen.jpg', file_names)  # Del directorio binarios
    
    def test_file_paths_are_absolute(self):
        """
        Prueba que las rutas de archivos retornadas sean absolutas
        """
        main_dir = os.path.join(self.test_dir, 'main')
        files = scanner.scan_directory(main_dir)
        
        for file_path in files:
            self.assertTrue(
                os.path.isabs(file_path), 
                f"La ruta {file_path} debería ser absoluta"
            )
    
    def test_file_count_accuracy(self):
        """
        Prueba que el conteo de archivos sea preciso
        """
        # Contar archivos manualmente
        expected_files = []
        
        # Archivos en main/
        expected_files.extend([
            'file1.txt', 'file2.py', 'archivo_sub.md', 
            'datos.json', 'profundo.txt'
        ])
        
        # Archivos en binarios/
        expected_files.extend(['imagen.jpg', 'documento.pdf'])
        
        # Escanear y comparar
        directories = [
            os.path.join(self.test_dir, 'main'),
            os.path.join(self.test_dir, 'binarios')
        ]
        
        files = scanner.scan_directories(directories)
        file_names = [os.path.basename(f) for f in files]
        
        # Verificar que se encontraron todos los archivos esperados
        for expected_file in expected_files:
            self.assertIn(
                expected_file, 
                file_names, 
                f"Debería encontrar el archivo {expected_file}"
            )
        
        # Verificar el conteo total
        self.assertEqual(
            len(files), 
            len(expected_files), 
            f"Debería encontrar exactamente {len(expected_files)} archivos"
        )
    
    def test_large_directory_structure(self):
        """
        Prueba el rendimiento con una estructura de directorios más grande
        """
        # Crear una estructura más grande para pruebas de rendimiento
        large_dir = os.path.join(self.test_dir, 'grande')
        os.makedirs(large_dir)
        
        # Crear múltiples subdirectorios con archivos
        for i in range(10):
            sub_dir = os.path.join(large_dir, f'subdir_{i}')
            os.makedirs(sub_dir)
            
            for j in range(5):
                file_path = os.path.join(sub_dir, f'archivo_{i}_{j}.txt')
                with open(file_path, 'w') as f:
                    f.write(f'Contenido del archivo {i}-{j}')
        
        # Escanear y verificar
        files = scanner.scan_directory(large_dir)
        
        # Deberíamos tener 10 subdirectorios * 5 archivos = 50 archivos
        self.assertEqual(len(files), 50, "Debería encontrar exactamente 50 archivos")
    
    def test_unicode_filenames(self):
        """
        Prueba el manejo de nombres de archivos con caracteres especiales
        """
        unicode_dir = os.path.join(self.test_dir, 'unicode')
        os.makedirs(unicode_dir)
        
        # Crear archivos con nombres unicode
        unicode_files = ['café.txt', 'niño.py', 'corazón❤️.md', 'español_ñ.json']
        
        for filename in unicode_files:
            try:
                file_path = os.path.join(unicode_dir, filename)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f'Contenido de {filename}')
            except OSError:
                # Saltar si el sistema no soporta el nombre de archivo
                continue
        
        # Escanear
        files = scanner.scan_directory(unicode_dir)
        
        # Verificar que se pueden manejar archivos con nombres unicode
        self.assertGreater(len(files), 0, "Debería manejar archivos con nombres unicode")


if __name__ == '__main__':
    # Configurar y ejecutar las pruebas
    unittest.main(verbosity=2)