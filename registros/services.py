from datetime import datetime
from django.utils import timezone
from .models import EventoZK, Consumo
from .utils import clasificar_consumo

def _parsear_a_hora_local(fecha_hora_str: str):
    if not fecha_hora_str:
        return None
    dt_naive = datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M:%S")
    return timezone.make_aware(dt_naive, timezone.get_current_timezone())

def registrar_evento(evento_zk: dict) -> dict:

    zk_evento_id      = int(evento_zk["id"])
    numero_serie_term = evento_zk.get("terminal_sn", "")
    codigo_empleado   = str(evento_zk.get("emp_code", "")).strip()
    fecha_hora_evento = _parsear_a_hora_local(evento_zk.get("punch_time"))
    alias_area        = evento_zk.get("area_alias", "") or ""
    fecha_hora_carga  = _parsear_a_hora_local(evento_zk.get("upload_time"))

    evento, creado = EventoZK.objects.get_or_create(
        event_id=zk_evento_id,
        defaults={
            "terminal_sn": numero_serie_term,
            "codigo": codigo_empleado,
            "event_time": fecha_hora_evento,
            "area_alias": alias_area,
            "upload_time": fecha_hora_carga,
            "payload": evento_zk,
        }
    )
    if not creado:
        return {"created_event": False, "reason": "duplicate_event_id", "event_id": zk_evento_id}

    tipo_consumo = clasificar_consumo(fecha_hora_evento)
    consumo_creado = False
    consumo_registrado = None
    if tipo_consumo:
        consumo_registrado, consumo_creado = Consumo.objects.get_or_create(
            codigo=codigo_empleado,
            fecha=fecha_hora_evento.date(),
            tipo=tipo_consumo,
            defaults={
                "primer_evento": fecha_hora_evento,
                "terminal_sn": numero_serie_term,
            }
        )

    return {
        "created_event": True,
        "event_id": evento.event_id,
        "codigo": codigo_empleado,
        "tipo": tipo_consumo,
        "created_consumo": consumo_creado,
    }