from django.core.management.base import BaseCommand
from datetime import datetime, timedelta, time as dtime
from django.utils import timezone
import requests
import time
from registros.services import registrar_evento


class Command(BaseCommand):
    help = 'Polling del biométrico cada 10 segundos'

    def add_arguments(self, parser):
        parser.add_argument('--terminal-sn', required=True, help='Serial del terminal ZKTeco')
        parser.add_argument('--intervalo', type=int, default=10, help='Segundos entre consultas')
        parser.add_argument('--inicio', default='06:00:00', help='Hora de inicio HH:MM:SS (default 06:00:00)')

    def handle(self, *args, **options):
        terminal_sn = options['terminal_sn']
        intervalo = options['intervalo']
        hora_inicio_str = options['inicio']

        zona_horaria = timezone.get_current_timezone()
        fecha_hoy = timezone.now().astimezone(zona_horaria).date()
        hora, minuto, seg = map(int, hora_inicio_str.split(':'))
        inicio_del_dia = timezone.make_aware(datetime.combine(fecha_hoy, dtime(hora, minuto, seg)), zona_horaria)
        cursor_desde = inicio_del_dia
        self.stdout.write(f"Iniciando polling para terminal: {terminal_sn} desde={cursor_desde} cada={intervalo}s")

        while True:
            try:
                cursor_hasta = cursor_desde + timedelta(seconds=intervalo)
                consulta_inicio = max(cursor_desde - timedelta(seconds=2), inicio_del_dia)
                consulta_fin = cursor_hasta
                formato_api = "%Y-%m-%d %H:%M:%S"
                inicio_str = consulta_inicio.strftime(formato_api)
                fin_str = consulta_fin.strftime(formato_api)

                token_api = "1f228f3588a24a509c3dad042dc4b85e447cbbcc"
                eventos_recibidos = self.obtener_transacciones_recientes(token_api, terminal_sn, inicio_str,
                                                                         fin_str)
                if eventos_recibidos:
                    eventos_recibidos.sort(key=lambda e: e.get("punch_time", ""))
                    for evento in eventos_recibidos:
                        resultado = registrar_evento(evento)
                        if resultado.get('created_event'):
                            self.stdout.write(f"Nuevo evento: {resultado}")

                cursor_desde = cursor_hasta
                ahora_local = timezone.now().astimezone(zona_horaria)
                if cursor_desde >= ahora_local:
                    self.stdout.write("Polling actualizado. Sin eventos que registrar por el momento.")
                    time.sleep(0.3)

            except KeyboardInterrupt:
                self.stdout.write("Deteniendo polling...")
                break
            except Exception as e:
                self.stdout.write(f"Error: {e}")
                time.sleep(intervalo)

    def obtener_transacciones_recientes(self, token, terminal_sn , inicio_str, fin_str):
        TRANS_URL_BASE = "http://192.168.191.222:8081/iclock/api/transactions/"

        headers = {"Authorization": f"Token {token}"}
        params = {
            "start_time": inicio_str,
            "end_time": fin_str,
            "terminal_sn": terminal_sn,
        }

        todas = []
        next_url = TRANS_URL_BASE
        while next_url:
            try:
                if next_url == TRANS_URL_BASE:
                    resp = requests.get(next_url, headers=headers, params=params, timeout=30)
                else:
                    resp = requests.get(next_url, headers=headers, timeout=30)
                resp.raise_for_status()
                payload = resp.json()

                datos = payload.get("data", [])
                todas.extend(datos)

                next_url = payload.get("next")
            except requests.RequestException as e:
                print(f"Error al consultar transacciones para terminal {terminal_sn}: {e}")
                break

        return todas
