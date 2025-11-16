from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User 
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils import timezone
import openpyxl
from openpyxl.styles import Font
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from .forms import HistorialBusquedaFilterForm
from django.contrib.auth.forms import UserCreationForm
from arancel.models import Seccion, Capitulo, Partida, Subpartida
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from .models import HistorialBusqueda, Rol, PerfilUsuario
from .forms import RegistroUsuarioForm
from django.contrib.auth.decorators import permission_required
from django.db.models import Avg, Max, Min

def es_superusuario_o_tiene_permiso_usuarios(user):
    return user.is_superuser or (hasattr(user, 'perfil') and user.perfil.rol and user.perfil.rol.permisos_usuarios)

@login_required
def home(request):
    total_secciones = Seccion.objects.count()
    total_capitulos = Capitulo.objects.count()
    total_partidas = Partida.objects.count()
    total_subpartidas = Subpartida.objects.count()
    
    # Obtener historial de búsquedas del usuario (últimas 10)
    historial = HistorialBusqueda.objects.filter(usuario=request.user)[:10]
    
    return render(request, 'home.html', {
        'total_secciones': total_secciones,
        'total_capitulos': total_capitulos,
        'total_partidas': total_partidas,
        'total_subpartidas': total_subpartidas,
        'historial_busquedas': historial,
    })

@login_required
def limpiar_historial(request):
    if request.method == 'POST':
        HistorialBusqueda.objects.filter(usuario=request.user).delete()
        messages.success(request, 'Historial de búsquedas limpiado correctamente.')
    return redirect('central:home')

@login_required
@user_passes_test(es_superusuario_o_tiene_permiso_usuarios)
def gestionar_usuarios(request):
    usuarios = User.objects.all().order_by('username')
    roles = Rol.objects.all().order_by('nombre')
    
    if request.method == 'POST':
        usuario_id = request.POST.get('usuario_id')
        rol_id = request.POST.get('rol_id')
        accion = request.POST.get('accion')
        
        if accion == 'asignar_rol':
            usuario = get_object_or_404(User, id=usuario_id)
            rol = get_object_or_404(Rol, id=rol_id) if rol_id else None
            
            perfil, created = PerfilUsuario.objects.get_or_create(usuario=usuario)
            perfil.rol = rol
            perfil.save()
            
            messages.success(request, f'Rol "{rol.nombre if rol else "Sin rol"}" asignado a {usuario.username}')
            
        elif accion == 'activar_desactivar':
            usuario = get_object_or_404(User, id=usuario_id)
            perfil, created = PerfilUsuario.objects.get_or_create(usuario=usuario)
            perfil.activo = not perfil.activo
            perfil.save()
            
            estado = "activado" if perfil.activo else "desactivado"
            messages.success(request, f'Usuario {usuario.username} {estado}')
        elif accion == 'eliminar_usuario':
            usuario = get_object_or_404(User, id=usuario_id)
            if usuario.is_superuser:
                messages.error(request, 'No puedes eliminar un superusuario desde esta interfaz.')
            else:
                usuario.delete()
                messages.success(request, f'Usuario {usuario.username} eliminado correctamente.')
    
    return render(request, 'central/gestionar_usuarios.html', {
        'usuarios': usuarios,
        'roles': roles,
    })

