"""
Encryptor - Módulo para encriptación AES-256 con paralelismo
"""

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import os
import dask.bag as db
from src.utils import logger

def generate_key(password, salt=None):
    """Genera una clave a partir de la contraseña utilizando PBKDF2"""
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # 32 bytes = 256 bits para AES-256
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    
    key = kdf.derive(password.encode())
    return key, salt

def encrypt_chunk(data_chunk, key):
    """Encripta un chunk de datos usando AES-256"""
    iv = os.urandom(16)  # Initialization vector
    
    # Preparar el padding
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data_chunk) + padder.finalize()
    
    # Crear cifrador
    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    
    # Encriptar
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    
    # Devolver IV + datos encriptados
    return iv + encrypted_data

def decrypt_chunk(encrypted_chunk, key):
    """Desencripta un chunk de datos usando AES-256"""
    # Extraer IV (primeros 16 bytes)
    iv = encrypted_chunk[:16]
    encrypted_data = encrypted_chunk[16:]
    
    # Crear descifrador
    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )
    decryptor = cipher.decryptor()
    
    # Desencriptar
    padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
    
    # Quitar padding
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()
    
    return data

def encrypt_file(file_path, output_path, password, chunk_size=1024*1024, workers=4):
    """
    Encripta un archivo utilizando AES-256 con paralelización de Dask
    """
    logger.get_logger().info(f"Encriptando archivo: {file_path}")
    
    # Generar clave a partir de contraseña
    key, salt = generate_key(password)
    
    # Leer archivo en chunks
    chunks = []
    
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            chunks.append(chunk)
    
    # Encriptar chunks en paralelo
    try:
        chunks_bag = db.from_sequence(chunks)
        encrypted_chunks = chunks_bag.map(lambda chunk: encrypt_chunk(chunk, key)).compute()
    except:
        # Fallback secuencial
        logger.get_logger().warning("Error con Dask, encriptando secuencialmente")
        encrypted_chunks = [encrypt_chunk(chunk, key) for chunk in chunks]
    
    # Escribir archivo encriptado
    # Formato: salt(16) + encrypted_chunk1 + encrypted_chunk2 + ...
    with open(output_path, 'wb') as f:
        f.write(salt)  # Guardar salt al inicio
        for chunk in encrypted_chunks:
            f.write(chunk)
    
    logger.get_logger().info(f"Archivo encriptado guardado en: {output_path}")
    return output_path

def decrypt_file(encrypted_path, output_path, password, chunk_size=1024*1024, workers=4):
    """
    Desencripta un archivo utilizando AES-256 con paralelización de Dask
    """
    logger.get_logger().info(f"Desencriptando archivo: {encrypted_path}")
    
    # Leer salt (primeros 16 bytes)
    with open(encrypted_path, 'rb') as f:
        salt = f.read(16)
    
    # Regenerar clave a partir de contraseña y salt
    key, _ = generate_key(password, salt)
    
    # Leer archivo en chunks (saltando los primeros 16 bytes de salt)
    encrypted_chunks = []
    with open(encrypted_path, 'rb') as f:
        f.seek(16)  # Saltar salt
        while True:
            chunk = f.read(chunk_size + 16 + 16)  # Tamaño + IV + posible padding
            if not chunk:
                break
            encrypted_chunks.append(chunk)
    
    # Desencriptar chunks en paralelo
    try:
        chunks_bag = db.from_sequence(encrypted_chunks)
        decrypted_chunks = chunks_bag.map(lambda chunk: decrypt_chunk(chunk, key)).compute()
    except:
        # Fallback secuencial
        logger.get_logger().warning("Error con Dask, desencriptando secuencialmente")
        decrypted_chunks = [decrypt_chunk(chunk, key) for chunk in encrypted_chunks]
    
    # Escribir archivo desencriptado
    with open(output_path, 'wb') as f:
        for chunk in decrypted_chunks:
            f.write(chunk)
    
    logger.get_logger().info(f"Archivo desencriptado guardado en: {output_path}")
    return output_path