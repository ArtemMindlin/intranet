import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from comisiones.models import (
    Boletin,
    Comision,
    Incidencia,
    LecturaBoletin,
    Perfil,
    Venta,
)


class Command(BaseCommand):
    help = (
        "Puebla la base de datos con datos demo reproducibles para ventas, comisiones "
        "incidencias y boletines."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--n-ventas",
            type=int,
            default=30,
            help="Numero de ventas demo a crear (default: 30).",
        )
        parser.add_argument(
            "--n-incidencias",
            type=int,
            default=10,
            help="Numero de incidencias demo a crear (default: 10).",
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help=(
                "Elimina datos demo de ventas/comisiones/incidencias y vuelve a "
                "generarlos."
            ),
        )

    def handle(self, *args, **options):
        n_ventas = max(0, options["n_ventas"])
        n_incidencias = max(0, options["n_incidencias"])
        reset = options["reset"]

        if not reset and (
            Venta.objects.exists()
            or Incidencia.objects.exists()
            or Boletin.objects.exists()
        ):
            self.stdout.write(
                self.style.WARNING(
                    "Seed omitido: ya existen ventas, incidencias o boletines. "
                    "Usa --reset para regenerar."
                )
            )
            return

        with transaction.atomic():
            if reset:
                deleted_lecturas, _ = LecturaBoletin.objects.all().delete()
                deleted_boletines, _ = Boletin.objects.all().delete()
                deleted_incidencias, _ = Incidencia.objects.all().delete()
                deleted_comisiones, _ = Comision.objects.all().delete()
                deleted_ventas, _ = Venta.objects.all().delete()
                self.stdout.write(
                    self.style.WARNING(
                        f"Reset aplicado: lecturas={deleted_lecturas}, "
                        f"boletines={deleted_boletines}, incidencias={deleted_incidencias}, "
                        f"comisiones={deleted_comisiones}, ventas={deleted_ventas}"
                    )
                )

            grupos = self._crear_grupos()
            users = self._crear_usuarios(grupos)
            self._configurar_perfiles(users)
            ventas = self._crear_ventas_y_comisiones(users, n_ventas)
            incidencias = self._crear_incidencias(users, ventas, n_incidencias)
            boletines = self._crear_boletines()
            lecturas_boletin = self._crear_lecturas_boletin(users, boletines)

        self.stdout.write(self.style.SUCCESS("Seed completado correctamente."))
        self.stdout.write(f"- Usuarios demo asegurados: {len(users)}")
        self.stdout.write(f"- Ventas creadas: {len(ventas)}")
        self.stdout.write(f"- Incidencias creadas: {len(incidencias)}")
        self.stdout.write(f"- Boletines creados: {len(boletines)}")
        self.stdout.write(f"- Lecturas de boletin creadas: {len(lecturas_boletin)}")

    def _crear_grupos(self):
        group_names = [
            "Vendedor",
            "Jefe de ventas",
            "Gerente",
            "Director Comercial",
        ]
        grupos = {}
        for name in group_names:
            grupo, _ = Group.objects.get_or_create(name=name)
            grupos[name] = grupo
        return grupos

    def _crear_usuarios(self, grupos):
        def _upsert_user(username, first_name, last_name, email, group_name, password):
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                },
            )
            changed = False
            if user.first_name != first_name:
                user.first_name = first_name
                changed = True
            if user.last_name != last_name:
                user.last_name = last_name
                changed = True
            if user.email != email:
                user.email = email
                changed = True
            if changed:
                user.save()

            user.set_password(password)
            user.save(update_fields=["password"])
            user.groups.add(grupos[group_name])
            return user

        users = {
            "director": _upsert_user(
                "director_demo",
                "Daniel",
                "Director",
                "director.demo@example.com",
                "Director Comercial",
                "Demo12345!",
            ),
            "gerente": _upsert_user(
                "gerente_demo",
                "Gabriel",
                "Gerente",
                "gerente.demo@example.com",
                "Gerente",
                "Demo12345!",
            ),
            "jefe": _upsert_user(
                "jefe_demo",
                "Javier",
                "Jefe",
                "jefe.demo@example.com",
                "Jefe de ventas",
                "Demo12345!",
            ),
            "jefe_postventa": _upsert_user(
                "jefe_postventa_demo",
                "Patricia",
                "Postventa",
                "jefe.postventa.demo@example.com",
                "Jefe de ventas",
                "Demo12345!",
            ),
            "vendedor_1": _upsert_user(
                "vendedor_1_demo",
                "Valeria",
                "Ventas",
                "vendedor1.demo@example.com",
                "Vendedor",
                "Demo12345!",
            ),
            "vendedor_2": _upsert_user(
                "vendedor_2_demo",
                "Victor",
                "Comercial",
                "vendedor2.demo@example.com",
                "Vendedor",
                "Demo12345!",
            ),
            "vendedor_3": _upsert_user(
                "vendedor_3_demo",
                "Violeta",
                "Asesora",
                "vendedor3.demo@example.com",
                "Vendedor",
                "Demo12345!",
            ),
        }
        return users

    def _configurar_perfiles(self, users):
        sede_principal = "Orihuela"
        dni_por_usuario = {
            "director": "70000001A",
            "gerente": "70000002B",
            "jefe": "70000003C",
            "jefe_postventa": "70000004D",
            "vendedor_1": "70000005E",
            "vendedor_2": "70000006F",
            "vendedor_3": "70000007G",
        }
        telefono_por_usuario = {
            "director": "600000001",
            "gerente": "600000002",
            "jefe": "600000003",
            "jefe_postventa": "600000004",
            "vendedor_1": "600000005",
            "vendedor_2": "600000006",
            "vendedor_3": "600000007",
        }

        director_perfil, _ = Perfil.objects.get_or_create(user=users["director"])
        director_perfil.dni = dni_por_usuario["director"]
        director_perfil.telefono = telefono_por_usuario["director"]
        director_perfil.sede = sede_principal
        director_perfil.area = Perfil.AREA_VENTAS
        director_perfil.save()

        gerente_perfil, _ = Perfil.objects.get_or_create(user=users["gerente"])
        gerente_perfil.dni = dni_por_usuario["gerente"]
        gerente_perfil.telefono = telefono_por_usuario["gerente"]
        gerente_perfil.sede = sede_principal
        gerente_perfil.area = Perfil.AREA_VENTAS
        gerente_perfil.director_comercial = users["director"]
        gerente_perfil.save()

        jefe_perfil, _ = Perfil.objects.get_or_create(user=users["jefe"])
        jefe_perfil.dni = dni_por_usuario["jefe"]
        jefe_perfil.telefono = telefono_por_usuario["jefe"]
        jefe_perfil.sede = sede_principal
        jefe_perfil.area = Perfil.AREA_VENTAS
        jefe_perfil.gerente = users["gerente"]
        jefe_perfil.director_comercial = users["director"]
        jefe_perfil.save()

        jefe_postventa_perfil, _ = Perfil.objects.get_or_create(
            user=users["jefe_postventa"]
        )
        jefe_postventa_perfil.dni = dni_por_usuario["jefe_postventa"]
        jefe_postventa_perfil.telefono = telefono_por_usuario["jefe_postventa"]
        jefe_postventa_perfil.sede = sede_principal
        jefe_postventa_perfil.area = Perfil.AREA_POSTVENTA
        jefe_postventa_perfil.gerente = users["gerente"]
        jefe_postventa_perfil.director_comercial = users["director"]
        jefe_postventa_perfil.save()

        perfiles_vendedores = [
            ("vendedor_1", Perfil.AREA_VENTAS, users["jefe"]),
            ("vendedor_2", Perfil.AREA_POSTVENTA, users["jefe_postventa"]),
            ("vendedor_3", Perfil.AREA_POSTVENTA, users["jefe_postventa"]),
        ]
        for vendedor_key, area, jefe_ref in perfiles_vendedores:
            perfil, _ = Perfil.objects.get_or_create(user=users[vendedor_key])
            perfil.dni = dni_por_usuario[vendedor_key]
            perfil.telefono = telefono_por_usuario[vendedor_key]
            perfil.sede = sede_principal
            perfil.area = area
            perfil.jefe_ventas = jefe_ref
            perfil.gerente = users["gerente"]
            perfil.director_comercial = users["director"]
            perfil.save()

    def _crear_ventas_y_comisiones(self, users, n_ventas):
        vendedores = [users["vendedor_1"], users["vendedor_2"], users["vendedor_3"]]
        today = timezone.localdate()
        ventas = []

        nombres = [
            "Carlos Martinez",
            "Laura Fernandez",
            "Miguel Navarro",
            "Sonia Lopez",
            "Rocio Sanchez",
            "Pablo Garcia",
            "Noelia Ruiz",
            "Mario Perez",
            "Sara Romero",
            "Jorge Morales",
        ]
        prefijos = ["ABC", "BTR", "CVM", "DQS", "ELX", "FRM", "GNT", "HJK"]
        sufijos = ["MXS", "LPR", "TQV", "NRT", "QPL", "ZXC", "RTY"]

        for idx in range(n_ventas):
            vendedor = vendedores[idx % len(vendedores)]
            tipo_venta = random.choice([code for code, _ in Venta.TIPO_VENTA_CHOICES])
            tipo_cliente = random.choice(
                [code for code, _ in Venta.TIPO_CLIENTE_CHOICES]
            )
            matricula = f"{random.randint(1000, 9999)}{random.choice(prefijos)}"[:10]
            idv = 2000000 + idx
            ud_financiadas = (
                random.choice([None, 1, 1, 2]) if tipo_venta != "EXENTA" else None
            )
            cliente = random.choice(nombres)
            dni_pref = random.randint(10000000, 99999999)
            dni_suf = random.choice(sufijos)[0]
            dni = f"{dni_pref}{dni_suf}"[:12]
            fecha_venta = today - timedelta(days=random.randint(0, 90))

            venta = Venta.objects.create(
                usuario=vendedor,
                matricula=matricula,
                idv=idv,
                tipo_venta=tipo_venta,
                ud_financiadas=ud_financiadas,
                dni=dni,
                tipo_cliente=tipo_cliente,
                nombre_cliente=cliente,
            )
            # fecha_venta usa auto_now_add; se ajusta tras crear para generar historico demo.
            Venta.objects.filter(pk=venta.pk).update(fecha_venta=fecha_venta)
            venta.refresh_from_db(fields=["fecha_venta"])
            ventas.append(venta)

            monto = Decimal(random.randint(80, 700))
            estado = random.choices(
                ["pendiente", "aprobada", "rechazada"], weights=[30, 55, 15], k=1
            )[0]
            Comision.objects.create(
                venta=venta,
                monto=monto,
                facturacion=Decimal(random.randint(15000, 50000)),
                margen_bruto=Decimal(random.randint(1500, 9000)),
                imp_costo=Decimal(random.randint(500, 3500)),
                comision_financiera=Decimal(random.randint(0, 1200)),
                total_beneficio=Decimal(random.randint(1000, 10000)),
                seguros=Decimal(random.randint(0, 700)),
                imp_comision=monto,
                estado=estado,
            )

        return ventas

    def _crear_incidencias(self, users, ventas, n_incidencias):
        if n_incidencias == 0:
            return []

        vendedores = [users["vendedor_1"], users["vendedor_2"], users["vendedor_3"]]
        today = timezone.localdate()
        incidencias = []
        tipos = [
            "Revision de comision",
            "Venta no reflejada",
            "Correccion de datos del cliente",
            "Error en financiacion",
            "Consulta de validacion",
        ]

        for idx in range(n_incidencias):
            vendedor = vendedores[idx % len(vendedores)]
            es_general = idx % 4 == 0
            estado = random.choices(
                ["pte_revision", "aceptada", "rechazada"], weights=[50, 35, 15], k=1
            )[0]
            fecha = today - timedelta(days=random.randint(0, 45))
            tipo = random.choice(tipos)
            detalle = (
                f"Incidencia demo {idx + 1}: revisar la operacion y confirmar "
                "la informacion de comision."
            )

            incidencia = Incidencia.objects.create(
                reportado_por=vendedor,
                es_general=es_general,
                fecha_incidencia=fecha,
                tipo=tipo,
                detalle=detalle,
                estado=estado,
                validacion_ok=estado == "aceptada",
            )

            if ventas and not es_general:
                venta = ventas[idx % len(ventas)]
                incidencia.ventas.add(venta)

            incidencias.append(incidencia)

        return incidencias

    def _crear_boletines(self):
        hoy = timezone.localdate()
        boletines_data = [
            {
                "boletin": "Boletín de objetivos comerciales",
                "fecha": hoy - timedelta(days=5),
                "marca": "Nissan",
                "tipo": "Comercial",
            },
            {
                "boletin": "Novedades de financiación Q1",
                "fecha": hoy - timedelta(days=18),
                "marca": "Renault",
                "tipo": "Financiero",
            },
            {
                "boletin": "Cambios de campañas de marca",
                "fecha": hoy - timedelta(days=32),
                "marca": "Dacia",
                "tipo": "Marketing",
            },
            {
                "boletin": "Resumen operativo mensual",
                "fecha": hoy - timedelta(days=41),
                "marca": "Nissan",
                "tipo": "Operativo",
            },
        ]
        boletines = []
        for data in boletines_data:
            boletines.append(Boletin.objects.create(**data))
        return boletines

    def _crear_lecturas_boletin(self, users, boletines):
        if not boletines:
            return []

        lecturas = []
        lecturas_config = [
            ("vendedor_1", [0, 1]),
            ("vendedor_2", [0]),
            ("vendedor_3", []),
            ("jefe", [0, 1, 2]),
            ("jefe_postventa", [0, 2]),
        ]
        for user_key, boletines_indices in lecturas_config:
            usuario = users[user_key]
            for idx in boletines_indices:
                if idx >= len(boletines):
                    continue
                lectura = LecturaBoletin.objects.create(
                    boletin=boletines[idx],
                    usuario=usuario,
                    confirmado=True,
                )
                lecturas.append(lectura)
        return lecturas
