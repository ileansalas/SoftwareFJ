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


# =============================================================================
# ABSTRACCIÓN + HERENCIA + POLIMORFISMO: Servicios
# =============================================================================
class Servicio(EntidadSistema):
    """Clase abstracta de servicios; centraliza disponibilidad y cálculo de costos."""

    DURACION_MIN = 1  # Duración mínima por defecto (las subclases la sobrescriben)
    DURACION_MAX = 24  # Duración máxima por defecto (las subclases la sobrescriben)

    def __init__(self, id_servicio=None, nombre=None, tarifa_hora=None) -> None:
        """Construye el servicio validando id, nombre y tarifa."""
        self._id = _requerido(id_servicio, "id_servicio")  # Identificador obligatorio
        self._nombre = _requerido(nombre, "nombre")  # Nombre obligatorio
        tarifa = _requerido(tarifa_hora, "tarifa_hora")  # Tarifa obligatoria
        # La tarifa debe ser número (no bool) y mayor que cero
        if not isinstance(tarifa, (int, float)) or isinstance(tarifa, bool) or tarifa <= 0:
            raise DatosInvalidosError(f"Tarifa por hora inválida: {tarifa!r}.")
        self._tarifa_hora = float(tarifa)  # Se guarda como decimal
        self._disponible = True  # Todo servicio nace disponible

    @property
    def identificador(self) -> str:
        """Id del servicio."""
        return str(self._id)

    @property
    def nombre(self) -> str:
        """Nombre del servicio."""
        return self._nombre

    @property
    def tarifa_hora(self) -> float:
        """Tarifa por hora del servicio."""
        return self._tarifa_hora

    @property
    def disponible(self) -> bool:
        """Indica si el servicio puede reservarse."""
        return self._disponible

    def ocupar(self) -> None:
        """Marca el servicio como no disponible; falla si ya estaba ocupado."""
        if not self._disponible:  # Ya estaba ocupado: no se puede volver a ocupar
            raise ServicioNoDisponibleError(f"El servicio {self._id} ya está ocupado.")
        self._disponible = False  # Pasa a no disponible

    def liberar(self) -> None:
        """Marca el servicio como disponible nuevamente."""
        self._disponible = True

    @abstractmethod
    def validar_parametros(self, duracion) -> None:
        """Valida la duración y los parámetros propios del servicio (obligatorio en hijas)."""

    @abstractmethod
    def describir(self) -> str:
        """Descripción detallada del servicio (obligatorio en hijas)."""

    def _validar_duracion(self, duracion) -> None:
        """Valida que la duración sea numérica y esté dentro del rango del servicio."""
        # Debe ser número y no booleano (True/False son int en Python)
        if isinstance(duracion, bool) or not isinstance(duracion, (int, float)):
            raise DatosInvalidosError(f"Duración no numérica: {duracion!r}.")
        # Debe estar entre el mínimo y el máximo de la clase concreta (polimorfismo de atributos)
        if not (self.DURACION_MIN <= duracion <= self.DURACION_MAX):
            raise DatosInvalidosError(
                f"Duración {duracion}h fuera de rango "
                f"({self.DURACION_MIN}-{self.DURACION_MAX}h) para {self._nombre}."
            )

    def calcular_costo(self, duracion=None, impuesto=0.19, descuento=0.0, recargo_extra=0.0) -> float:
        """Calcula el costo total. Los parámetros opcionales dan la "sobrecarga" de métodos.

        Variantes de uso:
            calcular_costo(3)                                  -> solo duración (IVA 19 %)
            calcular_costo(3, descuento=0.10)                  -> con descuento
            calcular_costo(3, impuesto=0.0, recargo_extra=2e4) -> sin impuesto y con recargo
        """
        if duracion is None:  # Si no se indica duración...
            duracion = self.DURACION_MIN  # ...se usa la mínima del servicio
        self.validar_parametros(duracion)  # Polimorfismo: cada subclase valida a su manera
        if not 0 <= descuento < 1:  # El descuento debe ser 0 % <= d < 100 %
            raise CalculoInconsistenteError(f"Descuento fuera de rango: {descuento}.")
        if not 0 <= impuesto <= 1:  # El impuesto debe estar entre 0 % y 100 %
            raise CalculoInconsistenteError(f"Impuesto fuera de rango: {impuesto}.")
        if recargo_extra < 0:  # Un recargo no puede ser negativo
            raise CalculoInconsistenteError(f"Recargo negativo: {recargo_extra}.")
        subtotal = self._tarifa_hora * duracion + recargo_extra  # Tarifa x horas + recargo
        con_descuento = subtotal * (1 - descuento)  # Se aplica el descuento
        total = con_descuento * (1 + impuesto)  # Se aplica el impuesto
        if total < 0:  # Verificación final de coherencia
            raise CalculoInconsistenteError("El costo total resultó negativo.")
        return round(total, 2)  # Se redondea a 2 decimales

    def resumen(self) -> str:
        """Resumen común: descripción + tarifa + estado de disponibilidad."""
        estado = "disponible" if self._disponible else "ocupado"  # Texto del estado
        return f"{self.describir()} | ${self._tarifa_hora:,.0f}/h | {estado}"


