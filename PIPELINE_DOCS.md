
# Documentación del Pipeline de CI/CD

Este documento detalla el pipeline de Integración Continua y Despliegue Continuo (CI/CD) configurado para este proyecto a través de GitHub Actions.

## 1. Descripción General
Es es el pipeline del proyecto Banana

## 2. Detalle de los Trabajos (Jobs)

El pipeline consta de dos trabajos secuenciales: `build-and-test` y `deploy`.

### Job: `build-and-test`

Este trabajo es el responsable de verificar la integridad y calidad del código.

-   **Disparadores**: Se ejecuta en cada `push` o `pull_request` dirigido a la rama `main`.
-   **Entorno**: Se ejecuta en un contenedor de `ubuntu-latest` con Python `3.12`.
-   **Pasos**:
    1.  **Checkout repository**: Descarga la última versión del código del repositorio.
    2.  **Set up Python**: Configura el entorno de ejecución con la versión de Python especificada (`3.12`).
    3.  **Install dependencies**: Instala todas las librerías y paquetes necesarios para el proyecto, listados en el archivo `requirements.txt`.
    4.  **Run unit tests**: Ejecuta el conjunto de pruebas unitarias utilizando el descubridor de `unittest` de Python. Busca y corre todos los tests ubicados en el directorio `src/photo_sorter`. Si alguna prueba falla, el pipeline se detiene aquí.

### Job: `deploy`

Este trabajo se encarga de desplegar la aplicación en el servidor de destino.

-   **Dependencia**: Solo se ejecuta si el trabajo `build-and-test` ha finalizado con éxito (`needs: build-and-test`).
-   **Condición de Ejecución**: Para evitar despliegues no deseados, este trabajo **solo se ejecuta si se cumplen dos condiciones**:
    1.  El evento que activó el pipeline fue un `push` a la rama `main`.
    2.  El trabajo `build-and-test` fue exitoso.
-   **Pasos**:
    1.  **Checkout repository**: Descarga nuevamente el código del repositorio.
    2.  **Deploy to server**: Utiliza la acción `appleboy/scp-action` para copiar de forma segura los archivos de la aplicación al servidor remoto.
        -   **Fuente (`source`)**: Copia el contenido del directorio `src/`.
        -   **Destino (`target`)**: El directorio en el servidor donde se desplegará la aplicación.
        -   **Autenticación**: Usa claves SSH para una conexión segura.

## 3. Requerimientos de Configuración

Para que el pipeline funcione correctamente, especialmente la parte de despliegue, es necesario configurar los siguientes "Secrets" en el repositorio de GitHub.

### Secrets Requeridos

Estos valores son sensibles y deben ser almacenados de forma segura.

-   `SSH_HOST`: La dirección IP o el nombre de dominio del servidor de despliegue.
-   `SSH_USER`: El nombre de usuario para conectarse al servidor vía SSH.
-   `SSH_KEY`: La clave privada SSH utilizada para la autenticación. La clave pública correspondiente debe estar en el archivo `~/.ssh/authorized_keys` del usuario en el servidor.
-   `TARGET_DIR`: La ruta absoluta en el servidor donde se deben copiar los archivos de la aplicación (ej: `/home/user/my-app`).

### ¿Cómo configurar los Secrets?

1.  Ve a tu repositorio en GitHub.
2.  Haz clic en la pestaña **Settings**.
3.  En el menú de la izquierda, navega a **Secrets and variables > Actions**.
4.  Haz clic en el botón **New repository secret** para cada uno de los secrets listados arriba y añade sus valores correspondientes.

## 4. Instrucciones de Operación

El pipeline está diseñado para integrarse de forma natural en el flujo de trabajo de desarrollo.

-   **Para ejecutar solo las pruebas**:
    -   Crea una nueva rama para tus cambios.
    -   Cuando estés listo, abre un `Pull Request` apuntando a la rama `main`.
    -   El job `build-and-test` se ejecutará automáticamente. Podrás ver el resultado en la pestaña "Checks" del Pull Request.

-   **Para desplegar la aplicación**:
    -   Una vez que el Pull Request ha sido revisado y las pruebas pasan, haz `merge` a la rama `main`.
    -   El `merge` crea un `push` a `main`, lo que activará el pipeline completo.
    -   Primero se ejecutarán las pruebas (`build-and-test`) y, si tienen éxito, se procederá con el despliegue (`deploy`).
