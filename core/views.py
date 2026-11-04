from django.contrib.auth.models import Group
from django.db import transaction
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest
from django.views.decorators.http import require_POST

from .forms import ComentarioForm, PerfilEstiloForm, RegistroClienteForm,SolicitudCitaForm
from .models import Comentario, Favorito, Outfit, PerfilEstilo, Cita, Usuario

def registro(request):
    if request.method == "POST":
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                grupo = Group.objects.get(name="Cliente")
                usuario = form.save()
                usuario.groups.add(grupo)
            return redirect("core:login")
    else:
        form = RegistroClienteForm()

    return render(request, "core/registro.html", {"form": form})


def cuenta(request):
    favoritos = (
        Favorito.objects.filter(usuario=request.user, outfit__publicado=True)
        .select_related("outfit")
        .order_by("outfit__nombre", "pk")
    )
    return render(
        request,
        "core/cuenta.html",
        {
            "favoritos": favoritos,
            "es_cliente": request.user.groups.filter(name="Cliente").exists(),
            "es_asesor": request.user.groups.filter(name="Asesor").exists(),
        },
    )





def catalogo(request):
    outfits = (
        Outfit.objects.filter(publicado=True)
        .select_related("tendencia")
        .order_by("nombre", "pk")
    )
    return render(request, "core/catalogo.html", {"outfits": outfits})


def detalle_outfit(request, pk):
    outfits = Outfit.objects.filter(publicado=True).select_related("tendencia")
    outfit = get_object_or_404(outfits, pk=pk)
    es_cliente = (
        request.user.is_authenticated
        and request.user.groups.filter(name="Cliente").exists()
    )
    es_favorito = es_cliente and Favorito.objects.filter(
        usuario=request.user, outfit=outfit
    ).exists()

    comentarios = (
        Comentario.objects.filter(outfit=outfit)
        .select_related("usuario")
        .order_by("-creado_en", "-pk")
    )
    ya_comento = es_cliente and comentarios.filter(usuario=request.user).exists()
    form = None

    if request.method == "POST":
        if not es_cliente:
            raise PermissionDenied

        form = ComentarioForm(request.POST)
        if form.is_valid():
            _, creado = Comentario.objects.get_or_create(
                usuario=request.user,
                outfit=outfit,
                defaults=form.cleaned_data,
            )
            if creado:
                return redirect("core:detalle_outfit", pk=outfit.pk)
            form.add_error(None, "Ya tienes un comentario en este outfit.")
    elif es_cliente and not ya_comento:
        form = ComentarioForm()

    return render(
        request,
        "core/detalle_outfit.html",
        {
            "outfit": outfit,
            "prendas": outfit.prendas.order_by("nombre", "pk"),
            "es_cliente": es_cliente,
            "es_favorito": es_favorito,
            "comentarios": comentarios,
            "comentario_form": form,
        },
    )

@login_required(login_url="core:login")
@require_POST
def cambiar_favorito(request, pk):
    if not request.user.groups.filter(name="Cliente").exists():
        raise PermissionDenied

    outfit = get_object_or_404(Outfit, pk=pk, publicado=True)
    accion = request.POST.get("accion")

    if accion == "guardar":
        Favorito.objects.get_or_create(usuario=request.user, outfit=outfit)
    elif accion == "quitar":
        Favorito.objects.filter(usuario=request.user, outfit=outfit).delete()
    else:
        return HttpResponseBadRequest("Acción de favorito inválida.")

    return redirect("core:detalle_outfit", pk=outfit.pk)


@login_required(login_url="core:login")
@require_POST
def eliminar_comentario(request, pk):
    if not request.user.groups.filter(name="Cliente").exists():
        raise PermissionDenied

    outfit = get_object_or_404(Outfit, pk=pk, publicado=True)
    Comentario.objects.filter(usuario=request.user, outfit=outfit).delete()
    return redirect("core:detalle_outfit", pk=outfit.pk)

@login_required(login_url="core:login")
def perfil_estilo(request):
    if not request.user.groups.filter(name="Cliente").exists():
        raise PermissionDenied

    perfil = PerfilEstilo.objects.filter(usuario=request.user).first()

    if request.method == "POST":
        form = PerfilEstiloForm(request.POST, instance=perfil)
        if form.is_valid():
            PerfilEstilo.objects.update_or_create(
                usuario=request.user,
                defaults=form.cleaned_data,
            )
            return redirect("core:cuenta")
    else:
        form = PerfilEstiloForm(instance=perfil)

    return render(request, "core/perfil_estilo.html", {"form": form})



