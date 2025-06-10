from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Usuario, BackupRegistro, BackupConfig
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt 
from django.contrib.auth import authenticate, login, logout



from django.http import HttpResponse, FileResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect

from django.utils.encoding import smart_str
from django.contrib.auth.models import User
from django.utils.timezone import datetime


from django.utils.timezone import now
from django.urls import reverse_lazy
from django.contrib import messages
from django.conf import settings
from .models import BackupConfig
from django.conf import settings

from django import forms
import subprocess
import requests
import os
import re

def index(request):
    return render(request, 'index.html')



#----------- CRUD Usuarios -----------#
class UsuarioList(ListView):
    model = Usuario
    template_name = 'usuarios/lista.html'

class UsuarioCreate(CreateView):
    model = Usuario
    fields = ['nombre', 'correo']
    template_name = 'usuarios/form.html'
    success_url = reverse_lazy('usuario_lista')

class UsuarioUpdate(UpdateView):
    model = Usuario
    fields = ['nombre', 'correo']
    template_name = 'usuarios/form.html'
    success_url = reverse_lazy('usuario_lista')

class UsuarioDelete(DeleteView):
    model = Usuario
    template_name = 'usuarios/confirmar_eliminar.html'
    success_url = reverse_lazy('usuario_lista')

def cambiar_rol_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    nuevo_rol = request.POST.get('rol')

    if nuevo_rol in ['admin', 'tecnico', 'usuario']:
        usuario.rol = nuevo_rol
        usuario.save()

        # Crear usuario de MySQL y asignar permisos
        nombre_mysql = usuario.correo.split('@')[0]  # ejemplo: josue@gmail.com → 'josue'
        password_mysql = '123456'  # ⚠️ Puedes hacerlo dinámico más adelante

        # Crear usuario si no existe
        crear_usuario = f"CREATE USER IF NOT EXISTS '{nombre_mysql}'@'localhost' IDENTIFIED BY '{password_mysql}';"
        ejecutar_sql_mysql(crear_usuario)

        # Asignar permisos según rol
        if nuevo_rol == 'admin':
            permisos = f"GRANT ALL PRIVILEGES ON gestion_bd.* TO '{nombre_mysql}'@'localhost';"
        elif nuevo_rol == 'tecnico':
            permisos = f"GRANT SELECT, INSERT, UPDATE ON gestion_bd.* TO '{nombre_mysql}'@'localhost';"
        else:  # usuario
            permisos = f"GRANT SELECT ON gestion_bd.* TO '{nombre_mysql}'@'localhost';"

        ejecutar_sql_mysql(permisos)
        ejecutar_sql_mysql("FLUSH PRIVILEGES;")

        messages.success(request, f"Rol actualizado y permisos aplicados para '{usuario.nombre}'")
    else:
        messages.error(request, "Rol inválido")

    return redirect('usuario_lista')

#------------ Login / Register --------------#

def login_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({'success': True, 'message': f'Bienvenido, {user.username}'})
            else:
                return JsonResponse({'success': False, 'error': 'Credenciales inválidas'})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Usuario no encontrado'})
        
def logout_user(request):
    logout(request)
    return redirect('index')
class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_password(self):
        password = self.cleaned_data.get('password')

        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
            raise ValidationError('La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula, un número y un símbolo.')

        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Las contraseñas no coinciden.")
        
@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        recaptcha_response = request.POST.get('g-recaptcha-response')

        data = {
            'secret': '6LfUJForAAAAAIqNdi4mV1-8_W7Rbg-hVU_AaIEl',
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        if not result.get('success'):
            return JsonResponse({'success': False, 'error': 'Por favor verifica que no eres un robot.'})

        username = request.POST.get('username')
        email = request.POST.get('email')

        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'error': 'El nombre de usuario ya está en uso.'})

        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'error': 'El correo electrónico ya está en uso.'})

        if form.is_valid():
            password = form.cleaned_data['password']
            User.objects.create_user(username=username, email=email, password=password)
            return JsonResponse({'success': True, 'message': 'Registro exitoso. Ahora puedes iniciar sesión.'})
        else:
            errors = form.errors.get_json_data()
            print("Errores del Formulario:", errors)
            
            for field, error_list in errors.items():
                first_error = error_list[0]['message']
                return JsonResponse({'success': False, 'error': first_error})

    
    return JsonResponse({'success': False, 'error': 'Método no permitido.'})

#------------ Backup --------------#

