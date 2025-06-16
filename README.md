# keyHm
Una aplicación de escritorio simple para Ubuntu que te permite crear y gestionar atajos de teclado personalizados para ejecutar comandos de terminal.

## Características

- **Interfaz Gráfica Simple:** Añade, edita y elimina atajos de teclado fácilmente.
- **Ejecución en Segundo Plano:** Los atajos funcionan globalmente en todo el sistema, incluso si la ventana de la aplicación está cerrada.
- **Configuración Persistente:** Tus atajos se guardan en un archivo `key_bindings.json` y se cargan automáticamente al iniciar la aplicación.

## Requisitos Previos

Necesitarás tener Python 3 y `pip` instalados en tu sistema Ubuntu.

- **Instalar Tkinter (si no está disponible):**
  ```bash
  sudo apt-get update
  sudo apt-get install python3-tk
