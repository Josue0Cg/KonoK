from django.db import models
from django.utils import timezone

class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)

    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('tecnico', 'Técnico'),
        ('usuario', 'Usuario'),
    ]

    rol = models.CharField(max_length=10, choices=ROL_CHOICES, default='usuario')

    def __str__(self):
        return self.nombre

class BackupRegistro(models.Model):
    fecha = models.DateTimeField(default=timezone.now)
    archivo = models.CharField(max_length=200)

    def __str__(self):
        return f"Backup: {self.archivo} - {self.fecha.strftime('%Y-%m-%d %H:%M:%S')}"
    
class BackupConfig(models.Model):
    hora_backup = models.TimeField(help_text="Hora del día para ejecutar el backup automático")
    activa = models.BooleanField(default=True, help_text="Indica si el backup automático está activo")

    def __str__(self):
        estado = "Activo" if self.activa else "Inactivo"
        return f"Backup automático a las {self.hora_backup} ({estado})"
class Comentario(models.Model):
    nombre = models.CharField(max_length=100)
    comentario = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # Fecha y hora en que se crea el comentario

    def __str__(self):
        return f"Comentario de {self.nombre} el {self.fecha_creacion}"