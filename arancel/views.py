from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Seccion, Partida, Subpartida, Capitulo
from .forms import SeccionForm
from django.views.decorators.http import require_GET
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib import messages
from django.db import models
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_GET
from central.models import HistorialBusqueda, Reporte
from arancel.templatetags.custom_filters import is_descriptive_code
from difflib import get_close_matches
from difflib import get_close_matches
from django.db.models import Q # Asegúrate de que Q esté importado



# Utilidad interna: limpiar guiones bajos para respuestas JSON (sugerencias)
def _clean_text_for_json(value):
    if value is None:
        return ''
    try:
        return str(value).replace('_', ' ')
    except Exception:
        return str(value)

# Utilidad: Crear reporte de trazabilidad automáticamente
def _crear_reporte_busqueda(usuario, codigo, descripcion, tipo_accion, resultado='exitosa'):
    """Crea un registro de trazabilidad sin afectar el flujo de la aplicación."""
    try:
        Reporte.objects.create(
            usuario=usuario,
            codigo_arancelario=codigo,
            descripcion_clasificacion=descripcion[:500],  # Limitar a 500 caracteres
            tipo_accion=tipo_accion,
            resultado_operacion=resultado,
            detalles_adicionales=f'Búsqueda automática: {tipo_accion}'
        )
    except Exception:
        pass  # Si falla la creación de reporte, no afecta el flujo normal


@method_decorator(login_required, name='dispatch')
class SeccionListView(ListView):
    model = Seccion
    template_name = 'arancel/seccion_list.html'
    context_object_name = 'secciones'

@method_decorator(login_required, name='dispatch')
class SeccionCreateView(CreateView):
    model = Seccion
    form_class = SeccionForm
    template_name = 'arancel/seccion_form.html'
    success_url = reverse_lazy('arancel:seccion_list')

@method_decorator(login_required, name='dispatch')
class SeccionUpdateView(UpdateView):
    model = Seccion
    form_class = SeccionForm
    template_name = 'arancel/seccion_form.html'
    success_url = reverse_lazy('arancel:seccion_list')

@method_decorator(login_required, name='dispatch')
class SeccionDeleteView(DeleteView):
    model = Seccion
    template_name = 'arancel/seccion_confirm_delete.html'
    success_url = reverse_lazy('arancel:seccion_list')

@method_decorator(login_required, name='dispatch')
class SeccionDetailView(DetailView):
    model = Seccion
    template_name = 'arancel/seccion_detail.html'
    context_object_name = 'seccion'

@method_decorator(login_required, name='dispatch')
class CapituloDetailView(DetailView):
    model = Capitulo
    template_name = 'arancel/capitulo_detail.html'
    context_object_name = 'capitulo'

@method_decorator(login_required, name='dispatch')
class PartidaDetailView(DetailView):
    model = Partida
    template_name = 'arancel/partida_detail.html'
    context_object_name = 'partida'

@method_decorator(login_required, name='dispatch')
class SubpartidaDetailView(DetailView):
    model = Subpartida
    template_name = 'arancel/subpartida_detail.html'
    context_object_name = 'subpartida'

@login_required
def tabla_aranceles(request):
    query = request.GET.get('q', '').strip()
    secciones = Seccion.objects.prefetch_related('capitulos__partidas__subpartidas')
    if query:
        query_lower = query.lower()
        secciones_filtradas = []
        for seccion in secciones:
            capitulos_filtrados = []
            for capitulo in seccion.capitulos.all():
                partidas_filtradas = []
                for partida in capitulo.partidas.all():
                    subpartidas_filtradas = [s for s in partida.subpartidas.all() if query_lower in s.codigo.lower() or query_lower in s.descripcion.lower()]
                    if query_lower in partida.codigo.lower() or query_lower in partida.descripcion.lower() or subpartidas_filtradas:
                        partida.subpartidas_filtradas = subpartidas_filtradas if subpartidas_filtradas else list(partida.subpartidas.all())
                        partidas_filtradas.append(partida)
                if query_lower in capitulo.codigo.lower() or query_lower in capitulo.nombre.lower() or partidas_filtradas:
                    capitulo.partidas_filtradas = partidas_filtradas if partidas_filtradas else list(capitulo.partidas.all())
                    capitulos_filtrados.append(capitulo)
            if query_lower in seccion.nombre.lower() or capitulos_filtrados:
                seccion.capitulos_filtrados = capitulos_filtrados if capitulos_filtrados else list(seccion.capitulos.all())
                secciones_filtradas.append(seccion)
        secciones = secciones_filtradas
    return render(request, 'arancel/tabla_aranceles.html', {'secciones': secciones, 'query': query})