def acciones_backup(request):
    config = BackupConfig.objects.first()  
    historial = BackupRegistro.objects.all().order_by('-fecha') 

    if not config:
        messages.info(request, "No se ha configurado el backup automático.")
        
    return render(request, 'usuarios/acciones.html', {'config': config, 'historial': historial})

def exportar_usuarios_sql(request):
    db_name = 'gestion_bd'
    table_name = 'gestion_usuarios_usuario'
    output_name = f"backup_usuarios_{now().strftime('%Y%m%d_%H%M%S')}.sql"
    media_dir = settings.MEDIA_ROOT
    output_path = os.path.join(media_dir, output_name)

    mysqldump_path = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe"  # Ruta de mysqldump

    if not os.path.exists(media_dir):
        os.makedirs(media_dir)

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            subprocess.run([mysqldump_path, '-u', 'root', '-padmin', db_name, table_name], stdout=f, check=True)

        BackupRegistro.objects.create(archivo=output_name)

        with open(output_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/sql')
            response['Content-Disposition'] = f'attachment; filename="{output_name}"'
            return response

    except subprocess.CalledProcessError as e:
        return HttpResponse(f"Error al exportar: {str(e)}", content_type='text/plain')


def importar_usuarios_sql(request):
    if request.method == 'POST' and request.FILES.get('archivo_sql'):
        archivo = request.FILES['archivo_sql']
        ruta_archivo = default_storage.save('temporal.sql', archivo)
        full_path = os.path.join(settings.MEDIA_ROOT, ruta_archivo)

        mysql_path = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
        db_name = 'gestion_bd'

        command = f'"{mysql_path}" -u root -padmin {db_name} < "{full_path}"'

        try:
            subprocess.run(command, shell=True, check=True)
            BackupRegistro.objects.create(archivo=archivo.name)
            os.remove(full_path)

            return HttpResponse("Importación realizada con éxito.")
        except subprocess.CalledProcessError as e:
            return HttpResponse(f"Error al importar el archivo SQL:<br>{e}", content_type='text/html')

    return render(request, 'usuarios/importar_sql.html')

def guardar_config_backup(request):
    if request.method == 'POST':
        hora_backup = request.POST.get('hora_backup')
        activa = 'activa' in request.POST
        print(f"Valor recibido de hora_backup: {hora_backup}") 

        if not hora_backup:
            messages.error(request, "Debes ingresar una hora válida para el backup.")
            return redirect('acciones_backup')

        try:
            if ":" in hora_backup:
                hora_backup = datetime.strptime(hora_backup, "%H:%M").time()
                print(f"Hora convertida a 24 horas: {hora_backup}")
            else:
                messages.error(request, "Formato de hora inválido.")
                return redirect('acciones_backup')

        except ValueError:
            messages.error(request, "Formato de hora inválido.")
            return redirect('acciones_backup')

        config, created = BackupConfig.objects.get_or_create(id=1)
        config.hora_backup = hora_backup
        config.activa = activa
        config.save()

        messages.success(request, "Configuración de backup guardada correctamente.")
        print(f"Salio de guardar configig",request )
        return redirect('acciones_backup')

    return render(request, 'usuarios/acciones.html')


def descargar_backup(request, archivo_nombre):
    media_dir = settings.MEDIA_ROOT
    archivo_path = os.path.join(media_dir, archivo_nombre)

    if not os.path.exists(archivo_path):
        return HttpResponse("Archivo no encontrado.", status=404)

    response = FileResponse(open(archivo_path, 'rb'))
    response['Content-Disposition'] = f'attachment; filename="{smart_str(archivo_nombre)}"'
    return response

def visualizar_backup(request, archivo_nombre):
    media_dir = settings.MEDIA_ROOT
    archivo_path = os.path.join(media_dir, archivo_nombre)

    if not os.path.exists(archivo_path):
        return HttpResponse("Archivo no encontrado.", status=404)

    with open(archivo_path, 'r', encoding='utf-8', errors='ignore') as f:
        contenido = f.read()

    return HttpResponse(f"<pre>{contenido}</pre>")

def ejecutar_sql_mysql(sql):
    mysql_path = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
    comando = f'"{mysql_path}" -u root -padmin -e "{sql}"'
    
    try:
        subprocess.run(comando, shell=True, check=True)
        print(f"✔️ Comando ejecutado:\n{sql}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar comando SQL:\n{sql}\nError: {e}")