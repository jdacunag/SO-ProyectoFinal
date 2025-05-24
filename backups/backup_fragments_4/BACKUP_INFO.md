# Información del Backup - Sistema de Backup Seguro

## Detalles del Backup
- **Fecha y hora:** 2025-05-24 13:27:36
- **Directorios respaldados:** 1
- **Algoritmo de compresión:** ZIP
- **Modo de almacenamiento:** fragments
- **Encriptación:** No

## Directorios Incluidos
1. **test_data/docs**
   - Ruta completa: `/home/jdacunag/soperativos/SO-ProyectoFinal/SO-ProyectoFinal/test_data/docs`
   - Archivos: 2
   - Tamaño: 0.00 MB

## Configuración de Fragmentación
- **Tamaño por fragmento:** 500 MB
- **Uso recomendado:** Copiar cada fragmento a un USB diferente
- **Para reconstruir:** Ejecutar `rebuild.py` en este directorio

## Comandos de Restauración

### Para archivos locales:
```bash
python -m src.main restore -i ARCHIVO_BACKUP -o ./restaurado
```

### Para archivos encriptados:
```bash
python -m src.main restore -i ARCHIVO_BACKUP.enc -o ./restaurado --password TU_PASSWORD
```

### Para fragmentos:
```bash
# Ir al directorio de fragmentos y ejecutar:
python rebuild.py
```

## Notas
- Este backup fue creado con el Sistema de Backup Seguro v1.0
- Guarda este archivo junto con tu backup para referencia futura
- Para fragmentos: todos los archivos .part### son necesarios para la reconstrucción
