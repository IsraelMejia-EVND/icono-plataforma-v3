# ICONO · Interfaz Tabler
Basado en el ZIP del proyecto entregado por el equipo. Tabler 1.7.3, licencia MIT.
Las fotografías editoriales son recortes de las composiciones facilitadas. Comprueba sus permisos antes de publicar comercialmente.

## Instalación
Trabaja en una rama y con el árbol Git limpio. Descomprime el paquete en la carpeta que contiene manage.py.
En config/settings.py añade estas opciones:
    LANGUAGES = [("es", "Español"), ("en", "English")]
    LANGUAGE_CODE = "es"
    USE_I18N = True
En MIDDLEWARE, inmediatamente después de SessionMiddleware, añade:
    "django.middleware.locale.LocaleMiddleware",
Mantén CommonMiddleware después de LocaleMiddleware.
Ejecuta:
    python manage.py check
    python manage.py runserver
No requiere nuevas migraciones.
Prueba inicio, registro, sesión, catálogo, favoritos, comentarios, perfil y los dos paneles de citas.
Cambia idioma y tema, recarga y navega. Los registros escritos por usuarios conservan su idioma original.
Las traducciones compiladas están incluidas en core/locale/en/LC_MESSAGES.
La zona horaria sigue siendo America/Tijuana.
