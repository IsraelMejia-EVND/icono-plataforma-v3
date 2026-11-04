from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView
from django.urls import path

from . import views


app_name = "core"

urlpatterns = [
    path("registro/", views.registro, name="registro"),
    path("iniciar-sesion/",LoginView.as_view(template_name="core/login.html",next_page="core:cuenta",),name="login",),
    path("mi-cuenta/", login_required(views.cuenta, login_url="core:login"), name="cuenta"),
    path("outfits/", views.catalogo, name="catalogo"),
    path("outfits/<int:pk>/", views.detalle_outfit, name="detalle_outfit"),
    path("outfits/<int:pk>/favorito/", views.cambiar_favorito, name="cambiar_favorito"),
    path("outfits/<int:pk>/comentario/eliminar/",views.eliminar_comentario,name="eliminar_comentario",),
    path("mi-cuenta/perfil/", views.perfil_estilo, name="perfil_estilo"),
    path("mi-cuenta/citas/", views.citas_cliente, name="citas_cliente"),
    path("asesor/citas/", views.citas_asesor, name="citas_asesor"),
    path("asesor/citas/<int:pk>/responder/",views.responder_cita,name="responder_cita",),
    path("mi-cuenta/citas/<int:pk>/cancelar/", views.cancelar_cita, name="cancelar_cita"),
    path("asesor/citas/<int:pk>/perfil/",views.perfil_cliente_asesor,name="perfil_cliente_asesor",),
    path("", TemplateView.as_view(template_name="core/inicio.html"), name="inicio"),
    path("cerrar-sesion/", LogoutView.as_view(next_page="core:inicio"), name="logout"),
]