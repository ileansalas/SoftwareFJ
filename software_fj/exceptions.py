"""exceptions.py - Jerarquía de excepciones personalizadas de Software FJ."""


class SoftwareFJError(Exception):
    """Excepción base: todas las excepciones del sistema heredan de ella.

    Permite capturar cualquier error propio con un solo `except SoftwareFJError`.
    """
    # No necesita código: hereda todo el comportamiento de Exception.


class DatosInvalidosError(SoftwareFJError):
    """Se lanza cuando un dato tiene formato o valor inválido (correo, teléfono, tarifa...)."""
    # Hereda de SoftwareFJError, por lo que también es capturable como error del sistema.


class ParametrosFaltantesError(SoftwareFJError):
    """Se lanza cuando falta un parámetro obligatorio (None, vacío o argumento omitido)."""
    # Se usa en la creación de clientes y servicios.


class OperacionNoPermitidaError(SoftwareFJError):
    """Se lanza cuando la operación no es válida en el estado actual (duplicados, cancelar dos veces)."""
    # Representa violaciones de reglas de negocio.


class ReservaInvalidaError(SoftwareFJError):
    """Se lanza cuando no es posible crear o procesar una reserva."""
    # Es la excepción "envoltorio" que el gestor encadena con `raise ... from`.


class ServicioNoDisponibleError(SoftwareFJError):
    """Se lanza cuando se intenta usar un servicio que ya está ocupado."""
    # Se produce al confirmar una reserva sobre un servicio no disponible.


class CalculoInconsistenteError(SoftwareFJError):
    """Se lanza cuando un cálculo financiero produce valores incoherentes (descuento > 100 %, etc.)."""
    # Protege la integridad de los costos calculados.
