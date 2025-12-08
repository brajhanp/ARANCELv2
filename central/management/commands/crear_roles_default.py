from django.core.management.base import BaseCommand
from central.models import Rol

class Command(BaseCommand):
    help = 'Crea los roles por defecto: Administrador y Despachador de Aduana'

    def handle(self, *args, **options):
        # Crear rol de Administrador
        admin_rol, created = Rol.objects.get_or_create(
            nombre='Administrador',
            defaults={
                'descripcion': 'Rol con acceso completo al sistema. Puede gestionar usuarios, roles y acceder a todas las funcionalidades.',
                'permisos_arancel': True,
                'permisos_admin': True,
                'permisos_usuarios': True,
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('✅ Rol "Administrador" creado exitosamente')
            )
        else:
            self.stdout.write(
                self.style.WARNING('⚠️  El rol "Administrador" ya existe')
            )

        # Crear rol de Despachador de Aduana
        despachador_rol, created = Rol.objects.get_or_create(
            nombre='Despachador de Aduana',
            defaults={
                'descripcion': 'Rol para despachadores de aduana. Puede acceder a la información de aranceles y realizar búsquedas.',
                'permisos_arancel': True,
                'permisos_admin': False,
                'permisos_usuarios': False,
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('✅ Rol "Despachador de Aduana" creado exitosamente')
            )
        else:
            self.stdout.write(
                self.style.WARNING('⚠️  El rol "Despachador de Aduana" ya existe')
            )

        self.stdout.write(
            self.style.SUCCESS('\n🎉 Roles por defecto configurados correctamente!')
        ) 