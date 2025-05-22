from dask.distributed import Client, LocalCluster
import dask.bag as db
import os
from src.utils import logger

def create_local_cluster(n_workers=4, threads_per_worker=2, memory_limit='4GB'):
    """
    Crea un clúster local de Dask con configuración personalizada
    """
    logger.get_logger().info(f"Creando clúster local con {n_workers} workers")
    
    cluster = LocalCluster(
        n_workers=n_workers,
        threads_per_worker=threads_per_worker,
        memory_limit=memory_limit
    )
    
    client = Client(cluster)
    logger.get_logger().info(f"Clúster Dask iniciado: {client}")
    return client

def process_in_parallel(items, process_function, batch_size=100, workers=4):
    """
    Procesa una lista de elementos en paralelo utilizando Dask
    """
    # Crear cliente
    client = create_local_cluster(n_workers=workers)
    
    try:
        # Dividir la lista en batches para un mejor rendimiento
        batches = [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
        
        # Crear un Dask Bag a partir de los batches
        bag = db.from_sequence(batches)
        
        # Aplicar la función a cada batch
        results = bag.map(lambda batch: [process_function(item) for item in batch]).flatten().compute()
        
        return results
    finally:
        # Cerrar el cliente cuando hayamos terminado
        client.close()

def parallel_file_operation(file_paths, operation_func, chunk_size=1024*1024, workers=4):
    """
    Aplica una operación a múltiples archivos en paralelo,
    dividiendo cada archivo en chunks para procesamiento eficiente
    """
    client = create_local_cluster(n_workers=workers)
    
    try:
        def process_file(file_path):
            """Procesa un archivo en chunks"""
            file_size = os.path.getsize(file_path)
            chunks = []
            
            # Leer el archivo en chunks
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    chunks.append(chunk)
            
            # Procesar cada chunk
            processed_chunks = [operation_func(chunk) for chunk in chunks]
            
            return {
                'file_path': file_path,
                'chunks': processed_chunks
            }
        
        # Crear Dask Bag y procesar archivos
        file_bag = db.from_sequence(file_paths)
        results = file_bag.map(process_file).compute()
        
        return results
    finally:
        client.close()

def get_dashboard_url():
    """
    Retorna la URL del dashboard de Dask si está disponible
    """
    try:
        client = Client.current()
        return client.dashboard_link
    except:
        return None