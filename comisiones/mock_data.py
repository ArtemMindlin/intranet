VENTAS = [
        {
            "matricula": "2127MXT",
            "idv": "2398695",
            "tipo_venta": "VENTA DETALL EXENTA",
            "ud_financiadas": "",
            "dni": "52708465T",
            "tipo_cliente": "CIF (FLOTAS)",
            "nombre_cliente": "Manuel Garcí­a"
        },
        {
            "matricula": "0453MXZ",
            "idv": "2412606",
            "tipo_venta": "VENTA RENTING",
            "ud_financiadas": "1",
            "dni": "21651068R",
            "tipo_cliente": "CIF (FLOTAS)",
            "nombre_cliente": "David Jimenez"
        },
        {
            "matricula": "0422MXR",
            "idv": "2442228",
            "tipo_venta": "VENTA DETALL PARTICULAR",
            "ud_financiadas": "",
            "dni": "44869497G",
            "tipo_cliente": "NIF (PARTICULAR)",
            "nombre_cliente": "Julia Gutierrez"
        },
        {
            "matricula": "1084MXR",
            "idv": "2440829",
            "tipo_venta": "VENTA DETALL PARTICULAR",
            "ud_financiadas": "",
            "dni": "25403558L",
            "tipo_cliente": "NIF (PARTICULAR)",
            "nombre_cliente": "Nieves Fernandez"
        },
        {
            "matricula": "9178MXV",
            "idv": "2446855",
            "tipo_venta": "VENTA DETALL PARTICULAR",
            "ud_financiadas": "",
            "dni": "34826735F",
            "tipo_cliente": "NIF (PARTICULAR)",
            "nombre_cliente": "José López"
        }
    ]

comision_aprobada = 1325
COMISION_APROBADA = f"{comision_aprobada:,}".replace(",", ".")

INCIDENCIAS = [
    {
        "empleado": "Rafael González",
        "matricula": "2127MXT",
        "fecha": "26/12/2025",
        "tipo": "Incidencia comisiones Diciembre",
        "detalle": "No se ha reflejado la venta del Nissan Qashqai con IDV 2398695.",
        "estado": "Pte. revisión",
        "validacion_ok": True,
    },
    {
        "empleado": "Vicente Martínez",
        "matricula": "5869AEF",
        "fecha": "23/12/2025",
        "tipo": "Incidencia comisiones Diciembre",
        "detalle": "La venta del vehículo 5869AEF es financiada y no aparece computada.",
        "estado": "Aceptada",
        "validacion_ok": False,
    },
    {
        "empleado": "Vicente Martínez",
        "matricula": "0422MXR",
        "fecha": "23/12/2025",
        "tipo": "Modificación vehículo",
        "detalle": "El usuario ha solicitado la modificación de datos del vehículo asignado.",
        "estado": "Aceptada",
        "validacion_ok": False,
    },
    {
        "empleado": "Artem Mindlin",
        "matricula": "9178MXV",
        "fecha": "27/12/2025",
        "tipo": "Cambio estructura organizativa",
        "detalle": "El usuario ha notificado un cambio de estructura interna.",
        "estado": "Rechazada",
        "validacion_ok": False,
    },
]

