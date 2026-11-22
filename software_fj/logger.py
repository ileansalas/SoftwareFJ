"""logger.py - Registro de eventos y errores en un archivo de texto plano."""
from datetime import datetime  # Para generar la marca de tiempo de cada línea del log
from pathlib import Path  # Para construir rutas de archivos de forma portable (Windows/Linux/Mac)

# Carpeta raíz del proyecto: dos niveles arriba de este archivo (software_fj/logger.py -> raíz)
RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
# Ruta por defecto del único archivo que maneja el sistema: logs/software_fj_eventos.log
ARCHIVO_LOG = RAIZ_PROYECTO / "logs" / "software_fj_eventos.log"


class RegistroEventos:
    """Escribe eventos y excepciones (con su causa encadenada) en el archivo .log."""

    def __init__(self, ruta: Path = ARCHIVO_LOG) -> None:
        """Guarda la ruta del log y garantiza que la carpeta `logs/` exista."""
        self.__ruta = Path(ruta)  # Atributo privado: ruta del archivo de log
        try:
            self.__ruta.parent.mkdir(parents=True, exist_ok=True)  # Crea la carpeta si no existe
        except OSError as error:  # Si no se puede crear, no se detiene el programa
            print(f"[AVISO] No se pudo crear la carpeta de logs: {error}")

    def __escribir(self, nivel: str, mensaje: str) -> None:
        """Agrega una línea al log; garantiza el cierre del archivo con try/finally."""
        marca = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Fecha y hora actuales formateadas
        archivo = None  # Se inicializa en None para poder consultarlo dentro de finally
        try:
            archivo = open(self.__ruta, "a", encoding="utf-8")  # Abre en modo "append" (agregar al final)
            archivo.write(f"{marca} | {nivel:<7} | {mensaje}\n")  # Escribe: marca | nivel | mensaje
        except OSError as error:  # Error de disco, permisos, etc.
            # Un fallo del log nunca debe detener el programa: solo se avisa por consola
            print(f"[AVISO] No se pudo escribir en el log: {error}")
        finally:  # Este bloque se ejecuta SIEMPRE, haya o no error
            if archivo is not None:  # Si el archivo llegó a abrirse...
                archivo.close()  # ...se cierra de forma segura

    def info(self, mensaje: str) -> None:
        """Registra un evento informativo (operación exitosa, inicio, fin...)."""
        self.__escribir("INFO", mensaje)  # Delegamos en el método privado con nivel INFO

    def error(self, mensaje: str) -> None:
        """Registra un error simple sin excepción asociada."""
        self.__escribir("ERROR", mensaje)  # Nivel ERROR

    def excepcion(self, contexto: str, error: BaseException) -> None:
        """Registra una excepción y, si existe, toda su cadena de causas (__cause__)."""
        # Línea principal: contexto + nombre de la clase de la excepción + su mensaje
        self.__escribir("ERROR", f"{contexto} -> {type(error).__name__}: {error}")
        causa = error.__cause__  # Excepción original asignada con `raise ... from ...`
        while causa is not None:  # Recorre toda la cadena (una causa puede tener otra causa)
            self.__escribir("CAUSA", f"{type(causa).__name__}: {causa}")  # Una línea por causa
            causa = causa.__cause__  # Avanza a la siguiente causa de la cadena
