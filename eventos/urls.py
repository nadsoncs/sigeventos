from django.conf.urls import include, url
from . import views

app_name = 'eventos'
urlpatterns = [
    url(r'^$', views.home),
    url(r'^eventos/(?P<pk>[0-9]+)/$', views.evento_detalhes, name='evento_detalhes'),
    url(r'^eventos/edit/(?P<pk>[0-9]+)/$', views.evento_edit, name='evento_edit'),
    url(r'^inscricao/(?P<pk>[0-9]+)/$', views.evento_inscricao, name='evento_inscricao'),
    url(r'^programacao/(?P<pk>[0-9]+)/$', views.evento_atividade, name='evento_atividade'),
    url(r'^atividade/add/(?P<pk>[0-9]+)/$', views.atividade_new, name='atividade_new'),
    url(r'^atividade/(?P<pk>[0-9]+)/$', views.atividade_detalhes, name='atividade_detalhes'),
    url(r'^atividade/presentes/(?P<pk>[0-9]+)/$', views.presentes, name='presentes'),
    url(r'^aula/add/(?P<pk>[0-9]+)/$', views.aula_new, name='aula_new'),
    url(r'^arquivo/add/(?P<pk>[0-9]+)/$', views.arquivo_new, name='arquivo_new'),
    url(r'^inscricao/confirmar/(?P<pk>[0-9]+)/$', views.confirmar_inscricao, name='confirmar_inscricao'),
    url(r'^inscricao/delete/(?P<pk>[0-9]+)/$', views.inscricao_delete, name='inscricao_delete'),
    url(r'^inscricao/update/(?P<pk>[0-9]+)/$', views.inscricao_update, name='inscricao_update'),
    url(r'^certificados/(?P<ev>[0-9]+)/(?P<at>[0-9]+)/$', views.certificados, name='certificados'),
    url(r'^impressos/(?P<pk>[0-9]+)/$', views.impressos, name='impressos'),
    url(r'^listas/(?P<ev>[0-9]+)/(?P<at>[0-9]+)/$', views.lista_participantes, name='listas'),
    url(r'^crachas/(?P<ev>[0-9]+)/(?P<at>[0-9]+)/$', views.crachas, name='crachas'),
    url(r'^mensagem/(?P<ev>[0-9]+)/(?P<at>[0-9]+)/$', views.mensagem, name='mensagem'),
    url(r'^register/', views.register, name='register'),
    url(r'^perfil/edit/', views.editar_perfil, name='editar_perfil'),
    url(r'^logout/', views.logout_view, name='logout'),
    url(r'^login/', views.login_view, name='login'),
]