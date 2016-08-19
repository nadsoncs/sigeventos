from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Evento)
#admin.site.register(Video)
admin.site.register(Inscricao)
admin.site.register(Atividade)
admin.site.register(Inscricao_atividade)
admin.site.register(Arquivo)
admin.site.register(Aula)
admin.site.register(Presenca)