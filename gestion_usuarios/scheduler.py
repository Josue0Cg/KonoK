from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from django_apscheduler.jobstores import DjangoJobStore, register_events
from apscheduler.jobstores.base import JobLookupError
from django.conf import settings
from django.utils.timezone import now
from .models import BackupConfig, BackupRegistro
import subprocess
import os

# Crear el scheduler una sola vez, global para todo el módulo
scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")

def start_scheduler():
    global scheduler
    if scheduler.running:
        print("Scheduler ya está corriendo.")
        return
    
    # Iniciar el scheduler
    scheduler.start()
    print("Scheduler iniciado.")

def exportar_backup_usuarios():
    print("Iniciando exportación de backup automático...")

    nombre_archivo = f"backup_automatico_{now().strftime('%Y%m%d_%H%M%S')}.sql"
    ruta_backup = os.path.join(settings.MEDIA_ROOT, nombre_archivo)

    mysqldump_path = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe"

    if not os.path.exists(settings.MEDIA_ROOT):
        os.makedirs(settings.MEDIA_ROOT)

    comando = [
        mysqldump_path,
        "-u", "root",
        "-padmin",  # Ajusta la contraseña o usa variable segura
        "gestion_bd",
        "gestion_usuarios_usuario",
        "--result-file", ruta_backup,
    ]

    try:
        subprocess.run(comando, check=True)
        print(f"Backup generado: {ruta_backup}")

        # Registrar en la tabla BackupRegistro
        BackupRegistro.objects.create(archivo=nombre_archivo)
        print("Registro de backup guardado en la base de datos.")

    except Exception as e:
        print(f"Error al generar backup: {e}")

def revisar_configuracion_y_programar():
    config = BackupConfig.objects.first()

    if config and config.activa:
        hora = config.hora_backup.hour
        minuto = config.hora_backup.minute
        print(f"Configuración encontrada: Backup activo. Programando para las {hora}:{minuto:02d}")

        # Programamos el trabajo de acuerdo a la hora y minuto establecidos
        trigger = CronTrigger(hour=hora, minute=minuto)
        scheduler.add_job(exportar_backup_usuarios, trigger, id="backup_diario", replace_existing=True)
        print(f"Backup programado para las {hora}:{minuto:02d}")

    else:
        try:
            scheduler.remove_job("backup_diario")
            print("Backup automático deshabilitado, job eliminado.")
        except JobLookupError:
            print("Job 'backup_diario' no existía al intentar deshabilitar backup.")