def search_predictive(request):
    query = request.GET.get('q', '').strip()  # Obtén el término de búsqueda
    if not query:
        return JsonResponse([], safe=False)

    # Buscar por código exacto en partidas y subpartidas
    partidas = Partida.objects.filter(codigo__icontains=query)
    subpartidas = Subpartida.objects.filter(codigo__icontains=query)

    # Buscar por palabras en la descripción
    partidas_descripcion = Partida.objects.filter(descripcion__icontains=query)
    subpartidas_descripcion = Subpartida.objects.filter(descripcion__icontains=query)

    # Combinar resultados
    results = []
    for partida in partidas.union(partidas_descripcion):
        results.append({
            'type': 'partida',
            'codigo': _clean_text_for_json(partida.codigo),
            'descripcion': _clean_text_for_json(partida.descripcion),
        })

    for subpartida in subpartidas.union(subpartidas_descripcion):
        results.append({
            'type': 'subpartida',
            'codigo': _clean_text_for_json(subpartida.codigo),
            'descripcion': _clean_text_for_json(subpartida.descripcion),
        })

    return JsonResponse(results, safe=False)

@login_required
def buscador_global(request):
    query = request.GET.get('q', '').strip()
    if not query:
        messages.warning(request, 'Por favor ingresa un término de búsqueda.')
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # --- Búsqueda EXACTA para redirección 1-a-1 ---
    # (Cambiamos __icontains por búsquedas exactas o 'startswith' para ser más precisos)
    partidas_exactas = Partida.objects.filter(codigo=query)
    subpartidas_exactas = Subpartida.objects.filter(codigo=query)
    
    # Si hay una sola partida EXACTA
    if partidas_exactas.count() == 1 and subpartidas_exactas.count() == 0:
        partida = partidas_exactas.first()
        HistorialBusqueda.objects.create(
            usuario=request.user, termino_busqueda=query,
            tipo_resultado='Partida', id_resultado=partida.id
        )
        # Crear reporte de trazabilidad
        _crear_reporte_busqueda(
            request.user, 
            partida.codigo, 
            partida.descripcion, 
            'consulta_detalle'
        )
        return redirect('arancel:partida_detail', pk=partida.id)

    # Si hay una sola subpartida EXACTA
    if subpartidas_exactas.count() == 1 and partidas_exactas.count() == 0:
        subpartida = subpartidas_exactas.first()
        # ... (Tu lógica de historial y redirect a subpartida)
        if is_descriptive_code(subpartida.codigo):
            HistorialBusqueda.objects.create(
                usuario=request.user, termino_busqueda=query,
                tipo_resultado='Subpartida', id_resultado=subpartida.id
            )
            # Crear reporte de trazabilidad
            _crear_reporte_busqueda(
                request.user,
                subpartida.codigo,
                subpartida.descripcion,
                'consulta_detalle'
            )
            return redirect(f'/arancel/partidas/{subpartida.partida.id}/?highlight={subpartida.id}')
        else:
            HistorialBusqueda.objects.create(
                usuario=request.user, termino_busqueda=query,
                tipo_resultado='Subpartida', id_resultado=subpartida.id
            )
            # Crear reporte de trazabilidad
            _crear_reporte_busqueda(
                request.user,
                subpartida.codigo,
                subpartida.descripcion,
                'consulta_detalle'
            )
            return redirect('arancel:subpartida_detail', pk=subpartida.id)

    # Búsqueda exacta en Capítulos y Secciones
    capitulo = Capitulo.objects.filter(Q(codigo=query) | Q(nombre__iexact=query)).first()
    if capitulo:
        HistorialBusqueda.objects.create(
            usuario=request.user, termino_busqueda=query,
            tipo_resultado='Capítulo', id_resultado=capitulo.id
        )
        # Crear reporte de trazabilidad
        _crear_reporte_busqueda(
            request.user,
            capitulo.codigo,
            capitulo.nombre,
            'consulta_detalle'
        )
        return redirect('arancel:capitulo_detail', pk=capitulo.id)

    seccion = Seccion.objects.filter(nombre__iexact=query).first()
    if seccion:
        HistorialBusqueda.objects.create(
            usuario=request.user, termino_busqueda=query,
            tipo_resultado='Sección', id_resultado=seccion.id
        )
        # Crear reporte de trazabilidad
        _crear_reporte_busqueda(
            request.user,
            '',  # Las secciones no tienen código
            seccion.nombre,
            'consulta_detalle'
        )
        return redirect('arancel:seccion_detail', pk=seccion.id)

    # --- Si no hay NINGUNA coincidencia exacta 1-a-1 ---
    # Redirigir a la página de resultados. 
    # Esta página se encargará de buscar por __icontains Y de buscar sugerencias.
    return redirect(f"/arancel/resultados_busqueda/?q={query}")

