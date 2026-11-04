from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


from .models import Outfit, Prenda, Tendencia, Usuario

admin.site.register(Usuario, UserAdmin)
admin.site.register([Tendencia, Prenda, Outfit])