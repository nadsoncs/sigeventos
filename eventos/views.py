from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from .models import *
from eventos.forms import *
from django.forms import modelformset_factory
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages 
# Create your views here.
def home(request):
    eventos = Evento.objects.all()
    context = {
        'eventos':eventos,
    }
    return render(request, 'eventos/home.html', context)

def register(request):
    if request.method == "POST":
        form = RegistrerForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            new_user = User.objects.create_user(user.username, user.email, user.password)
            new_user.first_name = user.first_name
            new_user.last_name = user.last_name
            new_user.save()
            user_authenticated = authenticate(username=user.username, password=user.password)
            login(request, user_authenticated)
            return HttpResponseRedirect(reverse('eventos:editar_perfil'))
    else:
        form = RegistrerForm()
    context = {
        "form":form,
    }

    return render(request, 'eventos/register.html',context)

@login_required(login_url='/login/')    
def editar_perfil(request):
    #se já existir o perfil vai atualizar
    if (UserProfile.objects.filter(user=request.user)):
        perfil = UserProfile.objects.get(user=request.user)
        if request.method == "POST":
            form = PerfilForm(request.POST, request.FILES, instance=perfil)
            if form.is_valid():
                perfil = form.save(commit=False)
                perfil.save()
                messages.success(request, 'Perfil alterado com sucesso!')
                return HttpResponseRedirect('/')
        else:
            form = PerfilForm(instance=perfil)
            context = {
                'form':form,
                'perfil':perfil,
            }
            return render(request, 'eventos/perfil_edit.html', context)
    #se não existir o perfil vai inserir
    else:
        if request.method == "POST":
            form = PerfilForm(request.POST, request.FILES)
            if form.is_valid():
                perfil = form.save(commit=False)
                perfil.user = request.user
                perfil.save()
            return HttpResponseRedirect('/')
        else:
            form = PerfilForm()
            context = {
                'form':form,
            }
            return render(request, 'eventos/perfil_edit.html', context)

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            password = form.cleaned_data['password']
            user_authenticated = authenticate(username=user, password=password)
            if user_authenticated is not None:
                if user_authenticated.is_active:
                    login(request, user_authenticated)
                    if UserProfile.objects.filter(user=request.user).exists():
                        return HttpResponseRedirect('/')
                    else:
                        return HttpResponseRedirect(reverse('eventos:editar_perfil'))
                else:
                    messages.error(request, 'Sua conta de usuário está inativada')
                    return HttpResponseRedirect(reverse('eventos:login'))
            else:
                messages.error(request, 'Usuário ou senha inválido')
                return HttpResponseRedirect(reverse('eventos:login'))
    else:
        form = LoginForm()
    context = {
        'form':form,
    }
    return render(request, 'eventos/login.html', context)

