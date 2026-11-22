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


class ReservaSala(Servicio):
    """Servicio de reserva de salas: duración 1-12 h e incluye capacidad."""

    DURACION_MIN, DURACION_MAX = 1, 12  # Rango propio de las salas

    def __init__(self, id_servicio=None, nombre=None, tarifa_hora=None, capacidad=None) -> None:
        """Construye la sala; valida además la capacidad."""
        super().__init__(id_servicio, nombre, tarifa_hora)  # Valida los datos comunes
        capacidad = _requerido(capacidad, "capacidad")  # La capacidad es obligatoria
        # Debe ser entero positivo (y no booleano)
        if not isinstance(capacidad, int) or isinstance(capacidad, bool) or capacidad <= 0:
            raise DatosInvalidosError(f"Capacidad inválida: {capacidad!r}.")
        self._capacidad = capacidad  # Número de personas que caben

    def validar_parametros(self, duracion) -> None:
        """Valida la duración contra el rango de salas (1-12 h)."""
        self._validar_duracion(duracion)

    def describir(self) -> str:
        """Descripción específica de una sala."""
        return f"Sala '{self._nombre}' [{self._id}] para {self._capacidad} personas"


class AlquilerEquipo(Servicio):
    """Servicio de alquiler de equipos: 2-72 h, con gama y seguro obligatorio."""

    DURACION_MIN, DURACION_MAX = 2, 72  # Rango propio de equipos
    GAMAS = ("BASICA", "MEDIA", "ALTA")  # Gamas permitidas
    PORCENTAJE_SEGURO = 0.05  # El seguro obligatorio es el 5 % del costo base

    def __init__(self, id_servicio=None, nombre=None, tarifa_hora=None, gama=None) -> None:
        """Construye el equipo; valida además la gama."""
        super().__init__(id_servicio, nombre, tarifa_hora)  # Datos comunes
        gama = _requerido(gama, "gama")  # La gama es obligatoria
        if str(gama).upper() not in self.GAMAS:  # Debe estar en la lista permitida
            raise DatosInvalidosError(f"Gama inválida '{gama}'. Use {self.GAMAS}.")
        self._gama = str(gama).upper()  # Se guarda en mayúsculas

    def validar_parametros(self, duracion) -> None:
        """Valida la duración contra el rango de equipos (2-72 h)."""
        self._validar_duracion(duracion)

    def calcular_costo(self, duracion=None, impuesto=0.19, descuento=0.0, recargo_extra=0.0) -> float:
        """SOBRESCRIBE el cálculo: agrega el seguro obligatorio como recargo adicional."""
        horas = self.DURACION_MIN if duracion is None else duracion  # Duración efectiva
        self.validar_parametros(horas)  # Se valida antes de calcular el seguro
        seguro = self._tarifa_hora * horas * self.PORCENTAJE_SEGURO  # 5 % del costo base
        # Se reutiliza el cálculo de la clase padre sumando el seguro al recargo
        return super().calcular_costo(horas, impuesto, descuento, recargo_extra + seguro)

    def describir(self) -> str:
        """Descripción específica de un equipo."""
        return f"Equipo '{self._nombre}' [{self._id}] gama {self._gama} (seguro obligatorio 5%)"


class AsesoriaEspecializada(Servicio):
    """Servicio de asesoría: duración 1-8 h, con área de especialidad."""

    DURACION_MIN, DURACION_MAX = 1, 8  # Rango propio de asesorías

    def __init__(self, id_servicio=None, nombre=None, tarifa_hora=None, especialidad=None) -> None:
        """Construye la asesoría; valida además la especialidad."""
        super().__init__(id_servicio, nombre, tarifa_hora)  # Datos comunes
        # La especialidad es obligatoria; se guarda sin espacios sobrantes
        self._especialidad = str(_requerido(especialidad, "especialidad")).strip()

    def validar_parametros(self, duracion) -> None:
        """Valida la duración contra el rango de asesorías (1-8 h)."""
        self._validar_duracion(duracion)

    def describir(self) -> str:
        """Descripción específica de una asesoría."""
        return f"Asesoría '{self._nombre}' [{self._id}] en {self._especialidad}"


# =============================================================================
# RESERVA
# =============================================================================
class EstadoReserva(Enum):
    """Estados posibles de una reserva."""

    PENDIENTE = "PENDIENTE"  # Creada pero aún sin confirmar
    CONFIRMADA = "CONFIRMADA"  # Confirmada: el servicio queda ocupado
    CANCELADA = "CANCELADA"  # Cancelada: el servicio se libera
    PROCESADA = "PROCESADA"  # Procesada: costo final calculado y reserva cerrada


