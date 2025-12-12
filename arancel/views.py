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
from central.views import registrar_bitacora
from arancel.templatetags.custom_filters import is_descriptive_code
from arancel.sinonimos import obtener_sinonimos, expandir_busqueda_con_sinonimos, aplicar_sinonimos_a_query
from difflib import get_close_matches
from difflib import get_close_matches
from django.db.models import Q # Asegúrate de que Q esté importado
from spellchecker import SpellChecker
import re



# Utilidad interna: limpiar guiones bajos para respuestas JSON (sugerencias)
def _clean_text_for_json(value):
    if value is None:
        return ''
    try:
        return str(value).replace('_', ' ')
    except Exception:
        return str(value)

# Cache para el vocabulario de la base de datos (se carga una vez)
_vocabulario_cache = None
_vocabulario_palabras_cache = None

def _obtener_vocabulario_bd():
    """
    Obtiene todas las palabras únicas de las descripciones en la BD.
    Esto sirve como diccionario personalizado para corrección ortográfica.
    """
    global _vocabulario_cache, _vocabulario_palabras_cache
    
    if _vocabulario_cache is None:
        try:
            # Obtener todas las descripciones
            descripciones_partidas = Partida.objects.values_list('descripcion', flat=True)
            descripciones_subpartidas = Subpartida.objects.values_list('descripcion', flat=True)
            nombres_capitulos = Capitulo.objects.values_list('nombre', flat=True)
            
            # Unir todas las descripciones
            todas_descripciones = list(descripciones_partidas) + list(descripciones_subpartidas) + list(nombres_capitulos)
            
            # Extraer todas las palabras únicas (mínimo 3 caracteres)
            palabras_unicas = set()
            for desc in todas_descripciones:
                if desc:
                    # Extraer palabras (solo letras, mínimo 3 caracteres)
                    palabras = re.findall(r'\b[a-záéíóúñü]{3,}\b', desc.lower())
                    palabras_unicas.update(palabras)
            
            _vocabulario_cache = todas_descripciones
            _vocabulario_palabras_cache = palabras_unicas
            
        except Exception:
            _vocabulario_cache = []
            _vocabulario_palabras_cache = set()
    
    return _vocabulario_palabras_cache, _vocabulario_cache

def _corregir_palabra_con_vocabulario(palabra, vocabulario_palabras, todas_descripciones):
    """
    Corrige una palabra usando el vocabulario de la BD y similitud de texto.
    Mejorado para buscar en todas las palabras del vocabulario con mejor rendimiento.
    """
    from difflib import get_close_matches, SequenceMatcher
    
    palabra_lower = palabra.lower()
    
    # Si la palabra ya está en el vocabulario, no necesita corrección
    if palabra_lower in vocabulario_palabras:
        return palabra
    
    # Buscar palabras similares en el vocabulario con cutoff más bajo para mayor flexibilidad
    # Reducimos el cutoff a 0.6 para encontrar palabras como "cabalo" -> "caballo"
    palabras_similares = get_close_matches(palabra_lower, list(vocabulario_palabras), n=5, cutoff=0.6)
    
    if palabras_similares:
        # Calcular similitud exacta para elegir la mejor
        mejor_similitud = 0
        mejor_palabra = palabras_similares[0]
        
        for palabra_similar in palabras_similares:
            similitud = SequenceMatcher(None, palabra_lower, palabra_similar).ratio()
            if similitud > mejor_similitud:
                mejor_similitud = similitud
                mejor_palabra = palabra_similar
        
        # Solo retornar corrección si la similitud es razonable (>= 0.65)
        if mejor_similitud >= 0.65:
            return mejor_palabra
    
    # Si no hay coincidencias buenas, retornar la palabra original
    return palabra

