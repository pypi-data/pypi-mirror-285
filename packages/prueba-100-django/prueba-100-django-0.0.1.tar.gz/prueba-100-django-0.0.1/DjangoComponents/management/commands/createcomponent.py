from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
import os

class Command(BaseCommand):
    help = 'Crear un archivo HTML dentro de una app'

    def add_arguments(self, parser):
        parser.add_argument('app_name', type=str, help='Nombre de la app')
        parser.add_argument('file_path', type=str, help='Ruta del componente HTML dentro de templates')
        parser.add_argument('instrucciones', type=str, help='Instrucciones para utilizar el paquete')

    def handle(self, *args, **kwargs):
        app_name = kwargs['app_name']
        file_path = kwargs['file_path']

        # Obtener la configuración de la app dinámicamente
        try:
            app_config = apps.get_app_config(app_name)
        except LookupError:
            raise CommandError(f'App "{app_name}" no encontrada.')

        # Construir la ruta del directorio templates
        templates_dir = os.path.join(app_config.path, 'templates')

        # Asegurar que el directorio templates exista, crearlo si no
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)

        # Construir la ruta del archivo dentro del directorio templates
        templates_path = os.path.join(templates_dir, file_path)

        # Normalizar la ruta para asegurar separadores correctos según el sistema operativo
        templates_path = os.path.normpath(templates_path)

        # Asegurar que la estructura de directorios exista
        templates_folder = os.path.dirname(templates_path)
        if not os.path.exists(templates_folder):
            os.makedirs(templates_folder)

        # Verificar si el archivo ya existe
        if os.path.exists(templates_path):
            self.stdout.write(self.style.WARNING(f'El archivo {file_path} ya existe en la carpeta {app_name}/templates/.'))
        else:
            # Crear el archivo
            with open(templates_path, 'w') as f:
                f.write('<div>Este es el contenido del componente.</div>')

            self.stdout.write(self.style.SUCCESS(f'Se ha creado exitosamente {file_path} en la carpeta {app_name}/templates/.'))
