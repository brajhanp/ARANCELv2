from django.urls import path
from .views import (
    tabla_aranceles, SeccionListView, SeccionCreateView, SeccionUpdateView,
    SeccionDeleteView, SeccionDetailView, CapituloDetailView, PartidaDetailView,
    SubpartidaDetailView, buscador_global, autocomplete_arancel, resultados_busqueda,
    prevalidacion_view, prevalidacion_api
)

app_name = 'arancel'

urlpatterns = [
    path('', tabla_aranceles, name='tabla_aranceles'),
    path('tabla/', tabla_aranceles, name='tabla_aranceles'),
    path('prevalidacion/', prevalidacion_view, name='prevalidacion'),
    path('api/prevalidacion/<str:codigo>/', prevalidacion_api, name='prevalidacion_api'),

    # CRUD Seccion
    path('secciones/', SeccionListView.as_view(), name='seccion_list'),
    path('secciones/nueva/', SeccionCreateView.as_view(), name='seccion_create'),
    path('secciones/<int:pk>/editar/', SeccionUpdateView.as_view(), name='seccion_update'),
    path('secciones/<int:pk>/eliminar/', SeccionDeleteView.as_view(), name='seccion_delete'),
    path('secciones/<int:pk>/', SeccionDetailView.as_view(), name='seccion_detail'),

    path('capitulos/<int:pk>/', CapituloDetailView.as_view(), name='capitulo_detail'),
    path('partidas/<int:pk>/', PartidaDetailView.as_view(), name='partida_detail'),
    path('subpartidas/<int:pk>/', SubpartidaDetailView.as_view(), name='subpartida_detail'),

    path('buscar/', buscador_global, name='buscador_global'),
    path('autocomplete/', autocomplete_arancel, name='autocomplete_arancel'),
    path('resultados_busqueda/', resultados_busqueda, name='resultados_busqueda'),
]