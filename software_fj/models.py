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