@login_required
@user_passes_test(es_superusuario_o_tiene_permiso_usuarios)
def gestionar_roles(request):
    roles = Rol.objects.all().order_by('nombre')
    
    if request.method == 'POST':
        accion = request.POST.get('accion')
        
        if accion == 'crear_rol':
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion', '')
            permisos_arancel = request.POST.get('permisos_arancel') == 'on'
            permisos_admin = request.POST.get('permisos_admin') == 'on'
            permisos_usuarios = request.POST.get('permisos_usuarios') == 'on'
            
            if nombre:
                # Verificar que no se duplique un rol del sistema
                if nombre.lower() in ['administrador', 'despachador de aduana']:
                    messages.error(request, f'El rol "{nombre}" ya existe en el sistema.')
                else:
                    rol = Rol.objects.create(
                        nombre=nombre,
                        descripcion=descripcion,
                        permisos_arancel=permisos_arancel,
                        permisos_admin=permisos_admin,
                        permisos_usuarios=permisos_usuarios
                    )
                    messages.success(request, f'Rol "{rol.nombre}" creado exitosamente')
            else:
                messages.error(request, 'El nombre del rol es obligatorio')
                
        elif accion == 'editar_rol':
            rol_id = request.POST.get('rol_id')
            rol = get_object_or_404(Rol, id=rol_id)
            
            # Permitir editar descripción y permisos de roles del sistema, pero no el nombre
            if rol.nombre in ['Administrador', 'Despachador de Aduana']:
                rol.descripcion = request.POST.get('descripcion', rol.descripcion)
                rol.permisos_arancel = request.POST.get('permisos_arancel') == 'on'
                rol.permisos_admin = request.POST.get('permisos_admin') == 'on'
                rol.permisos_usuarios = request.POST.get('permisos_usuarios') == 'on'
                rol.save()
                messages.success(request, f'Permisos del rol "{rol.nombre}" actualizados exitosamente')
            else:
                # Para roles personalizados, permitir editar todo
                rol.nombre = request.POST.get('nombre', rol.nombre)
                rol.descripcion = request.POST.get('descripcion', rol.descripcion)
                rol.permisos_arancel = request.POST.get('permisos_arancel') == 'on'
                rol.permisos_admin = request.POST.get('permisos_admin') == 'on'
                rol.permisos_usuarios = request.POST.get('permisos_usuarios') == 'on'
                rol.save()
                messages.success(request, f'Rol "{rol.nombre}" actualizado exitosamente')
            
        elif accion == 'eliminar_rol':
            rol_id = request.POST.get('rol_id')
            rol = get_object_or_404(Rol, id=rol_id)
            
            # Proteger roles del sistema
            if rol.nombre in ['Administrador', 'Despachador de Aduana']:
                messages.error(request, f'No se puede eliminar el rol "{rol.nombre}" porque es un rol del sistema.')
            else:
                # Verificar si hay usuarios usando este rol
                usuarios_con_rol = PerfilUsuario.objects.filter(rol=rol).count()
                if usuarios_con_rol > 0:
                    messages.error(request, f'No se puede eliminar el rol "{rol.nombre}" porque {usuarios_con_rol} usuario(s) lo están usando')
                else:
                    rol.delete()
                    messages.success(request, f'Rol "{rol.nombre}" eliminado exitosamente')
    
    return render(request, 'central/gestionar_roles.html', {
        'roles': roles,
    })

def register_view(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Crear perfil de usuario por defecto
            PerfilUsuario.objects.create(usuario=user)
            messages.success(request, 'Usuario registrado correctamente. Ahora puedes iniciar sesión.')
            return redirect('login')
        else:
            messages.error(request, 'Error en el registro. Por favor, verifica los datos.')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Verificar si el usuario está activo
            try:
                perfil = user.perfil
                if not perfil.activo:
                    messages.error(request, 'Tu cuenta ha sido desactivada. Contacta al administrador.')
                    return render(request, 'registration/login.html')
            except PerfilUsuario.DoesNotExist:
                # Si no tiene perfil, crear uno por defecto
                PerfilUsuario.objects.create(usuario=user)
            
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    return render(request, 'registration/login.html')

def logout_view(request):
    logout(request) 
    return redirect('login')    

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario registrado correctamente. Ahora puedes iniciar sesión.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})    

@login_required
@user_passes_test(es_superusuario_o_tiene_permiso_usuarios)
def panel_admin_simplificado(request):
    """Panel de administración simplificado para usuarios con permisos de admin"""
    # Obtener estadísticas
    total_usuarios = User.objects.count()
    usuarios_activos = PerfilUsuario.objects.filter(activo=True).count()
    total_roles = Rol.objects.count()
    total_busquedas = HistorialBusqueda.objects.count()
    
    return render(request, 'central/panel_admin_simplificado.html', {
        'total_usuarios': total_usuarios,
        'usuarios_activos': usuarios_activos,
        'total_roles': total_roles,
        'total_busquedas': total_busquedas,
    })

@login_required
def admin_redirect(request):
    """Redirige a usuarios según sus permisos"""
    if request.user.is_superuser:
        # Superusuarios van al admin completo
        return redirect('/admin/')
    elif hasattr(request.user, 'perfil') and request.user.perfil.rol and request.user.perfil.rol.permisos_admin:
        # Usuarios con permisos admin van al panel simplificado
        return redirect('panel_admin_simplificado')
    else:
        # Usuarios sin permisos van al home
        messages.warning(request, 'No tienes permisos para acceder al panel de administración.')
        return redirect('home')    

