# Software FJ – Sistema Integral de Gestión de Clientes, Servicios y Reservas

Proyecto del curso **Programación (213023)** – UNAD, Ingeniería de Sistemas.
Aplicación en **Python 3.12+** orientada a objetos, **sin bases de datos**: todo se gestiona en memoria
(objetos y listas). El único archivo que se escribe es el log `logs/software_fj_eventos.log`.

## Estructura de carpetas

```
SoftwareFJ/
├── main.py                   # Punto de entrada: simulación de 23 operaciones
├── README.md
├── .gitignore
├── logs/
│   └── software_fj_eventos.log   # Se genera al ejecutar
└── software_fj/              # Paquete con la lógica
    ├── __init__.py
    ├── exceptions.py         # SoftwareFJError y 6 excepciones derivadas
    ├── logger.py             # RegistroEventos: log con marca de tiempo y causas (__cause__)
    ├── models.py             # EntidadSistema, Cliente, Servicio (+3 hijas), Reserva
    └── gestor.py             # GestorFJ: listas internas, fábrica de servicios, reservas
```

## Conceptos aplicados

- **Abstracción:** `EntidadSistema` y `Servicio` (clases abstractas con `abc`).
- **Encapsulación:** `Cliente` con atributos privados, `@property` y setters validados
  (regex de correo, teléfono numérico ≥ 7 dígitos, nombre ≥ 3 caracteres).
- **Herencia y polimorfismo:** `ReservaSala` (1-12 h), `AlquilerEquipo` (2-72 h, seguro obligatorio 5 %)
  y `AsesoriaEspecializada` (1-8 h) sobrescriben validación, descripción y costo.
- **Sobrecarga:** `calcular_costo(duracion=None, impuesto=0.19, descuento=0.0, recargo_extra=0.0)`.
- **Reserva:** estados `PENDIENTE → CONFIRMADA → PROCESADA` (o `CANCELADA`); `confirmar()` ocupa el servicio, `procesar()` fija el costo final y `cancelar()` lo libera.
- **Excepciones:** `try/except`, `try/except/else`, `try/except/finally` y `raise ... from ...`
  (el log registra el error y su causa).

## Ejecución

```bash
python main.py
```

No requiere dependencias externas.

## Simulación (23 operaciones)

Clientes válidos, inválidos y duplicados · servicios válidos, con tarifa negativa y parámetros faltantes ·
reservas exitosas (descuento e impuestos) · procesamiento de reservas · reservas fallidas (servicio ocupado, cliente inexistente,
duración fuera de rango) · descuento inconsistente · cancelación con liberación del servicio.

## Ejemplo de log

```
ERROR   | Operación 13 (...) -> ReservaInvalidaError: No se pudo procesar la reserva de C002 para S001.
CAUSA   | ServicioNoDisponibleError: El servicio S001 ya está ocupado.
```

## Equipo

Integrantes: _ILEAN XAVIER SALAS JAIMES_