@login_required(login_url="core:login")
def citas_cliente(request):
    if not request.user.groups.filter(name="Cliente").exists():
        raise PermissionDenied

    datos = request.POST if request.method == "POST" else None
    form = SolicitudCitaForm(datos, cliente=request.user)

    if request.method == "POST" and form.is_valid():
        asesor = form.cleaned_data["asesor"]
        fecha_hora = form.cleaned_data["fecha_hora"]

        with transaction.atomic():
            # Serializa solicitudes simultáneas de cualquiera de las dos cuentas.
            list(
                Usuario.objects.select_for_update()
                .filter(pk__in=[request.user.pk, asesor.pk])
                .order_by("pk")
            )
            citas_del_horario = Cita.objects.filter(
                fecha_hora=fecha_hora,
                estado__in=[Cita.Estado.PENDIENTE, Cita.Estado.CONFIRMADA],
            )
            if citas_del_horario.filter(asesor=asesor).exists():
                form.add_error("fecha_hora", "El asesor ya tiene una cita a esa hora.")
            elif citas_del_horario.filter(cliente=request.user).exists():
                form.add_error("fecha_hora", "Ya tienes una cita a esa hora.")
            else:
                Cita.objects.create(
                    cliente=request.user,
                    asesor=asesor,
                    fecha_hora=fecha_hora,
                )
                return redirect("core:citas_cliente")

    citas = (
        Cita.objects.filter(cliente=request.user)
        .select_related("asesor")
        .order_by("-fecha_hora", "-pk")
    )
    return render(
        request,
        "core/citas_cliente.html",
        {"form": form, "citas": citas, "ahora": timezone.now()},
    )

@login_required(login_url="core:login")
def citas_asesor(request):
    if not request.user.groups.filter(name="Asesor").exists():
        raise PermissionDenied

    citas = (
        Cita.objects.filter(asesor=request.user)
        .select_related("cliente")
        .order_by("fecha_hora", "pk")
    )
    return render(
        request,
        "core/citas_asesor.html",
        {"citas": citas, "ahora": timezone.now()},
    )


@login_required(login_url="core:login")
@require_POST
def responder_cita(request, pk):
    if not request.user.groups.filter(name="Asesor").exists():
        raise PermissionDenied

    cita = get_object_or_404(Cita, pk=pk, asesor=request.user)
    citas = Cita.objects.filter(pk=cita.pk, asesor=request.user)
    accion = request.POST.get("accion")
    ahora = timezone.now()

    if accion == "confirmar":
        actualizadas = citas.filter(
            estado=Cita.Estado.PENDIENTE,
            fecha_hora__gt=ahora,
        ).update(estado=Cita.Estado.CONFIRMADA)
    elif accion == "rechazar":
        actualizadas = citas.filter(
            estado=Cita.Estado.PENDIENTE,
        ).update(estado=Cita.Estado.CANCELADA)
    elif accion == "completar":
        actualizadas = citas.filter(
            estado=Cita.Estado.CONFIRMADA,
            fecha_hora__lte=ahora,
        ).update(estado=Cita.Estado.COMPLETADA)
    else:
        return HttpResponseBadRequest("Acción de cita inválida.")

    if not actualizadas:
        return HttpResponseBadRequest("La cita ya no admite esa acción.")

    return redirect("core:citas_asesor")


@login_required(login_url="core:login")
@require_POST
def cancelar_cita(request, pk):
    if not request.user.groups.filter(name="Cliente").exists():
        raise PermissionDenied

    cita = get_object_or_404(Cita, pk=pk, cliente=request.user)
    actualizadas = Cita.objects.filter(
        pk=cita.pk,
        cliente=request.user,
        estado__in=[Cita.Estado.PENDIENTE, Cita.Estado.CONFIRMADA],
        fecha_hora__gt=timezone.now(),
    ).update(estado=Cita.Estado.CANCELADA)

    if not actualizadas:
        return HttpResponseBadRequest("Esta cita ya no se puede cancelar.")

    return redirect("core:citas_cliente")


@login_required(login_url="core:login")
def perfil_cliente_asesor(request, pk):
    if not request.user.groups.filter(name="Asesor").exists():
        raise PermissionDenied

    cita = get_object_or_404(
        Cita.objects.select_related("cliente"),
        pk=pk,
        asesor=request.user,
        estado=Cita.Estado.CONFIRMADA,
    )
    perfil = (
        PerfilEstilo.objects.select_related("tendencia_preferida")
        .filter(usuario=cita.cliente)
        .first()
    )
    return render(
        request,
        "core/perfil_cliente_asesor.html",
        {"cita": cita, "perfil": perfil},
    )