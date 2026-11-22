"""models.py - Entidades del dominio: Cliente, Servicios (3 tipos) y Reserva."""
import re  # Módulo de expresiones regulares: se usa para validar el formato del correo
from abc import ABC, abstractmethod  # ABC = clase base abstracta; abstractmethod = método sin implementar
from enum import Enum  # Para definir el conjunto cerrado de estados de una reserva

# Importamos las excepciones propias que usarán las validaciones
from software_fj.exceptions import (
    CalculoInconsistenteError,
    DatosInvalidosError,
    OperacionNoPermitidaError,
    ParametrosFaltantesError,
    ReservaInvalidaError,
    ServicioNoDisponibleError,
)

# Patrón de correo: texto@dominio.extensión (permite letras, números, ., +, - y _)
PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")


def _requerido(valor, nombre: str):
    """Verifica que un parámetro obligatorio exista; si no, lanza ParametrosFaltantesError."""
    # Es "faltante" si es None o si es un texto vacío/solo espacios
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        raise ParametrosFaltantesError(f"Falta el parámetro obligatorio '{nombre}'.")
    return valor  # Si está bien, se devuelve el mismo valor para poder encadenar la asignación


# =============================================================================
# ABSTRACCIÓN: entidad general del sistema
# =============================================================================
class EntidadSistema(ABC):
    """Clase abstracta que representa cualquier entidad identificable del sistema."""

    @property
    @abstractmethod
    def identificador(self) -> str:
        """Identificador único de la entidad (las hijas deben implementarlo)."""

    @abstractmethod
    def resumen(self) -> str:
        """Texto breve que describe la entidad (las hijas deben implementarlo)."""

    def __str__(self) -> str:
        """Al convertir la entidad a texto (print/str) se muestra su resumen."""
        return self.resumen()  # Polimorfismo: cada subclase aporta su propio resumen


# =============================================================================
# ENCAPSULACIÓN: Cliente
# =============================================================================
class Cliente(EntidadSistema):
    """Cliente con atributos privados y validaciones estrictas en sus setters."""

    def __init__(self, id_cliente=None, nombre=None, correo=None, telefono=None) -> None:
        """Construye el cliente validando cada dato recibido."""
        self.__id = _requerido(id_cliente, "id_cliente")  # Atributo privado: el id no tiene setter
        self.nombre = nombre  # Usa el setter de nombre (valida)
        self.correo = correo  # Usa el setter de correo (valida con regex)
        self.telefono = telefono  # Usa el setter de teléfono (valida)

    @property
    def identificador(self) -> str:
        """Devuelve el id del cliente (solo lectura)."""
        return str(self.__id)

    @property
    def nombre(self) -> str:
        """Devuelve el nombre del cliente."""
        return self.__nombre

    @nombre.setter
    def nombre(self, valor) -> None:
        """Asigna el nombre; exige mínimo 3 caracteres."""
        valor = _requerido(valor, "nombre")  # Debe existir y no estar vacío
        if len(str(valor).strip()) < 3:  # Regla: mínimo 3 caracteres
            raise DatosInvalidosError(f"Nombre demasiado corto: '{valor}'.")
        self.__nombre = str(valor).strip()  # Guarda el nombre sin espacios sobrantes

    @property
    def correo(self) -> str:
        """Devuelve el correo del cliente."""
        return self.__correo

    @correo.setter
    def correo(self, valor) -> None:
        """Asigna el correo; exige formato válido según la expresión regular."""
        valor = _requerido(valor, "correo")  # Debe existir
        if not PATRON_CORREO.match(str(valor).strip()):  # Compara con el patrón de correo
            raise DatosInvalidosError(f"Correo con formato inválido: '{valor}'.")
        self.__correo = str(valor).strip().lower()  # Se normaliza a minúsculas

    @property
    def telefono(self) -> str:
        """Devuelve el teléfono del cliente."""
        return self.__telefono

    @telefono.setter
    def telefono(self, valor) -> None:
        """Asigna el teléfono; debe ser numérico y de al menos 7 dígitos."""
        valor = _requerido(valor, "telefono")  # Debe existir
        texto = str(valor).strip()  # Se trabaja como texto sin espacios
        if not (texto.isdigit() and len(texto) >= 7):  # Solo dígitos y largo mínimo 7
            raise DatosInvalidosError(f"Teléfono inválido: '{valor}'.")
        self.__telefono = texto  # Guarda el teléfono validado

    def resumen(self) -> str:
        """Descripción corta del cliente."""
        return f"Cliente[{self.identificador}] {self.nombre} <{self.correo}> Tel:{self.telefono}"