class HistorialBusquedaListView(LoginRequiredMixin, ListView):
    model = HistorialBusqueda
    template_name = 'central/historial_busquedas.html'
    context_object_name = 'historial'
    paginate_by = 20

    def get_queryset(self):
        queryset = HistorialBusqueda.objects.all()
        form = HistorialBusquedaFilterForm(self.request.GET)
        
        if form.is_valid():
            if form.cleaned_data['fecha_inicio']:
                queryset = queryset.filter(fecha_busqueda__date__gte=form.cleaned_data['fecha_inicio'])
            if form.cleaned_data['fecha_fin']:
                queryset = queryset.filter(fecha_busqueda__date__lte=form.cleaned_data['fecha_fin'])
            if form.cleaned_data['tipo_resultado']:
                queryset = queryset.filter(tipo_resultado=form.cleaned_data['tipo_resultado'])
            if form.cleaned_data['palabra_clave']:
                queryset = queryset.filter(
                    Q(termino_busqueda__icontains=form.cleaned_data['palabra_clave']) |
                    Q(usuario__username__icontains=form.cleaned_data['palabra_clave'])
                )
        
        return queryset.select_related('usuario')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = HistorialBusquedaFilterForm(self.request.GET)
        return context

def exportar_historial(request):
    # Obtener los datos filtrados
    queryset = HistorialBusqueda.objects.all()
    form = HistorialBusquedaFilterForm(request.GET)
    
    if form.is_valid():
        if form.cleaned_data['fecha_inicio']:
            queryset = queryset.filter(fecha_busqueda__date__gte=form.cleaned_data['fecha_inicio'])
        if form.cleaned_data['fecha_fin']:
            queryset = queryset.filter(fecha_busqueda__date__lte=form.cleaned_data['fecha_fin'])
        if form.cleaned_data['tipo_resultado']:
            queryset = queryset.filter(tipo_resultado=form.cleaned_data['tipo_resultado'])
        if form.cleaned_data['palabra_clave']:
            queryset = queryset.filter(
                Q(termino_busqueda__icontains=form.cleaned_data['palabra_clave']) |
                Q(usuario__username__icontains=form.cleaned_data['palabra_clave'])
            )

    format_type = request.GET.get('format', 'pdf')

    if format_type == 'excel':
        # Crear un nuevo libro de Excel
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Historial de Búsquedas"

        # Agregar encabezados
        headers = ['Usuario', 'Término de búsqueda', 'Tipo de resultado', 'Fecha y hora']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col)
            cell.value = header
            cell.font = Font(bold=True)

        # Agregar datos
        for row, registro in enumerate(queryset, 2):
            ws.cell(row=row, column=1).value = registro.usuario.username
            ws.cell(row=row, column=2).value = registro.termino_busqueda
            ws.cell(row=row, column=3).value = registro.tipo_resultado or '--'
            ws.cell(row=row, column=4).value = registro.fecha_busqueda.strftime('%d/%m/%Y %H:%M')

        # Crear la respuesta HTTP con el archivo Excel
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=historial_busquedas.xlsx'
        wb.save(response)
        return response

    else:  # PDF
        # Crear el documento PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Estilo para el título
        styles = getSampleStyleSheet()
        elements.append(Paragraph('Historial de Búsquedas', styles['Heading1']))
        elements.append(Paragraph(f'Generado el {timezone.now().strftime("%d/%m/%Y %H:%M")}', styles['Normal']))

        # Datos para la tabla
        data = [['Usuario', 'Término de búsqueda', 'Tipo de resultado', 'Fecha y hora']]
        for registro in queryset:
            data.append([
                registro.usuario.username,
                registro.termino_busqueda,
                registro.tipo_resultado or '--',
                registro.fecha_busqueda.strftime('%d/%m/%Y %H:%M')
            ])

        # Crear la tabla
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)

        # Generar el PDF
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()

        # Crear la respuesta HTTP con el archivo PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=historial_busquedas.pdf'
        response.write(pdf)
        return response

@login_required
def estadisticas_gravamenes(request):
    """Vista para mostrar estadísticas de gravámenes arancelarios por capítulo"""
    # Obtener todos los capítulos
    capitulos = Capitulo.objects.all().order_by('codigo')
    
    # Lista para almacenar las estadísticas por capítulo
    estadisticas_por_capitulo = []
    
    for capitulo in capitulos:
        # Obtener todas las subpartidas de este capítulo a través de las partidas
        # Filtrar solo aquellas que tienen GA (no nulo)
        subpartidas = Subpartida.objects.filter(
            partida__capitulo=capitulo,
            ga__isnull=False
        )
        
        if subpartidas.exists():
            # Calcular estadísticas
            estadisticas = subpartidas.aggregate(
                promedio=Avg('ga'),
                maximo=Max('ga'),
                minimo=Min('ga')
            )
            
            # Agregar información del capítulo y estadísticas
            estadisticas_por_capitulo.append({
                'capitulo': capitulo,
                'promedio': estadisticas['promedio'],
                'maximo': estadisticas['maximo'],
                'minimo': estadisticas['minimo'],
                'cantidad_subpartidas': subpartidas.count()
            })
    
    return render(request, 'central/estadisticas_gravamenes.html', {
        'estadisticas': estadisticas_por_capitulo,
    })