@require_GET
def autocomplete_arancel(request):
    from difflib import SequenceMatcher, get_close_matches
    from django.db.models import Q
    
    def calcular_similitud(texto1, texto2):
        """Calcular similitud entre dos textos usando SequenceMatcher"""
        return SequenceMatcher(None, texto1.lower(), texto2.lower()).ratio()
    
    def calcular_distancia_edicion(s1, s2):
        """Calcular distancia de Levenshtein simplificada para códigos"""
        if len(s1) < len(s2):
            s1, s2 = s2, s1
        if len(s2) == 0:
            return len(s1)
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]
    
    def calcular_puntaje_item(item, query, es_codigo=False):
        """Calcular el mejor puntaje de similitud para un item"""
        textos_a_comparar = []
        puntajes = []
        
        if hasattr(item, 'codigo'):
            textos_a_comparar.append(item.codigo)
        if hasattr(item, 'nombre'):
            textos_a_comparar.append(item.nombre)
        if hasattr(item, 'descripcion'):
            textos_a_comparar.append(item.descripcion or '')
        
        for texto in textos_a_comparar:
            if texto:
                if es_codigo and hasattr(item, 'codigo') and texto == item.codigo:
                    # Para códigos, usar distancia de edición
                    distancia = calcular_distancia_edicion(texto, query)
                    longitud_max = max(len(texto), len(query))
                    similitud = 1 - (distancia / longitud_max) if longitud_max > 0 else 0
                    puntajes.append(similitud)
                else:
                    # Para descripciones, usar similitud de secuencia
                    similitud = calcular_similitud(texto, query)
                    # Bonus si la búsqueda está al inicio
                    if texto.lower().startswith(query.lower()):
                        similitud += 0.1
                    puntajes.append(similitud)
        
        return max(puntajes) if puntajes else 0

    query = request.GET.get('q', '').strip()
    results = []
    
    if query and len(query) >= 1:
        query_lower = query.lower()
        
        # Determinar si la búsqueda parece ser un código (principalmente números)
        es_codigo = any(c.isdigit() for c in query) or len(query) <= 10
        
        # Búsqueda exacta primero (preferencia alta)
        secciones_exactas = Seccion.objects.filter(
            Q(nombre__iexact=query) | Q(nombre__istartswith=query) |
            Q(descripcion__iexact=query)
        )
        capitulos_exactos = Capitulo.objects.filter(
            Q(codigo__iexact=query) | Q(codigo__startswith=query) |
            Q(nombre__iexact=query) | Q(nombre__istartswith=query)
        )
        partidas_exactas = Partida.objects.filter(
            Q(codigo__iexact=query) | Q(codigo__startswith=query) |
            Q(descripcion__iexact=query) | Q(descripcion__istartswith=query)
        )
        subpartidas_exactas = Subpartida.objects.filter(
            Q(codigo__iexact=query) | Q(codigo__startswith=query) |
            Q(descripcion__iexact=query) | Q(descripcion__istartswith=query)
        )
        
        # Búsqueda aproximada (contenido)
        secciones_aprox = Seccion.objects.filter(
            Q(nombre__icontains=query) | Q(descripcion__icontains=query)
        ).exclude(id__in=[s.id for s in secciones_exactas])
        
        capitulos_aprox = Capitulo.objects.filter(
            Q(codigo__icontains=query) | Q(nombre__icontains=query)
        ).exclude(id__in=[c.id for c in capitulos_exactos])
        
        partidas_aprox = Partida.objects.filter(
            Q(codigo__icontains=query) | Q(descripcion__icontains=query)
        ).exclude(id__in=[p.id for p in partidas_exactas])
        
        subpartidas_aprox = Subpartida.objects.filter(
            Q(codigo__icontains=query) | Q(descripcion__icontains=query)
        ).exclude(id__in=[s.id for s in subpartidas_exactas])
        
        # Crear lista de resultados con puntajes
        resultados_con_puntaje = []
        
        # Agregar resultados exactos con puntaje alto
        for s in secciones_exactas:
            resultados_con_puntaje.append({
                'tipo': 'Sección',
                'id': s.id,
                'nombre': _clean_text_for_json(s.nombre),
                'descripcion': _clean_text_for_json(s.descripcion or ''),
                'puntaje': 1.0,
                'es_correccion': query != s.nombre
            })
        
        for c in capitulos_exactos:
            resultados_con_puntaje.append({
                'tipo': 'Capítulo',
                'id': c.id,
                'codigo': _clean_text_for_json(c.codigo),
                'nombre': _clean_text_for_json(c.nombre),
                'descripcion': _clean_text_for_json(c.descripcion or ''),
                'puntaje': 0.95,
                'es_correccion': query != c.codigo
            })
        
        for p in partidas_exactas:
            resultados_con_puntaje.append({
                'tipo': 'Partida',
                'id': p.id,
                'codigo': _clean_text_for_json(p.codigo),
                'descripcion': _clean_text_for_json(p.descripcion),
                'puntaje': 0.9 if es_codigo else 0.85,
                'es_correccion': query != p.codigo
            })
        
        for s in subpartidas_exactas:
            titulo_desc = ''
            anteriores = Subpartida.objects.filter(partida=s.partida, id__lt=s.id).order_by('-id')
            for ant in anteriores:
                if is_descriptive_code(ant.codigo):
                    titulo_desc = ant.descripcion
                    break
            resultados_con_puntaje.append({
                'tipo': 'Subpartida',
                'id': s.id,
                'codigo': _clean_text_for_json(s.codigo),
                'descripcion': _clean_text_for_json(s.descripcion),
                'titulo_desc': _clean_text_for_json(titulo_desc),
                'puntaje': 0.9 if es_codigo else 0.85,
                'es_correccion': query != s.codigo
            })
        
        # Agregar resultados aproximados con puntaje basado en similitud
        for s in secciones_aprox:
            puntaje = calcular_puntaje_item(s, query_lower)
            if puntaje > 0.25:  # Umbral mínimo de similitud reducido
                resultados_con_puntaje.append({
                    'tipo': 'Sección',
                    'id': s.id,
                    'nombre': _clean_text_for_json(s.nombre),
                    'descripcion': _clean_text_for_json(s.descripcion or ''),
                    'puntaje': puntaje,
                    'es_correccion': False
                })
        
        for c in capitulos_aprox:
            puntaje = calcular_puntaje_item(c, query_lower, es_codigo)
            if puntaje > 0.25:
                resultados_con_puntaje.append({
                    'tipo': 'Capítulo',
                    'id': c.id,
                    'codigo': _clean_text_for_json(c.codigo),
                    'nombre': _clean_text_for_json(c.nombre),
                    'descripcion': _clean_text_for_json(c.descripcion or ''),
                    'puntaje': puntaje,
                    'es_correccion': False
                })
        
        for p in partidas_aprox:
            puntaje = calcular_puntaje_item(p, query_lower, es_codigo)
            if puntaje > 0.25:
                resultados_con_puntaje.append({
                    'tipo': 'Partida',
                    'id': p.id,
                    'codigo': _clean_text_for_json(p.codigo),
                    'descripcion': _clean_text_for_json(p.descripcion),
                    'puntaje': puntaje,
                    'es_correccion': False
                })
        
        for s in subpartidas_aprox:
            puntaje = calcular_puntaje_item(s, query_lower, es_codigo)
            if puntaje > 0.25:
                titulo_desc = ''
                anteriores = Subpartida.objects.filter(partida=s.partida, id__lt=s.id).order_by('-id')
                for ant in anteriores:
                    if is_descriptive_code(ant.codigo):
                        titulo_desc = ant.descripcion
                        break
                resultados_con_puntaje.append({
                    'tipo': 'Subpartida',
                    'id': s.id,
                    'codigo': _clean_text_for_json(s.codigo),
                    'descripcion': _clean_text_for_json(s.descripcion),
                    'titulo_desc': _clean_text_for_json(titulo_desc),
                    'puntaje': puntaje,
                    'es_correccion': False
                })
        
        # Si no hay resultados suficientes (menos de 3), buscar sugerencias de corrección basadas en similitud de texto
        if len(resultados_con_puntaje) < 3:
            # Buscar sugerencias para códigos
            if es_codigo:
                todos_codigos = []
                todos_codigos.extend([(p.codigo, p.id, 'Partida') for p in Partida.objects.all()])
                todos_codigos.extend([(s.codigo, s.id, 'Subpartida') for s in Subpartida.objects.all()])
                todos_codigos.extend([(c.codigo, c.id, 'Capítulo') for c in Capitulo.objects.all()])
                
                sugerencias_codigos = get_close_matches(
                    query,
                    [codigo for codigo, _, _ in todos_codigos],
                    n=8,
                    cutoff=0.3  # Más permisivo para encontrar sugerencias
                )
                
                for codigo_sugerido in sugerencias_codigos:
                    # Encontrar el item correspondiente
                    for codigo, item_id, tipo in todos_codigos:
                        if codigo == codigo_sugerido:
                            similitud_codigo = calcular_similitud(query, codigo)
                            if similitud_codigo > 0.35:  # Asegurar similitud mínima
                                if tipo == 'Partida':
                                    item = Partida.objects.get(id=item_id)
                                    resultados_con_puntaje.append({
                                        'tipo': 'Partida',
                                        'id': item.id,
                                        'codigo': _clean_text_for_json(item.codigo),
                                        'descripcion': _clean_text_for_json(item.descripcion),
                                        'puntaje': 0.65,
                                        'es_correccion': True
                                    })
                                elif tipo == 'Subpartida':
                                    item = Subpartida.objects.get(id=item_id)
                                    titulo_desc = ''
                                    anteriores = Subpartida.objects.filter(partida=item.partida, id__lt=item.id).order_by('-id')
                                    for ant in anteriores:
                                        if is_descriptive_code(ant.codigo):
                                            titulo_desc = ant.descripcion
                                            break
                                    resultados_con_puntaje.append({
                                        'tipo': 'Subpartida',
                                        'id': item.id,
                                        'codigo': _clean_text_for_json(item.codigo),
                                        'descripcion': _clean_text_for_json(item.descripcion),
                                        'titulo_desc': _clean_text_for_json(titulo_desc),
                                        'puntaje': 0.65,
                                        'es_correccion': True
                                    })
                                elif tipo == 'Capítulo':
                                    item = Capitulo.objects.get(id=item_id)
                                    resultados_con_puntaje.append({
                                        'tipo': 'Capítulo',
                                        'id': item.id,
                                        'codigo': _clean_text_for_json(item.codigo),
                                        'nombre': _clean_text_for_json(item.nombre),
                                        'descripcion': _clean_text_for_json(item.descripcion or ''),
                                        'puntaje': 0.65,
                                        'es_correccion': True
                                    })
                            break
            
            # Buscar sugerencias para descripciones (palabras mal escritas)
            if not es_codigo and len(resultados_con_puntaje) == 0:
                # Obtener todas las descripciones y buscar las más similares
                all_items = []
                
                # Partidas
                for p in Partida.objects.all():
                    similitud = calcular_similitud(query_lower, p.descripcion.lower())
                    if similitud > 0.35:
                        all_items.append((similitud, 'Partida', p))
                
                # Subpartidas
                for s in Subpartida.objects.all():
                    similitud = calcular_similitud(query_lower, s.descripcion.lower())
                    if similitud > 0.35:
                        all_items.append((similitud, 'Subpartida', s))
                
                # Capítulos
                for c in Capitulo.objects.all():
                    similitud = calcular_similitud(query_lower, c.nombre.lower())
                    if similitud > 0.35:
                        all_items.append((similitud, 'Capítulo', c))
                    if c.descripcion:
                        similitud = calcular_similitud(query_lower, c.descripcion.lower())
                        if similitud > 0.35:
                            all_items.append((similitud, 'Capítulo', c))
                
                # Secciones
                for s in Seccion.objects.all():
                    similitud = calcular_similitud(query_lower, s.nombre.lower())
                    if similitud > 0.35:
                        all_items.append((similitud, 'Sección', s))
                    if s.descripcion:
                        similitud = calcular_similitud(query_lower, s.descripcion.lower())
                        if similitud > 0.35:
                            all_items.append((similitud, 'Sección', s))
                
                # Ordenar por similitud y tomar los mejores
                all_items.sort(key=lambda x: x[0], reverse=True)
                
                for similitud, tipo, item in all_items[:8]:  # Limitar a 8 sugerencias
                    if tipo == 'Partida':
                        resultados_con_puntaje.append({
                            'tipo': 'Partida',
                            'id': item.id,
                            'codigo': _clean_text_for_json(item.codigo),
                            'descripcion': _clean_text_for_json(item.descripcion),
                            'puntaje': similitud * 0.8,
                            'es_correccion': True
                        })
                    elif tipo == 'Subpartida':
                        titulo_desc = ''
                        anteriores = Subpartida.objects.filter(partida=item.partida, id__lt=item.id).order_by('-id')
                        for ant in anteriores:
                            if is_descriptive_code(ant.codigo):
                                titulo_desc = ant.descripcion
                                break
                        resultados_con_puntaje.append({
                            'tipo': 'Subpartida',
                            'id': item.id,
                            'codigo': _clean_text_for_json(item.codigo),
                            'descripcion': _clean_text_for_json(item.descripcion),
                            'titulo_desc': _clean_text_for_json(titulo_desc),
                            'puntaje': similitud * 0.8,
                            'es_correccion': True
                        })
                    elif tipo == 'Capítulo':
                        resultados_con_puntaje.append({
                            'tipo': 'Capítulo',
                            'id': item.id,
                            'codigo': _clean_text_for_json(item.codigo),
                            'nombre': _clean_text_for_json(item.nombre),
                            'descripcion': _clean_text_for_json(item.descripcion or ''),
                            'puntaje': similitud * 0.8,
                            'es_correccion': True
                        })
                    elif tipo == 'Sección':
                        resultados_con_puntaje.append({
                            'tipo': 'Sección',
                            'id': item.id,
                            'nombre': _clean_text_for_json(item.nombre),
                            'descripcion': _clean_text_for_json(item.descripcion or ''),
                            'puntaje': similitud * 0.8,
                            'es_correccion': True
                        })
        
        # Ordenar por puntaje de mayor a menor
        resultados_con_puntaje.sort(key=lambda x: x['puntaje'], reverse=True)
        
        # Limitar resultados y remover duplicados
        resultados_unicos = {}
        for item in resultados_con_puntaje:
            clave = f"{item['tipo']}-{item['id']}"
            if clave not in resultados_unicos or item['puntaje'] > resultados_unicos[clave]['puntaje']:
                resultados_unicos[clave] = item
        
        # Tomar los mejores 12 resultados
        results = list(resultados_unicos.values())[:12]
        
    return JsonResponse(results, safe=False)

