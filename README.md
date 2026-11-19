## Estructura de carpetas

```
SoftwareFJ/
├── main.py                   # Punto de entrada: simulación de 20 operaciones
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
