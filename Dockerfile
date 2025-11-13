# Usa una imagen base oficial de Python.
# La etiqueta 'slim' es una buena opción para mantener un tamaño de imagen reducido.
FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor.
WORKDIR /app

# Establece variables de entorno para asegurar que la salida de Python se muestre en la terminal.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala las dependencias del depurador para VS Code y JetBrains.
# Esto permite la depuración remota desde tu IDE.
RUN pip install --no-cache-dir debugpy==1.8.1 

# Copia el archivo de dependencias y las instala.
# Se copia por separado para aprovechar el almacenamiento en caché de capas de Docker.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de tu aplicación al directorio de trabajo.
COPY ./src ./src

# Expone el puerto estándar para la depuración remota.
EXPOSE 5678

# Comando por defecto para ejecutar la aplicación.
# Este comando será sobreescrito por docker-compose para iniciar en modo de depuración.
CMD ["python", "src/photo_sorter/main.py"]