@login_required
@login_required
def prevalidacion_view(request):
    """Vista para la página de pre-validación de requisitos."""
    return render(request, 'arancel/prevalidacion.html')

@login_required
@require_GET
def prevalidacion_api(request, codigo):
    """API para obtener información de pre-validación de un código arancelario."""
    try:
        # Intentar encontrar primero como subpartida
        subpartida = Subpartida.objects.get(codigo=codigo)
        
        # Crear reporte de trazabilidad
        _crear_reporte_busqueda(
            request.user,
            subpartida.codigo,
            subpartida.descripcion,
            'consulta_detalle'
        )
        
        response_data = {
            'codigo': subpartida.codigo,
            'descripcion': subpartida.descripcion,
            'requiere_permiso': subpartida.requiere_permiso,
            'detalle_permiso': subpartida.detalle_permiso,
            'entidad_permiso': subpartida.entidad_permiso,
            'requiere_licencia': subpartida.requiere_licencia,
            'detalle_licencia': subpartida.detalle_licencia,
            'entidad_licencia': subpartida.entidad_licencia,
            'requiere_cupo': subpartida.requiere_cupo,
            'detalle_cupo': subpartida.detalle_cupo,
            'entidad_cupo': subpartida.entidad_cupo,
            'instrucciones_validacion': subpartida.instrucciones_validacion,
            'tipo_de_doc': subpartida.tipo_de_doc,
            'entidad_que_emite': subpartida.entidad_que_emite,
            'disposicion_legal': subpartida.disposicion_legal,
        }
        
        return JsonResponse(response_data)
        
    except ObjectDoesNotExist:
        return JsonResponse({
            'error': 'Código arancelario no encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'error': f'Error al procesar la solicitud: {str(e)}'
        }, status=500)

