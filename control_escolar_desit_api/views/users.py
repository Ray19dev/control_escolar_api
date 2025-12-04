from django.db.models import *
from django.db import transaction
from control_escolar_desit_api.serializers import UserSerializer
from control_escolar_desit_api.serializers import *
from control_escolar_desit_api.models import *
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import Group

from django.db import transaction
from control_escolar_desit_api.serializers import UserSerializer
from control_escolar_desit_api.models import Administradores, Maestros, Alumnos
from rest_framework import permissions, generics, status
from rest_framework.response import Response
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
import json


# ======== ADMINISTRADOR ========

class AdminAll(generics.CreateAPIView):
    #Esta función es esencial para todo donde se requiera autorización de inicio de sesión (token)
    permission_classes = (permissions.IsAuthenticated,)
    # Invocamos la petición GET para obtener todos los administradores
    def get(self, request, *args, **kwargs):
        admin = Administradores.objects.filter(user__is_active = 1).order_by("id")
        lista = AdminSerializer(admin, many=True).data
        return Response(lista, 200)

class AdminView(generics.CreateAPIView):
    
    def get_permissions(self):
        if self.request.method in ['GET', 'PUT', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return []  # POST no requiere autenticación
  
    
    def get(self, request, *args, **kwargs):
        admin = get_object_or_404(Administradores, id = request.GET.get("id"))
        admin = AdminSerializer(admin, many=False).data
        # Si todo es correcto, regresamos la información
        return Response(admin, 200)
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        
        user = UserSerializer(data=request.data)
        
        if user.is_valid():
            #Grabar datos del administrador
            role = request.data['rol']
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            password = request.data['password']
            #Valida si existe el usuario o bien el email registrado
            existing_user = User.objects.filter(email=email).first()

            if existing_user:
                return Response({"message":"Username "+email+", is already taken"},400)

            user = User.objects.create( username = email,
                                        email = email,
                                        first_name = first_name,
                                        last_name = last_name,
                                        is_active = 1)


            user.save()
            user.set_password(password)
            user.save()

            group, created = Group.objects.get_or_create(name=role)
            group.user_set.add(user)
            group.save()

            #Almacenar los datos adicionales del administrador
            admin = Administradores.objects.create(user=user,
                                            clave_admin= request.data["clave_admin"],
                                            telefono= request.data["telefono"],
                                            rfc= request.data["rfc"].upper(),
                                            edad= request.data["edad"],
                                            ocupacion= request.data["ocupacion"])
            admin.save()

            return Response({"Admin creado con el ID: ": admin.id }, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        permission_classes = (permissions.IsAuthenticated,)
        # Primero obtenemos el administrador a actualizar
        admin = get_object_or_404(Administradores, id=request.data["id"])
        admin.clave_admin = request.data["clave_admin"]
        admin.telefono = request.data["telefono"]
        admin.rfc = request.data["rfc"]
        admin.edad = request.data["edad"]
        admin.ocupacion = request.data["ocupacion"]
        admin.save()
        # Actualizamos los datos del usuario asociado (tabla auth_user de Django)
        user = admin.user
        user.first_name = request.data["first_name"]
        user.last_name = request.data["last_name"]
        user.save()
        
        return Response({"message": "Administrador actualizado correctamente", "admin": AdminSerializer(admin).data}, 200)
        # return Response(user,200)
    
     # Eliminar admin con delete (Borrar realmente)
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        administrador = get_object_or_404(Administradores, id=request.GET.get("id"))
        try:
            administrador.user.delete()
            return Response({"details":"Administrador eliminado"},200)
        except Exception as e:
            return Response({"details":"Algo pasó al eliminar"},400)

#*
# ======== MAESTRO ========

class MaestroAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user
        # TODO: Regresar perfil del maestro
        return Response({})


class MaestroView(generics.CreateAPIView):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user_serializer = UserSerializer(data=request.data)

        if user_serializer.is_valid():
            role = request.data['rol']
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            password = request.data['password']

            if User.objects.filter(email=email).exists():
                return Response({"message": f"El email {email} ya está registrado"}, status=400)

            user = User.objects.create_user(
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
                is_active=True
            )

            group, _ = Group.objects.get_or_create(name=role)
            group.user_set.add(user)

            maestro = Maestros.objects.create(
                user=user,
                telefono=request.data["telefono"],
                rfc=request.data["rfc"].upper(),
                cubiculo=request.data["cubiculo"],
                area_investigacion=request.data["area_investigacion"]
            )

            return Response({"Maestro creado con ID": maestro.id}, status=201)

        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class TotalUsers(generics.CreateAPIView):
    #Contar el total de cada tipo de usuarios
    def get(self, request, *args, **kwargs):
        # TOTAL ADMINISTRADORES
        admin_qs = Administradores.objects.filter(user__is_active=True)
        total_admins = admin_qs.count()

        # TOTAL MAESTROS
        maestros_qs = Maestros.objects.filter(user__is_active=True)
        lista_maestros = MaestroSerializer(maestros_qs, many=True).data

        # Convertir materias_json solo si existen maestros
        for maestro in lista_maestros:
            try:
                maestro["materias_json"] = json.loads(maestro["materias_json"])
            except Exception:
                maestro["materias_json"] = []  # fallback seguro

        total_maestros = maestros_qs.count()

        # TOTAL ALUMNOS
        alumnos_qs = Alumnos.objects.filter(user__is_active=True)
        total_alumnos = alumnos_qs.count()

        # Respuesta final SIEMPRE válida
        return Response(
            {
                "admins": total_admins,
                "maestros": total_maestros,
                "alumnos": total_alumnos
            },
            status=200
        )


# ======== ALUMNO ========


class AlumnoAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user
        # TODO: Regresar perfil del maestro
        return Response({})
    
class AlumnoView(generics.CreateAPIView):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user_serializer = UserSerializer(data=request.data)

        if user_serializer.is_valid():
            role = request.data['rol']
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            password = request.data['password']

            if User.objects.filter(email=email).exists():
                return Response({"message": f"El email {email} ya está registrado"}, status=400)

            user = User.objects.create_user(
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
                is_active=True,
               

            )

            group, _ = Group.objects.get_or_create(name=role)
            group.user_set.add(user)

            alumno = Alumnos.objects.create(
                user=user,
                curp=request.data["curp"],
                rfc=request.data["rfc"].upper(),
                edad=request.data["edad"],
                telefono=request.data["telefono"],
                ocupacion=request.data["ocupacion"]
            )

            return Response({"Alumno creado con ID": alumno.id}, status=201)

        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    