def evento_detalhes(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    if request.user.is_authenticated():
        if Inscricao.objects.filter(inscrito=request.user, evento=evento).exists():
            inscrito = Inscricao.objects.get(inscrito=request.user, evento=evento)
            papel = inscrito.papel
            atividade = evento.get_atividade(request.user)
        else:
            papel = ''
            atividade = ''
    else:
        papel = ''
        atividade = ''
    context = {
        'evento': evento,
        'papel':papel,
        'atividade':atividade,
    }
    return render(request, 'eventos/evento_detalhes.html', context)

@login_required(login_url='/login/')
def evento_edit(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    if evento.is_organizador(request.user):
        pass
    else:
        messages.error(request, 'Acesso negado! Essa função só está disponível para organizadores.')
        return HttpResponseRedirect(reverse('eventos:evento_detalhes', args=(pk)))

    if request.method =="POST":
        form = EventoForm(request.POST, instance=evento)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.save()
            #return redirect('views.evento_detalhes', pk=evento.pk)
            return HttpResponseRedirect(reverse('eventos:evento_detalhes', args=(evento.pk,)))
    else:
        form = EventoForm(instance=evento)
    context = {
        'evento': evento,
        'form':form,
        'papel':'O',
    }  
    return render(request, 'eventos/evento_edit.html', context)

@login_required(login_url='/login/')
def evento_inscricao(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    if Inscricao.objects.filter(inscrito=request.user, evento=evento).exists():
        messages.error(request, 'Usuário já está inscrito no evento!')
        return HttpResponseRedirect(reverse('eventos:evento_detalhes', args=(pk)))
    else:
        papel = ''
    if request.method =="POST":
        form = InscricaoForm(data=request.POST)
        if form.is_valid():
            inscrito = request.user
            papel = 'P'
            status = 'S'
            myInscrito = Inscricao(inscrito=inscrito, evento=evento, papel=papel, status=status)
            myInscrito.save()
            atividade = form.cleaned_data['atividades']
            inscAtividade = Inscricao_atividade(inscricao=myInscrito, atividade=atividade)
            inscAtividade.save()
        messages.success(request, 'Sua solicitação de inscrição foi realizada! Aguarde confirmação')
        return HttpResponseRedirect('/')

    else:
        form = InscricaoForm(evento=evento)
        papel = ''
    context = {
        'evento':evento,
        'form':form,
        'papel':papel,
    }  
    return render(request, 'eventos/evento_inscricao.html', context)

@login_required(login_url='/login/')
def confirmar_inscricao(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    
    if evento.is_organizador(request.user):
        pass
    else:
        messages.error(request, 'Acesso negado! Essa função só está disponível para organizadores.')
        return HttpResponseRedirect(reverse('eventos:evento_detalhes', args=(pk)))

    pendentes = Inscricao.objects.filter(evento=evento, status='S')
    context = {
        'evento': evento,
        'papel': 'O',
        'pendentes': pendentes,
    }
    return render(request, 'eventos/confirmar_inscricao.html', context)

def inscricao_update(request, pk):
    inscricao = get_object_or_404(Inscricao, pk=pk)
    if inscricao.evento.is_organizador(request.user):
        pass
    else:
        messages.error(request, 'Acesso negado! Essa função só está disponível para organizadores.')
        return HttpResponseRedirect(reverse('eventos:evento_detalhes', args=(pk,)))
    if Inscricao_atividade.objects.filter(inscricao=inscricao).exists():
        insc_atv = Inscricao_atividade.objects.get(inscricao=inscricao)
        #verifica o número de vagas
        if (Inscricao_atividade.objects.filter(inscricao=inscricao).count() < insc_atv.atividade.num_vagas):
            inscricao.status = 'C'
            inscricao.save()
            messages.success(request, 'Inscrição confirmada!')
            return HttpResponseRedirect(reverse('eventos:confirmar_inscricao', args=(inscricao.evento.pk,)))
        else:
            messages.error(request, 'Inscrição não confirmada, o curso desejado não dipoe de vagas.')
            return HttpResponseRedirect(reverse('eventos:confirmar_inscricao', args=(inscricao.evento.pk,)))
    
def inscricao_delete(request, pk):
    inscricao = get_object_or_404(Inscricao, pk=pk)
    if inscricao.evento.is_organizador(request.user):
        pass
    else:
        messages.error(request, 'Acesso negado! Essa função só está disponível para organizadores.')
        return HttpResponseRedirect(reverse('eventos:evento_detalhes', args=(pk,)))
        
    inscricao.delete()
    messages.success(request, 'Inscrição cancelada.')
    return HttpResponseRedirect(reverse('eventos:confirmar_inscricao', args=(inscricao.evento.pk,)))

@login_required(login_url='/login/')
def atividade_new(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    if evento.is_organizador(request.user):
        pass
    else:
        messages.error(request, 'Acesso negado! Essa função só está disponível para organizadores.')
        return HttpResponseRedirect(reverse('eventos:evento_detalhes', args=(pk,)))

    if request.method =="POST":
        form = AtividadeForm(request.POST)
        if form.is_valid():
            nome = form.cleaned_data['nome']
            descricao = form.cleaned_data['descricao']
            tipo = form.cleaned_data['tipo']
            doscente = form.cleaned_data['doscente']
            certificado = form.cleaned_data['certificado']
            cargahoraria = form.cleaned_data['cargahoraria']
            porcent_minimo = form.cleaned_data['porcent_minimo']
            num_vagas = form.cleaned_data['num_vagas']
    else:
        form = AtividadeForm(evento=evento)
        papel = 'O'
    context = {
        'evento': evento,
        'form':form,
        'papel':papel,
    }
    return render(request, 'eventos/atividade_add.html', context)

#Lista a programação do evento
def evento_atividade(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    palestras = Atividade.objects.filter(evento=evento, tipo='P')
    cursos = Atividade.objects.filter(evento=evento, tipo='C')
    if Inscricao.objects.filter(inscrito=request.user, evento=evento, status='C').exists():
        inscrito = Inscricao.objects.get(inscrito=request.user, evento=evento)
        papel = inscrito.papel
    else:
        papel = ''
    context = {
        'evento': evento,
        'palestras':palestras,
        'cursos':cursos,
        'papel':papel,
    }
    return render(request, 'eventos/programacao.html', context)

@login_required(login_url='/login/')
def atividade_detalhes(request, pk):
    atividade = get_object_or_404(Atividade, pk=pk)
    if atividade.evento.is_organizador(request.user):
        pass
    elif atividade.is_doscente(request.user):
        pass
    elif atividade.is_aluno(request.user):
        pass
    else:
        messages.error(request, 'Acesso negado! Você não está inscrito nessa atividade.')
        return HttpResponseRedirect(reverse('eventos:evento_detalhes', args=(atividade.evento.pk,)))
        #return HttpResponseRedirect('/')

    inscrito = Inscricao.objects.get(inscrito=request.user, evento=atividade.evento, status='C')
    aulas = Aula.objects.filter(atividade=atividade)
    arquivos = Arquivo.objects.filter(atividade=atividade)
    papel = inscrito.papel
    context = {
        'evento':atividade.evento,
        'atividade':atividade,
        'papel':papel,
        'aulas':aulas,
        'arquivos':arquivos,
    }
    return render(request, 'eventos/atividade.html', context)

@login_required(login_url='/login/')
def aula_new(request, pk):
    atividade =get_object_or_404(Atividade, pk=pk)
    if atividade.is_doscente(usuario=request.user):
        pass
    else:
        messages.error(request, 'Acesso negado! Você não está inscrito como doscente desta atividade')
        #return HttpResponseRedirect('/')
        return HttpResponseRedirect(reverse('eventos:evento_detalhes', args=(atividade.evento.pk,)))

    if request.method =="POST":
        form = AulaForm(request.POST)
        if form.is_valid():
            aula = form.save(commit=False)
            aula.atividade = atividade
            aula.save()
            messages.success(request, 'Aula cadastrada com sucesso')
            return HttpResponseRedirect(reverse('eventos:atividade_detalhes', args=(pk,)))
    else:
        form = AulaForm()
        papel = 'D'
    context = {
        'evento':atividade.evento,
        'atividade':atividade,
        'form':form,
        'papel':papel,
    }   
    return render(request, 'eventos/aula_add.html', context)

@login_required(login_url='/login/')
def presentes(request, pk):
    aula = get_object_or_404(Aula, pk=pk)
    evento = aula.atividade.evento
    if aula.atividade.is_doscente(usuario=request.user):
        pass
    else:
        messages.error(request, 'Acesso negado! Você não está inscrito como doscente desta atividade')
        #return HttpResponseRedirect('/')
        return HttpResponseRedirect(reverse('eventos:evento_detalhes', args=(atividade.evento.pk,)))

    inscritos = Inscricao_atividade.objects.filter(atividade=aula.atividade)
    if request.method =="POST":
        form = request.POST
        numform = form.cleaned_data['form-num']
        x = 0
        while x < numform:
            presente = form.cleaned_data['form-'+x+'-presente']
            participante = form.cleaned_data['form-'+x+'-participante']
            presenca = Presenca(participante=participante, aula=aula, presente=presente)
            presenca.save()
            x = x+1
        return HttpResponseRedirect(reverse('eventos:atividade_detalhes', args=(aula.atividade.pk,)))
    
    context = {
        'evento':aula.atividade.evento,
        'atividade':aula.atividade,
        'inscritos':inscritos,
        #'formset':formset,
        'papel':'D',
    }   
    return render(request, 'eventos/presenca.html', context)

@login_required(login_url='/login/')
def arquivo_new(request, pk):
    atividade =get_object_or_404(Atividade, pk=pk)
    if atividade.is_doscente(usuario=request.user):
        pass
    else:
        messages.error(request, 'Acesso negado! Você não está inscrito como doscente desta atividade')
        #return HttpResponseRedirect('/')
        return HttpResponseRedirect(reverse('eventos:evento_detalhes', args=(atividade.evento.pk,)))

    if request.method =="POST":
        form = ArquivoForm(request.POST, request.FILES)
        if form.is_valid():
            arquivo = form.save(commit=False)
            arquivo.atividade = atividade
            arquivo.save()
            return HttpResponseRedirect(reverse('eventos:atividade_detalhes', args=(atividade.pk,)))
    else:
        form = ArquivoForm()
        papel = 'D'
    context = {
        'evento':atividade.evento,
        'atividade':atividade,
        'form':form,
        'papel':papel,
    }
    return render(request, 'eventos/arquivo_add.html', context)

@login_required(login_url='/login/')
def impressos(request, pk):
    evento = get_object_or_404(Evento, pk=pk)

    if evento.is_organizador(request.user):
        pass
    else:
        messages.error(request, 'Acesso negado! Essa função só está disponível para organizadores.')
#            return HttpResponseRedirect('/')
        return HttpResponseRedirect(reverse('eventos:evento_detalhes', args=(pk,)))

    inscritos_atividade = Inscricao_atividade.objects.filter(atividade__evento=evento)
    atividades = Atividade.objects.filter(evento=evento)
    context = {
        'evento':evento,
        'inscritos_atividade':inscritos_atividade,
        'atividades':atividades,
        'papel':'O',
    }
    return render(request, 'eventos/impressos.html', context)

@login_required(login_url='/login/')
def lista_participantes(request, ev, at):
    evento = get_object_or_404(Evento, pk=ev)
    if evento.is_organizador(request.user):
        pass
    else:
        messages.error(request, 'Acesso negado! Essa função só está disponível para organizadores.')
#            return HttpResponseRedirect('/')
        return HttpResponseRedirect(reverse('eventos:evento_detalhes', args=(pk,)))

    inscritos_atividade = Inscricao_atividade.objects.filter(atividade=at)
    atividades = Atividade.objects.filter(evento=evento)
    context = {
        'evento':evento,
        'inscritos_atividade':inscritos_atividade,
        'atividades':atividades,
        'papel':'O',
    }
    return render(request, 'eventos/listas.html', context)

@login_required(login_url='/login/')
def crachas(request, ev, at):
    evento = get_object_or_404(Evento, pk=ev)
    if evento.is_organizador(request.user):
        pass
    else:
        messages.error(request, 'Acesso negado! Essa função só está disponível para organizadores.')
#            return HttpResponseRedirect('/')
        return HttpResponseRedirect(reverse('eventos:evento_detalhes', args=(pk,)))

    inscritos_atividade = Inscricao_atividade.objects.filter(atividade=at)
    atividades = Atividade.objects.filter(evento=evento)
    context = {
        'evento':evento,
        'inscritos_atividade':inscritos_atividade,
        'atividades':atividades,
        'papel':'O',
    }
    return render(request, 'eventos/crachas.html', context)

@login_required(login_url='/login/')
def certificados(request, ev, at):
    evento = get_object_or_404(Evento, pk=ev)
    if evento.is_organizador(request.user):
        pass
    else:
        messages.error(request, 'Acesso negado! Essa função só está disponível para organizadores.')
#            return HttpResponseRedirect('/')
        return HttpResponseRedirect(reverse('eventos:evento_detalhes', args=(pk,)))

    inscritos_atividade = Inscricao_atividade.objects.filter(atividade=at)
    atividade = Atividade.objects.get(pk=at)
    if (atividade.porcent_minimo > 0):
        minpresenca = atividade__aula.count() * (atividade.porcent_minimo * 100)
        aprovados = inscritos_atividade.filter(atividade__presenca.count() >= minpresenca)
    else:
        aprovados = inscritos_atividade

    context = {
        'evento':evento,
        'aprovados':aprovados,
        'atividade':atividade,
        'papel':'O',
    }
    return render(request, 'eventos/certificados.html', context)

#@login_required(login_url='/login/')
def mensagem(request, ev, at):
    evento = get_object_or_404(Evento, pk=ev)
    if request.method =="POST":
        form = EmailForm(data=request.POST, evento=evento)
        if form.is_valid(): 
            form.send_mail(request.user)
            messages.success(request, 'Mensagem enviada com sucesso!')

    else:
        form = EmailForm(evento=evento)
    papel = ''
    context = {
        'evento':evento,
        'form':form,
        'papel':papel,
    }  
    return render(request, 'eventos/mensagem.html', context)