# Utilidad: Corrección ortográfica mejorada usando vocabulario de BD + pyspellchecker
def _corregir_ortografia(texto):
    """
    Corrige errores ortográficos usando:
    1. Vocabulario de la base de datos (palabras reales en descripciones)
    2. pyspellchecker para palabras comunes en español
    
    Retorna el texto corregido y una lista de palabras corregidas.
    """
    try:
        # Obtener vocabulario de la BD
        vocabulario_palabras, todas_descripciones = _obtener_vocabulario_bd()
        
        # Inicializar el corrector ortográfico en español y agregar vocabulario personalizado
        spell = SpellChecker(language='es')
        # Agregar todas las palabras del vocabulario personalizado al diccionario
        if vocabulario_palabras:
            spell.word_frequency.load_words(list(vocabulario_palabras))
        
        # Dividir el texto en palabras preservando espacios
        palabras = re.findall(r'\S+|\s+', texto)
        palabras_corregidas = []
        texto_corregido = ''
        
        for palabra in palabras:
            # Si es espacio, mantenerlo
            if palabra.isspace():
                texto_corregido += palabra
                continue
            
            # Extraer solo letras para verificar ortografía
            palabra_solo_letras = re.sub(r'[^\w]', '', palabra)
            
            if palabra_solo_letras and len(palabra_solo_letras) > 2:
                palabra_lower = palabra_solo_letras.lower()
                
                # Primero intentar con el vocabulario de la BD (más preciso para términos técnicos)
                correccion_vocab = _corregir_palabra_con_vocabulario(
                    palabra_lower, vocabulario_palabras, todas_descripciones
                )
                
                # Si el vocabulario encontró una corrección diferente
                if correccion_vocab != palabra_lower:
                    # Mantener la capitalización original
                    if palabra_solo_letras[0].isupper():
                        correccion_vocab = correccion_vocab.capitalize()
                    
                    # Reconstruir la palabra con signos de puntuación originales
                    palabra_corregida = palabra.replace(palabra_solo_letras, correccion_vocab)
                    palabras_corregidas.append((palabra_solo_letras, correccion_vocab))
                    texto_corregido += palabra_corregida
                # Si no, intentar con pyspellchecker (para palabras comunes)
                elif palabra_lower not in spell:
                    correccion_spell = spell.correction(palabra_lower)
                    
                    if correccion_spell and correccion_spell != palabra_lower:
                        # Mantener la capitalización original
                        if palabra_solo_letras[0].isupper():
                            correccion_spell = correccion_spell.capitalize()
                        
                        # Reconstruir la palabra con signos de puntuación originales
                        palabra_corregida = palabra.replace(palabra_solo_letras, correccion_spell)
                        palabras_corregidas.append((palabra_solo_letras, correccion_spell))
                        texto_corregido += palabra_corregida
                    else:
                        texto_corregido += palabra
                else:
                    texto_corregido += palabra
            else:
                texto_corregido += palabra
        
        return texto_corregido.strip(), palabras_corregidas
    except Exception as e:
        # Si hay algún error, retornar el texto original
        return texto, []

# Utilidad: Buscar usando sinónimos
def _buscar_con_sinonimos(query):
    """
    Busca en la BD usando la query original y todos sus sinónimos.
    Retorna un QuerySet combinado de Partida y Subpartida.
    """
    from django.db.models import Q, Value
    from django.db.models.functions import Greatest
    
    # Obtener sinónimos y términos relacionados
    terminos_busqueda = expandir_busqueda_con_sinonimos(query)
    
    # Crear filtro Q dinámico para incluir todos los términos
    filtro_q = Q()
    for termino in terminos_busqueda:
        filtro_q |= (Q(descripcion__icontains=termino) | Q(nombre__icontains=termino) if hasattr(Partida, 'nombre') else Q(descripcion__icontains=termino))
    
    # Buscar en partidas
    partidas = Partida.objects.filter(filtro_q)
    
    # Buscar en subpartidas
    subpartidas = Subpartida.objects.filter(filtro_q)
    
    return partidas, subpartidas, terminos_busqueda

# Utilidad: Normalizar códigos (eliminar puntos)
def _normalizar_codigo(codigo):
    """
    Elimina puntos de un código para comparación flexible.
    Ej: "0101.21.00.00" → "010121.00.00" → "010121000000"
    """
    if not codigo:
        return ""
    return codigo.replace('.', '')

