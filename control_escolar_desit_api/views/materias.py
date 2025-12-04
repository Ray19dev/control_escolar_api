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
import json
from django.shortcuts import get_object_or_404

class MateriasAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    # GET → obtener todas las materias
    def get(self, request, *args, **kwargs):
        materias = Materias.objects.all().order_by("id")
        lista = MateriasSerializer(materias, many=True).data
        return Response(lista, 200)
    
    
class MateriasView(generics.CreateAPIView):
        
     def get_permissions(self):
        if self.request.method in ['GET', 'PUT', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return []  # POST no requiere autenticación
    
     def get(self, request, *args, **kwargs):
      id_materia = request.GET.get("id")

      if not id_materia:
        return Response({"error": "Falta parámetro ?id"}, 400)

      materia = get_object_or_404(Materias, id=id_materia)
      serializer = MateriasSerializer(materia)
      return Response(serializer.data, 200)
    
     def post(self, request, *args, **kwargs):

        serializer = MateriasSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"materia_created_id": serializer.data["id"]},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
     @transaction.atomic
     def delete(self, request, *args, **kwargs):
        materia = get_object_or_404(Materias, id=request.GET.get("id"))
        try:
            materia.delete()
            return Response({"details":"Materia eliminada"},200)
        except Exception as e:
            return Response({"details":"Algo pasó al eliminar"},400)
        
    
        
     @transaction.atomic
     def put(self, request):
        materia_id = request.GET.get("id")
        if not materia_id:
            return Response({"error": "Falta parámetro ?id"}, 400)

        materia = get_object_or_404(Materias, id=materia_id)

        serializer = MateriasSerializer(materia, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"details": "Materia actualizada correctamente"}, 200)

        return Response(serializer.errors, 400)
