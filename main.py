"""main.py - Punto de entrada: simulación automática de 23 operaciones de Software FJ."""
from software_fj.exceptions import SoftwareFJError  # Base de las excepciones propias
from software_fj.gestor import GestorFJ  # Controlador principal
from software_fj.logger import RegistroEventos  # Registrador de eventos

log = RegistroEventos()  # Crea el registrador (logs/software_fj_eventos.log)
gestor = GestorFJ(log)  # Crea el controlador con sus listas en memoria
resultados = {"ok": 0, "error": 0}  # Contadores de operaciones exitosas y fallidas


def ejecutar(numero: int, descripcion: str, operacion) -> None:
    """Ejecuta una operación sin permitir que un error detenga el programa."""
    print(f"\n[{numero:02d}] {descripcion}")  # Encabezado de la operación en consola
    try:
        resultado = operacion()  # Se intenta ejecutar la operación recibida (función sin argumentos)
    except SoftwareFJError as error:  # Errores controlados propios del sistema
        resultados["error"] += 1  # Se cuenta como operación con error
        log.excepcion(f"Operación {numero} ({descripcion})", error)  # Se registra error + causas
        print(f"     ERROR controlado: {type(error).__name__}: {error}")
        if error.__cause__ is not None:  # Si hay excepción encadenada, se muestra
            print(f"     Causa: {type(error.__cause__).__name__}: {error.__cause__}")
    except Exception as error:  # Cualquier otro error inesperado también se contiene
        resultados["error"] += 1
        log.excepcion(f"Operación {numero} - error inesperado", error)
        print(f"     ERROR inesperado: {type(error).__name__}: {error}")
    else:  # Se ejecuta solo si el try terminó SIN excepción
        resultados["ok"] += 1
        log.info(f"Operación {numero} exitosa: {descripcion}")
        print(f"     OK: {resultado}")
    finally:  # Se ejecuta SIEMPRE, con o sin error
        log.info(f"Operación {numero} finalizada")


def simular() -> None:
    """Define y ejecuta, en orden, las 23 operaciones de la demostración."""
    # ---------------------------------------------------------------- Clientes
    ejecutar(1, "Registro válido de cliente Ana", lambda: gestor.registrar_cliente(
        id_cliente="C001", nombre="Ana Pérez", correo="ana@mail.com", telefono="3101234567"))
    ejecutar(2, "Registro válido de cliente Luis", lambda: gestor.registrar_cliente(
        id_cliente="C002", nombre="Luis Gómez", correo="luis@mail.com", telefono="3207654321"))
    ejecutar(3, "Cliente con correo inválido", lambda: gestor.registrar_cliente(
        id_cliente="C003", nombre="Marta", correo="marta-sin-arroba", telefono="3001112233"))
    ejecutar(4, "Cliente con nombre corto y teléfono inválido", lambda: gestor.registrar_cliente(
        id_cliente="C004", nombre="Al", correo="al@mail.com", telefono="12ab"))
    ejecutar(5, "Cliente duplicado (mismo id)", lambda: gestor.registrar_cliente(
        id_cliente="C001", nombre="Ana Otra", correo="otra@mail.com", telefono="3109999999"))
    # ---------------------------------------------------------------- Servicios
    ejecutar(6, "Crear sala válida", lambda: gestor.crear_servicio(
        "sala", id_servicio="S001", nombre="Sala Júpiter", tarifa_hora=50000, capacidad=10).resumen())
    ejecutar(7, "Crear equipo válido", lambda: gestor.crear_servicio(
        "equipo", id_servicio="S002", nombre="Portátil Pro", tarifa_hora=15000, gama="alta").resumen())
    ejecutar(8, "Crear asesoría válida", lambda: gestor.crear_servicio(
        "asesoria", id_servicio="S003", nombre="Asesoría Cloud", tarifa_hora=80000,
        especialidad="Arquitectura en la nube").resumen())
    ejecutar(9, "Crear sala con tarifa negativa", lambda: gestor.crear_servicio(
        "sala", id_servicio="S004", nombre="Sala Marte", tarifa_hora=-100, capacidad=5))
    ejecutar(10, "Crear equipo con parámetros faltantes (sin gama)", lambda: gestor.crear_servicio(
        "equipo", id_servicio="S005", nombre="Proyector", tarifa_hora=20000))
    # ---------------------------------------------------------------- Reservas
    ejecutar(11, "Reserva exitosa de sala 3h con 10% de descuento", lambda: gestor.crear_reserva(
        "C001", "S001", 3, descuento=0.10).resumen())
    ejecutar(12, "Reserva exitosa de equipo 10h (seguro obligatorio)", lambda: gestor.crear_reserva(
        "C002", "S002", 10).resumen())
    ejecutar(13, "Reserva fallida: servicio ya ocupado", lambda: gestor.crear_reserva(
        "C002", "S001", 2))
    ejecutar(14, "Reserva fallida: cliente inexistente", lambda: gestor.crear_reserva(
        "C999", "S003", 2))
    ejecutar(15, "Reserva fallida: duración fuera de rango (20h en asesoría)", lambda: gestor.crear_reserva(
        "C001", "S003", 20))
    # ---------------------------------------------------------------- Cálculos
    ejecutar(16, "Cálculo inconsistente: descuento del 150%", lambda: gestor.buscar_servicio(
        "S003").calcular_costo(2, descuento=1.5))
    ejecutar(17, "Costo con sobrecarga: 4h, sin impuesto, recargo 20000", lambda: gestor.buscar_servicio(
        "S003").calcular_costo(4, impuesto=0.0, recargo_extra=20000))
    # ---------------------------------------------------------------- Procesamiento y cancelaciones
    ejecutar(18, "Procesar reserva R002 con 5% de descuento", lambda: gestor.procesar_reserva(
        "R002", descuento=0.05).resumen())
    ejecutar(19, "Procesar de nuevo R002 (ya procesada)", lambda: gestor.procesar_reserva(
        "R002"))
    ejecutar(20, "Cancelar R002 ya procesada (operación no permitida)", lambda: gestor.cancelar_reserva(
        "R002"))
    # ---------------------------------------------------------------- Cancelaciones
    ejecutar(21, "Cancelar reserva confirmada R001 (libera la sala)", lambda: gestor.cancelar_reserva(
        "R001").resumen())
    ejecutar(22, "Reservar de nuevo la sala liberada", lambda: gestor.crear_reserva(
        "C002", "S001", 2).resumen())
    ejecutar(23, "Cancelar de nuevo R001 (operación no permitida)", lambda: gestor.cancelar_reserva(
        "R001"))


if __name__ == "__main__":  # Solo se ejecuta al correr `python main.py` (no al importarlo)
    log.info("=== INICIO DE SIMULACIÓN SOFTWARE FJ ===")  # Marca de inicio en el log
    try:
        simular()  # Ejecuta las 23 operaciones
    finally:  # Cierre seguro de la simulación, incluso si algo falla gravemente
        print("\n=== RESUMEN FINAL ===")
        for reserva in gestor.reservas:  # Muestra todas las reservas registradas
            print(" ", reserva)
        print(f"Operaciones exitosas: {resultados['ok']} | con error controlado: {resultados['error']}")
        log.info(f"=== FIN DE SIMULACIÓN === ok={resultados['ok']} errores={resultados['error']}")