# Utilidad: Buscar códigos sin puntos
def _buscar_codigos_sin_puntos(query_normalizada):
    """
    Busca códigos en la BD que coincidan sin considerar puntos.
    Ej: busca "010121" y encuentra "0101.21.00.00"
    """
    # Obtener todos los códigos y normalizarlos
    partidas_todas = Partida.objects.all()
    subpartidas_todas = Subpartida.objects.all()
    
    partidas_encontradas = []
    subpartidas_encontradas = []
    
    for p in partidas_todas:
        if _normalizar_codigo(p.codigo).startswith(query_normalizada):
            partidas_encontradas.append(p)
    
    for s in subpartidas_todas:
        if _normalizar_codigo(s.codigo).startswith(query_normalizada):
            subpartidas_encontradas.append(s)
    
    return partidas_encontradas, subpartidas_encontradas

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
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        # Registrar consulta en bitácora
        if hasattr(self, 'object') and self.object:
            registrar_bitacora(
                request,
                'consulta',
                f'Consulta de detalle de Capítulo: {self.object.codigo} - {self.object.nombre}',
                {'tipo': 'Capitulo', 'codigo': self.object.codigo, 'id': self.object.id}
            )
        return response

@method_decorator(login_required, name='dispatch')
class PartidaDetailView(DetailView):
    model = Partida
    template_name = 'arancel/partida_detail.html'
    context_object_name = 'partida'
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        # Registrar consulta en bitácora
        if hasattr(self, 'object') and self.object:
            registrar_bitacora(
                request,
                'consulta',
                f'Consulta de detalle de Partida: {self.object.codigo} - {self.object.descripcion[:100]}',
                {'tipo': 'Partida', 'codigo': self.object.codigo, 'id': self.object.id}
            )
        return response

@method_decorator(login_required, name='dispatch')
class SubpartidaDetailView(DetailView):
    model = Subpartida
    template_name = 'arancel/subpartida_detail.html'
    context_object_name = 'subpartida'
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        # Registrar consulta en bitácora
        if hasattr(self, 'object') and self.object:
            registrar_bitacora(
                request,
                'consulta',
                f'Consulta de detalle de Subpartida: {self.object.codigo} - {self.object.descripcion[:100]}',
                {'tipo': 'Subpartida', 'codigo': self.object.codigo, 'id': self.object.id}
            )
        return response

