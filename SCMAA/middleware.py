"""
Middleware personalizado para permitir orígenes dinámicos de ngrok y otros proxies
en modo desarrollo.
"""
from django.conf import settings
from django.middleware.csrf import CsrfViewMiddleware
from urllib.parse import urlparse
import re


class DynamicCsrfMiddleware(CsrfViewMiddleware):
    """
    Middleware que permite orígenes dinámicos en modo DEBUG.
    Útil para desarrollo con ngrok, Cloudflare Tunnel, etc.
    """
    
    def process_view(self, request, callback, callback_args, callback_kwargs):
        """
        Procesa la vista antes de la verificación CSRF.
        Agrega dinámicamente el origen a CSRF_TRUSTED_ORIGINS si es necesario.
        """
        # Solo en modo DEBUG
        if settings.DEBUG:
            # Obtener el origen de la solicitud
            origin = request.META.get('HTTP_ORIGIN') or request.META.get('HTTP_REFERER', '')
            
            if origin:
                try:
                    parsed = urlparse(origin)
                    origin_url = f"{parsed.scheme}://{parsed.netloc}"
                    
                    # Dominios conocidos de servicios de túnel
                    trusted_patterns = [
                        r'\.ngrok\.io$',
                        r'\.ngrok-free\.app$',
                        r'\.ngrok-free\.dev$',
                        r'\.trycloudflare\.com$',
                    ]
                    
                    # Verificar si el dominio coincide con algún patrón conocido
                    is_trusted_domain = any(
                        re.search(pattern, parsed.netloc) 
                        for pattern in trusted_patterns
                    )
                    
                    # Si es un dominio conocido y no está en la lista, agregarlo
                    if is_trusted_domain and origin_url not in settings.CSRF_TRUSTED_ORIGINS:
                        settings.CSRF_TRUSTED_ORIGINS.append(origin_url)
                except Exception:
                    # Si hay algún error al parsear, continuar con el flujo normal
                    pass
        
        # Continuar con el procesamiento normal del middleware CSRF
        return super().process_view(request, callback, callback_args, callback_kwargs)

