"""gestor.py - Controlador que administra clientes, servicios y reservas en memoria."""
# Excepciones propias que el gestor lanza o captura
from software_fj.exceptions import (
    DatosInvalidosError,
    OperacionNoPermitidaError,
    ParametrosFaltantesError,
    ReservaInvalidaError,
    SoftwareFJError,
)
from software_fj.logger import RegistroEventos  # Para registrar eventos en el .log
# Clases del dominio que el gestor construye y administra
from software_fj.models import (
    AlquilerEquipo,
    AsesoriaEspecializada,
    Cliente,
    Reserva,
    ReservaSala,
    Servicio,
)


class GestorFJ:
    """Gestiona las listas internas (sin base de datos) y registra los eventos."""

    # Fábrica: relaciona el nombre del tipo de servicio con su clase concreta
    TIPOS_SERVICIO = {
        "sala": ReservaSala,
        "equipo": AlquilerEquipo,
        "asesoria": AsesoriaEspecializada,
    }

    def __init__(self, log: RegistroEventos) -> None:
        """Inicializa las listas vacías y guarda el registrador de eventos."""
        self.__log = log  # Registrador (privado)
        self.__clientes: list[Cliente] = []  # Lista interna de clientes
        self.__servicios: list[Servicio] = []  # Lista interna de servicios
        self.__reservas: list[Reserva] = []  # Lista interna de reservas

    # ------------------------------------------------------------------ clientes
    def registrar_cliente(self, **datos) -> Cliente:
        """Crea y registra un cliente; rechaza duplicados por id o por correo."""
        try:
            cliente = Cliente(**datos)  # Construye y valida el cliente
        except SoftwareFJError:
            raise  # Errores propios: se propagan tal cual para que el llamador los maneje
        except TypeError as error:  # Argumento desconocido o mal formado
            raise DatosInvalidosError("Datos de cliente mal formados.") from error  # Encadenamiento
        for existente in self.__clientes:  # Recorre los clientes ya registrados
            # Duplicado si coincide el id o el correo
            if existente.identificador == cliente.identificador or existente.correo == cliente.correo:
                raise OperacionNoPermitidaError(
                    f"Cliente duplicado (id/correo ya registrado): {cliente.identificador}."
                )
        self.__clientes.append(cliente)  # Se agrega a la lista interna
        self.__log.info(f"Cliente registrado: {cliente}")  # Se deja constancia en el log
        return cliente

    def buscar_cliente(self, id_cliente: str) -> Cliente:
        """Devuelve el cliente con ese id o lanza ReservaInvalidaError si no existe."""
        for cliente in self.__clientes:  # Búsqueda secuencial en la lista
            if cliente.identificador == id_cliente:
                return cliente
        raise ReservaInvalidaError(f"Cliente inexistente: {id_cliente}.")

    # ------------------------------------------------------------------ servicios
    def crear_servicio(self, tipo: str, **datos) -> Servicio:
        """Fábrica de servicios: crea el tipo pedido y lo agrega a la lista interna."""
        clase = self.TIPOS_SERVICIO.get(str(tipo).lower())  # Busca la clase según el tipo
        if clase is None:  # Tipo no reconocido
            raise DatosInvalidosError(f"Tipo de servicio desconocido: '{tipo}'.")
        try:
            servicio = clase(**datos)  # Construye el servicio (valida sus datos)
        except TypeError as error:  # Argumento no esperado por el constructor
            raise ParametrosFaltantesError(f"Parámetros incorrectos para '{tipo}'.") from error
        self.__servicios.append(servicio)  # Se agrega a la lista interna
        self.__log.info(f"Servicio creado: {servicio.describir()}")  # Constancia en el log
        return servicio

    def buscar_servicio(self, id_servicio: str) -> Servicio:
        """Devuelve el servicio con ese id o lanza ReservaInvalidaError si no existe."""
        for servicio in self.__servicios:  # Búsqueda secuencial
            if servicio.identificador == id_servicio:
                return servicio
        raise ReservaInvalidaError(f"Servicio inexistente: {id_servicio}.")

    # ------------------------------------------------------------------ reservas
    def crear_reserva(self, id_cliente: str, id_servicio: str, duracion, **opciones_costo) -> Reserva:
        """Crea y confirma una reserva; cualquier fallo se encadena con `raise ... from`."""
        try:
            cliente = self.buscar_cliente(id_cliente)  # Debe existir el cliente
            servicio = self.buscar_servicio(id_servicio)  # Debe existir el servicio
            id_reserva = f"R{len(self.__reservas) + 1:03d}"  # Id consecutivo: R001, R002...
            reserva = Reserva(id_reserva, cliente, servicio, duracion, **opciones_costo)  # Valida y calcula
            reserva.confirmar()  # Ocupa el servicio (puede lanzar ServicioNoDisponibleError)
        except SoftwareFJError as error:
            # ENCADENAMIENTO: el error original queda guardado en __cause__ de la nueva excepción
            raise ReservaInvalidaError(
                f"No se pudo procesar la reserva de {id_cliente} para {id_servicio}."
            ) from error
        else:  # Solo se ejecuta si NO hubo excepción en el try
            self.__reservas.append(reserva)  # La reserva se guarda en la lista interna
            self.__log.info(f"Reserva confirmada: {reserva}")  # Constancia en el log
            return reserva

    def buscar_reserva(self, id_reserva: str) -> Reserva:
        """Devuelve la reserva con ese id o lanza ReservaInvalidaError si no existe."""
        for reserva in self.__reservas:  # Búsqueda secuencial
            if reserva.identificador == id_reserva:
                return reserva
        raise ReservaInvalidaError(f"Reserva inexistente: {id_reserva}.")

    def procesar_reserva(self, id_reserva: str, **opciones_costo) -> Reserva:
        """Procesa una reserva confirmada; cualquier fallo se encadena con `raise ... from`."""
        try:
            reserva = self.buscar_reserva(id_reserva)  # Debe existir
            reserva.procesar(**opciones_costo)  # Puede lanzar OperacionNoPermitida o CalculoInconsistente
        except SoftwareFJError as error:
            # ENCADENAMIENTO: el error original queda en __cause__
            raise ReservaInvalidaError(f"No se pudo procesar la reserva {id_reserva}.") from error
        else:  # Solo si no hubo excepción
            self.__log.info(f"Reserva procesada: {reserva}")  # Constancia en el log
            return reserva

    def cancelar_reserva(self, id_reserva: str) -> Reserva:
        """Cancela una reserva existente y libera su servicio."""
        reserva = self.buscar_reserva(id_reserva)  # Debe existir
        reserva.cancelar()  # Cambia el estado y libera el servicio (puede lanzar OperacionNoPermitida)
        self.__log.info(f"Reserva cancelada: {reserva}")  # Constancia en el log
        return reserva

    # ------------------------------------------------------------------ consultas
    @property
    def reservas(self) -> list[Reserva]:
        """Copia de la lista de reservas (no se expone la lista interna)."""
        return list(self.__reservas)

    @property
    def servicios(self) -> list[Servicio]:
        """Copia de la lista de servicios."""
        return list(self.__servicios)

    @property
    def clientes(self) -> list[Cliente]:
        """Copia de la lista de clientes."""
        return list(self.__clientes)