@login_required
def tabla_aranceles(request):
    # Cargar todas las secciones sin filtrar (el filtrado se hace en el frontend)
    secciones = Seccion.objects.prefetch_related('capitulos__partidas__subpartidas')
    return render(request, 'arancel/tabla_aranceles.html', {'secciones': secciones})

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
    
    # Si no hay exactos, intentar sin puntos
    query_normalizada = _normalizar_codigo(query)
    if (not partidas_exactas.exists() and not subpartidas_exactas.exists()) and query_normalizada != query:
        partidas_exactas_sin_puntos, subpartidas_exactas_sin_puntos = _buscar_codigos_sin_puntos(query_normalizada)
        if len(partidas_exactas_sin_puntos) == 1 and len(subpartidas_exactas_sin_puntos) == 0:
            partida = partidas_exactas_sin_puntos[0]
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
            # Registrar en bitácora
            registrar_bitacora(
                request,
                'busqueda',
                f'Búsqueda realizada: "{query}" (normalizado: {partida.codigo}) - Resultado: Partida {partida.codigo}',
                {'termino': query, 'tipo_resultado': 'Partida', 'codigo': partida.codigo, 'id': partida.id}
            )
            return redirect('arancel:partida_detail', pk=partida.id)
        
        elif len(subpartidas_exactas_sin_puntos) == 1 and len(partidas_exactas_sin_puntos) == 0:
            subpartida = subpartidas_exactas_sin_puntos[0]
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
                # Registrar en bitácora
                registrar_bitacora(
                    request,
                    'busqueda',
                    f'Búsqueda realizada: "{query}" (normalizado: {subpartida.codigo}) - Resultado: Subpartida {subpartida.codigo}',
                    {'termino': query, 'tipo_resultado': 'Subpartida', 'codigo': subpartida.codigo, 'id': subpartida.id}
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
                # Registrar en bitácora
                registrar_bitacora(
                    request,
                    'busqueda',
                    f'Búsqueda realizada: "{query}" (normalizado: {subpartida.codigo}) - Resultado: Subpartida {subpartida.codigo}',
                    {'termino': query, 'tipo_resultado': 'Subpartida', 'codigo': subpartida.codigo, 'id': subpartida.id}
                )
                return redirect('arancel:subpartida_detail', pk=subpartida.id)
    
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
        # Registrar en bitácora
        registrar_bitacora(
            request,
            'busqueda',
            f'Búsqueda realizada: "{query}" - Resultado: Partida {partida.codigo}',
            {'termino': query, 'tipo_resultado': 'Partida', 'codigo': partida.codigo, 'id': partida.id}
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
            # Registrar en bitácora
            registrar_bitacora(
                request,
                'busqueda',
                f'Búsqueda realizada: "{query}" - Resultado: Subpartida {subpartida.codigo}',
                {'termino': query, 'tipo_resultado': 'Subpartida', 'codigo': subpartida.codigo, 'id': subpartida.id}
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
            # Registrar en bitácora
            registrar_bitacora(
                request,
                'busqueda',
                f'Búsqueda realizada: "{query}" - Resultado: Subpartida {subpartida.codigo}',
                {'termino': query, 'tipo_resultado': 'Subpartida', 'codigo': subpartida.codigo, 'id': subpartida.id}
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
        # Registrar en bitácora
        registrar_bitacora(
            request,
            'busqueda',
            f'Búsqueda realizada: "{query}" - Resultado: Capítulo {capitulo.codigo}',
            {'termino': query, 'tipo_resultado': 'Capitulo', 'codigo': capitulo.codigo, 'id': capitulo.id}
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
        # Registrar en bitácora
        registrar_bitacora(
            request,
            'busqueda',
            f'Búsqueda realizada: "{query}" - Resultado: Sección {seccion.nombre}',
            {'termino': query, 'tipo_resultado': 'Seccion', 'id': seccion.id}
        )
        return redirect('arancel:seccion_detail', pk=seccion.id)

    # --- Si no hay NINGUNA coincidencia exacta 1-a-1 ---
    # Redirigir a la página de resultados. 
    # Esta página se encargará de buscar por __icontains Y de buscar sugerencias.
    # Registrar búsqueda en bitácora
    registrar_bitacora(
        request,
        'busqueda',
        f'Búsqueda realizada: "{query}" - Resultado: Múltiples resultados',
        {'termino': query, 'tipo_resultado': 'Multiples'}
    )
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
        
        # Intentar corrección ortográfica si no parece ser un código
        query_original = query
        query_corregida = None
        es_codigo = any(c.isdigit() for c in query) or len(query) <= 10
        
        # Si no es un código, intentar corregir ortografía
        if not es_codigo and len(query) > 2:  # Solo corregir si tiene más de 2 caracteres
            query_corregida, _ = _corregir_ortografia(query)
            # Si la corrección es diferente y tiene sentido, usar ambas búsquedas
            if query_corregida and query_corregida.lower() != query.lower():
                # Usar la consulta corregida para búsquedas adicionales
                query = query_corregida
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
        
        # Búsqueda con sinónimos (si no es un código)
        partidas_sinonimos = Partida.objects.none()
        subpartidas_sinonimos = Subpartida.objects.none()
        if not es_codigo and len(query) >= 3:
            try:
                partidas_sin, subpartidas_sin, terminos_usados = _buscar_con_sinonimos(query)
                # Excluir resultados ya encontrados
                partidas_sinonimos = partidas_sin.exclude(
                    id__in=list(partidas_exactas.values_list('id', flat=True)) + 
                           list(partidas_aprox.values_list('id', flat=True))
                )
                subpartidas_sinonimos = subpartidas_sin.exclude(
                    id__in=list(subpartidas_exactas.values_list('id', flat=True)) + 
                           list(subpartidas_aprox.values_list('id', flat=True))
                )
            except Exception as e:
                pass  # Si hay error en búsqueda con sinónimos, continuar sin ellos
        
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
        
        # Agregar resultados de búsqueda con sinónimos (con puntaje más bajo que exacta/aproximada)
        for p in partidas_sinonimos[:5]:  # Limitar a 5 resultados de sinónimos
            puntaje = calcular_puntaje_item(p, query_lower, False)
            if puntaje > 0.2:
                resultados_con_puntaje.append({
                    'tipo': 'Partida',
                    'id': p.id,
                    'codigo': _clean_text_for_json(p.codigo),
                    'descripcion': _clean_text_for_json(p.descripcion),
                    'puntaje': puntaje * 0.75,  # Reducir puntaje para que aparezcan después de exactos/aproximados
                    'es_correccion': False,
                    'es_sinonimo': True
                })
        
        for s in subpartidas_sinonimos[:5]:  # Limitar a 5 resultados de sinónimos
            puntaje = calcular_puntaje_item(s, query_lower, False)
            if puntaje > 0.2:
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
                    'puntaje': puntaje * 0.75,  # Reducir puntaje para que aparezcan después de exactos/aproximados
                    'es_correccion': False,
                    'es_sinonimo': True
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
    
    # 1. Búsqueda normal con __icontains (sin ser agresivo con puntos)
    # Limpiar la query de puntos innecesarios para la búsqueda
    query_limpia = query.replace('.', '')  # Remover puntos para búsqueda más flexible
    
    # Búsqueda primaria con query limpia
    partidas = Partida.objects.filter(Q(codigo__icontains=query_limpia) | Q(descripcion__icontains=query_limpia))
    subpartidas = Subpartida.objects.filter(Q(codigo__icontains=query_limpia) | Q(descripcion__icontains=query_limpia))
    
    # Si es un código y no hay resultados, buscar sin considerar puntos en BD
    if (not partidas.exists() and not subpartidas.exists()) and any(char.isdigit() for char in query_limpia):
        try:
            partidas_sin_puntos, subpartidas_sin_puntos = _buscar_codigos_sin_puntos(query_limpia)
            if partidas_sin_puntos or subpartidas_sin_puntos:
                partidas = Partida.objects.filter(id__in=[p.id for p in partidas_sin_puntos])
                subpartidas = Subpartida.objects.filter(id__in=[s.id for s in subpartidas_sin_puntos])
        except Exception as e:
            pass  # Si hay error, continuar con búsqueda normal
    
    total_results = partidas.count() + subpartidas.count()
    
    sugerencias_codigos = []
    sugerencias_desc = []
    sugerencias_sinonimos = []
    query_corregida = None
    correcciones_realizadas = []
    
    # 1.5. Si no hay resultados, intentar búsqueda con sinónimos primero
    if total_results == 0 and query_limpia and len(query_limpia) >= 3:
        try:
            partidas_sin, subpartidas_sin, terminos_usados = _buscar_con_sinonimos(query_limpia)
            if partidas_sin.exists() or subpartidas_sin.exists():
                partidas = partidas_sin
                subpartidas = subpartidas_sin
                total_results = partidas.count() + subpartidas.count()
                # Guardar información de búsqueda con sinónimos
                sinonimos_encontrados = obtener_sinonimos(query_limpia)
                if sinonimos_encontrados:
                    sugerencias_sinonimos = sinonimos_encontrados[:5]
        except Exception as e:
            pass  # Si hay error, continuar con corrección ortográfica
    
    # 1.6. Si no hay resultados, intentar corrección ortográfica
    if total_results == 0 and query_limpia:
        # Intentar corregir la ortografía
        query_corregida, correcciones = _corregir_ortografia(query)
        
        # Si hubo correcciones y la consulta corregida es diferente
        if query_corregida and query_corregida.lower() != query.lower() and correcciones:
            correcciones_realizadas = correcciones
            # Buscar con la consulta corregida
            partidas_corregidas = Partida.objects.filter(
                Q(codigo__icontains=query_corregida) | Q(descripcion__icontains=query_corregida)
            )
            subpartidas_corregidas = Subpartida.objects.filter(
                Q(codigo__icontains=query_corregida) | Q(descripcion__icontains=query_corregida)
            )
            
            # Si encontramos resultados con la corrección, usarlos
            if partidas_corregidas.exists() or subpartidas_corregidas.exists():
                partidas = partidas_corregidas
                subpartidas = subpartidas_corregidas
                total_results = partidas.count() + subpartidas.count()
                # Agregar mensaje informativo sobre la corrección
                messages.info(request, f'Búsqueda corregida: "{query}" → "{query_corregida}"')
    
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
            # Registrar en bitácora
            registrar_bitacora(
                request,
                'busqueda',
                f'Búsqueda realizada: "{query}" - {tipo_resultado}',
                {'termino': query, 'tipo_resultado': tipo_resultado, 'total_resultados': total_results}
            )
            
    # 4. Renderizar la página
    return render(request, 'arancel/resultados_busqueda.html', {
        'query': query,
        'query_corregida': query_corregida,
        'correcciones_realizadas': correcciones_realizadas,
        'partidas': partidas,
        'subpartidas': subpartidas,
        'sugerencias_codigos': sugerencias_codigos,
        'sugerencias_desc': sugerencias_desc,
        'sugerencias_sinonimos': sugerencias_sinonimos,
    })