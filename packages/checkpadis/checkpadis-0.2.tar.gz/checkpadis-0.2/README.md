# Prototipo Funcional

Este prototipo tiene como objetivo principal probar distintas funcionalidades relacionadas con la creación y ejecución de comandos de entrada, llamadas HTTP, y la interacción con repositorios de GitHub. A continuación, se detallan los objetivos específicos y los pasos a seguir para cada uno de ellos.

## Objetivos

1. **Probar las entradas y que me devuelva una salida con consola y con color de manera local.**
2. **Probar llamadas HTTP y que salga por consola un resultado.**
3. **Ejecutar un comando que vaya a buscar a un repo de GitHub otro archivo Python donde haya una función a ejecutar (un ping, que devuelva pong).**
4. **Subir una librería en Python.**
5. **Bajar una librería en Codespaces y ejecutar las pruebas anteriores.**

## Funciones Utilizadas

### Base64

#### `base64.b64decode(s)`

- **Descripción**: Decodifica una cadena codificada en base64.
- **Uso en el Prototipo**: Decodifica el contenido del archivo descargado desde GitHub antes de guardarlo localmente.
- **Ejemplo**:

  ```python
  import base64

  encoded_string = 'ZGVmIHBpbmcoKToKICAgIHJldHVybiAicG9uZyIK'
  decoded_bytes = base64.b64decode(encoded_string)
  decoded_string = decoded_bytes.decode('utf-8')
  print(decoded_string)
  ```

## tempfile

### `tempfile.TemporaryDirectory()`

- **Descripción**: Crea un directorio temporal que se puede usar para almacenar archivos de manera temporal durante la ejecución del script. El directorio y su contenido se eliminan automáticamente cuando se sale del bloque `with`.
- **Uso en el Prototipo**: Se utiliza para crear un espacio temporal seguro donde se pueden descargar o crear archivos necesarios durante la ejecución del script. Esto asegura que los archivos temporales no queden en el sistema después de su uso.

#### Ejemplo de Uso

```python
import tempfile

# Crear un directorio temporal
with tempfile.TemporaryDirectory() as temp_dir:
    print(f"Directorio temporal creado: {temp_dir}")
    # Puedes realizar operaciones con el directorio temporal aquí

# El directorio y su contenido se eliminan automáticamente al salir del bloque
```