class Reserva(EntidadSistema):
    """Integra un cliente, un servicio, la duración y el estado."""

    def __init__(self, id_reserva, cliente, servicio, duracion, **opciones_costo) -> None:
        """Crea la reserva en estado PENDIENTE tras validar todos sus componentes."""
        if not isinstance(cliente, Cliente):  # El cliente debe ser un objeto Cliente
            raise ReservaInvalidaError("La reserva requiere un Cliente válido.")
        if not isinstance(servicio, Servicio):  # El servicio debe ser un objeto Servicio
            raise ReservaInvalidaError("La reserva requiere un Servicio válido.")
        servicio.validar_parametros(duracion)  # Valida la duración según el tipo de servicio
        self.__id = id_reserva  # Identificador de la reserva (privado)
        self.__cliente = cliente  # Cliente que reserva
        self.__servicio = servicio  # Servicio reservado
        self.__duracion = duracion  # Horas reservadas
        self.__estado = EstadoReserva.PENDIENTE  # Estado inicial
        self.__opciones_costo = dict(opciones_costo)  # Impuesto/descuento/recargo que se usarán al procesar
        # Costo calculado con polimorfismo (puede lanzar CalculoInconsistenteError)
        self.__costo = servicio.calcular_costo(duracion, **opciones_costo)

    @property
    def identificador(self) -> str:
        """Id de la reserva."""
        return str(self.__id)

    @property
    def cliente(self) -> Cliente:
        """Cliente de la reserva."""
        return self.__cliente

    @property
    def servicio(self) -> Servicio:
        """Servicio de la reserva."""
        return self.__servicio

    @property
    def estado(self) -> EstadoReserva:
        """Estado actual de la reserva."""
        return self.__estado

    @property
    def costo(self) -> float:
        """Costo total calculado."""
        return self.__costo

    def confirmar(self) -> None:
        """Confirma la reserva y marca el servicio como no disponible."""
        if self.__estado is not EstadoReserva.PENDIENTE:  # Solo se confirma desde PENDIENTE
            raise OperacionNoPermitidaError(
                f"Solo se confirma una reserva PENDIENTE (actual: {self.__estado.value})."
            )
        self.__servicio.ocupar()  # Puede lanzar ServicioNoDisponibleError si ya está ocupado
        self.__estado = EstadoReserva.CONFIRMADA  # Solo se llega aquí si ocupar() funcionó

    def procesar(self, **opciones_costo) -> float:
        """Procesa la reserva: recalcula el costo final y la cierra (estado PROCESADA).

        Acepta opciones opcionales (impuesto, descuento, recargo_extra) que sustituyen
        a las indicadas al crear la reserva.
        """
        if self.__estado is not EstadoReserva.CONFIRMADA:  # Solo se procesa una reserva CONFIRMADA
            raise OperacionNoPermitidaError(
                f"Solo se procesa una reserva CONFIRMADA (actual: {self.__estado.value})."
            )
        opciones = {**self.__opciones_costo, **opciones_costo}  # Las nuevas opciones tienen prioridad
        total = self.__servicio.calcular_costo(self.__duracion, **opciones)  # Puede lanzar CalculoInconsistenteError
        self.__costo = total  # Solo si el cálculo fue válido se actualiza el costo
        self.__estado = EstadoReserva.PROCESADA  # Nuevo estado: reserva cerrada
        return total

    def cancelar(self) -> None:
        """Cancela la reserva y libera el servicio si estaba confirmada."""
        if self.__estado is EstadoReserva.CANCELADA:  # No se puede cancelar dos veces
            raise OperacionNoPermitidaError("La reserva ya estaba cancelada.")
        if self.__estado is EstadoReserva.PROCESADA:  # Una reserva procesada ya no se cancela
            raise OperacionNoPermitidaError("No se puede cancelar una reserva ya procesada.")
        if self.__estado is EstadoReserva.CONFIRMADA:  # Si estaba confirmada, el servicio estaba ocupado
            self.__servicio.liberar()  # Se devuelve la disponibilidad
        self.__estado = EstadoReserva.CANCELADA  # Nuevo estado

    def resumen(self) -> str:
        """Descripción corta de la reserva."""
        return (
            f"Reserva[{self.__id}] {self.__cliente.nombre} -> {self.__servicio.nombre} "
            f"{self.__duracion}h | ${self.__costo:,.2f} | {self.__estado.value}"
        )