def resultados_busqueda(request):
    query = request.GET.get('q', '').strip()
    
    # 1. Búsqueda normal con __icontains
    partidas = Partida.objects.filter(Q(codigo__icontains=query) | Q(descripcion__icontains=query))
    subpartidas = Subpartida.objects.filter(Q(codigo__icontains=query) | Q(descripcion__icontains=query))
    
    total_results = partidas.count() + subpartidas.count()
    
    sugerencias_codigos = []
    sugerencias_desc = []
    
    # 2. Si no hay resultados, ¡activar búsqueda "fuzzy" con difflib!
    if total_results == 0 and query:
        
        # Criterio 1: Corrección de Código Arancelario
        # (Usamos tu import 'get_close_matches' que ya tienes)
        es_codigo = any(char.isdigit() for char in query)
        if es_codigo:
            # Traemos todos los códigos a memoria. (Advertencia: Lento)
            todos_codigos_partida = list(Partida.objects.values_list('codigo', flat=True))
            todos_codigos_subpartida = list(Subpartida.objects.values_list('codigo', flat=True))
            todos_los_codigos = todos_codigos_partida + todos_codigos_subpartida
            
            # Usamos get_close_matches. Es simple y directo.
            # n=5 (trae 5 sugerencias), cutoff=0.8 (80% de similitud)
            resultados_codigos = get_close_matches(query, todos_los_codigos, n=5, cutoff=0.8)
            
            if resultados_codigos:
                sugerencias_codigos = Subpartida.objects.filter(codigo__in=resultados_codigos).union(
                                        Partida.objects.filter(codigo__in=resultados_codigos)
                                      )

        # Criterio 2: Alternativas de Descripción (si no es un código o no hubo sugerencias de código)
        if not es_codigo or not sugerencias_codigos:
            
            # ⚠️ ADVERTENCIA: Esta parte es MUY lenta en SQLite.
            # Carga todas las descripciones a memoria.
            desc_map_partidas = {p.descripcion: p for p in Partida.objects.all()}
            desc_map_subpartidas = {s.descripcion: s for s in Subpartida.objects.all()}
            
            # Unimos los textos de las descripciones
            todas_las_descripciones = list(desc_map_partidas.keys()) + list(desc_map_subpartidas.keys())
            
            # Buscamos sugerencias. Usamos un cutoff más bajo (ej: 60%) para descripciones.
            resultados_desc = get_close_matches(query, todas_las_descripciones, n=5, cutoff=0.6)
            
            sugerencias_desc_obj = []
            for desc_texto in resultados_desc:
                if desc_texto in desc_map_partidas:
                    sugerencias_desc_obj.append(desc_map_partidas[desc_texto])
                elif desc_texto in desc_map_subpartidas:
                    sugerencias_desc_obj.append(desc_map_subpartidas[desc_texto])
            
            sugerencias_desc = sugerencias_desc_obj


    # 3. Registrar en historial (ahora la lógica está en el lugar correcto)
    if query and request.user.is_authenticated:
        tipo_resultado = 'Resultados múltiples'
        if total_results == 0 and not sugerencias_codigos and not sugerencias_desc:
            # Solo si no hay resultados Y TAMPOCO sugerencias
            tipo_resultado = 'Sin resultado'
        
        # Evitar duplicados si el usuario recarga
        if not HistorialBusqueda.objects.filter(usuario=request.user, termino_busqueda=query).exists():
            HistorialBusqueda.objects.create(
                usuario=request.user,
                termino_busqueda=query,
                tipo_resultado=tipo_resultado,
                id_resultado=None
            )
            
    # 4. Renderizar la página
    return render(request, 'arancel/resultados_busqueda.html', {
        'query': query,
        'partidas': partidas,
        'subpartidas': subpartidas,
        'sugerencias_codigos': sugerencias_codigos,   # <-- ¡Nuevos!
        'sugerencias_desc': sugerencias_desc,       # <-- ¡Nuevos!
    })