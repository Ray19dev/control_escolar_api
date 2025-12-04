from django.contrib.auth.models import User
from rest_framework import serializers
from .models import *
from .models import Maestros

class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('id','first_name','last_name', 'email')

class AdminSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model = Administradores
        fields = '__all__'
        
# TODO: Declarar los serializadores para los perfiles de alumnos y maestros

class AlumnoSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model = Alumnos
        fields = '__all__'

class MaestroSerializer(serializers.ModelSerializer):
    
    user=UserSerializer(read_only=True)
    class Meta:
        model = Maestros
        fields = '__all__'
        
class MateriasSerializer(serializers.ModelSerializer):
    
    maestro_first_name = serializers.CharField(source='id_maestro.user.first_name', read_only=True)
    
    maestro_last_name= serializers.CharField(source='id_maestro.user.last_name', read_only=True)

    class Meta:
        model = Materias
        fields = '__all__'