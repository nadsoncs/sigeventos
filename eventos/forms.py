from django import forms
from django.contrib.auth.models import User
from .models import *
from django.core.mail import send_mail
from django.conf import settings

class RegistrerForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ('username','first_name', 'last_name', 'email', 'password')
		labels = {
			'first_name': 'Nome',
			'last_name': 'Sobrenome',
		}
		widgets = {
			'password': forms.PasswordInput(),
		}
class PerfilForm(forms.ModelForm):
	class Meta:
		model = UserProfile
		fields = ('sexo', 'cep', 'estado', 'cidade', 'bairro', 'logradouro', 'numero', 'complemento', 'avatar')
		
class UserForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'email')
		labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
        }

class LoginForm(forms.Form):
    user = forms.CharField(label='Usuário')
    password = forms.CharField(label='Senha', widget=forms.PasswordInput)

class AtividadeForm(forms.Form):
	opt_tipo = (
		('P', 'Palestra'), 
		('C', 'Curso'),
	)
	opt_certificado = (
		('S', 'Sim'), 
		('N', 'Não'),
	)

	nome = forms.CharField(label='Nome', max_length=100)
	descricao = forms.CharField(label='Descrição', widget=forms.Textarea, max_length=200)
	tipo = forms.ChoiceField(widget=forms.Select, choices=opt_tipo)
	doscente = forms.ModelChoiceField(queryset=Inscricao.objects.all(), empty_label="Selecione",widget=forms.Select)
	certificado = forms.ChoiceField(widget=forms.Select, choices=opt_certificado)
	cargahoraria = forms.IntegerField(label='Carga Horária')
	porcent_minimo = forms.IntegerField(label='Porcentagem Mínima')
	num_vagas = forms.IntegerField(label='Número de vagas')

	def __init__(self, evento, *args, **kwargs):
		super(AtividadeForm, self).__init__(*args, **kwargs)
		self.fields['doscente'].queryset = Inscricao.objects.filter(evento=evento, papel='D')

class InscricaoForm(forms.Form):
	"""docstring for InscricaoForm"""
	atividades = forms.ModelChoiceField(queryset=Atividade.objects.all(), empty_label="Nenhum", widget=forms.RadioSelect)
	def __init__(self,evento=None, *args, **kwargs):
		super(InscricaoForm, self).__init__(*args, **kwargs)
		if (evento):
			self.fields['atividades'].queryset = Atividade.objects.filter(evento=evento)

	def clean_email(self):
		atividades =self.cleaned_data['atividades']
		if Inscricao_atividade.objects.filter(atividade=atividades, inscricao=request.user__inscricao).exists():
			raise forms.ValidationError('Usuário já está inscrito no evento')
		return atividades
		
class EventoForm(forms.ModelForm):
	class Meta:
		model = Evento
		fields = ('nome', 'local', 'descricao', 'dt_inicio', 'dt_fim', 'dt_ini_inscricao', 'dt_fim_inscricao', 'url')

class AulaForm(forms.ModelForm):
	class Meta:
		model = Aula
		fields = ('descricao', 'dt_inicio', 'hr_inicio', 'hr_fim')
		widgets = {
            'dt_inicio': forms.DateTimeInput(attrs={'class':'datepicker form-control'}),
            'hr_inicio': forms.TimeInput(attrs={'class':'datepicker form-control'}),
            'hr_fim': forms.TimeInput(attrs={'class':'datepicker form-control'}),
        }

class ArquivoForm(forms.ModelForm):
	class Meta:
		model = Arquivo
		fields = ('filename', 'upload')

class PresencaForm(forms.ModelForm):
	class Meta:
		model = Presenca
		fields = ('participante', 'aula', 'presente')
		widgets = {
			'participante': forms.Select(attrs={'disabled':True, 'class':'form-control'}),
			'aula': forms.HiddenInput(),
			'presente': forms.CheckboxInput(),
		}

class EmailForm(forms.Form):
	assunto = forms.CharField(label='Assunto', max_length=100)
	#email = forms.EmailField(label='E-mail')
	message = forms.CharField(
		label='Mensagem', widget=forms.Textarea
	)
	para = forms.ModelChoiceField(queryset=Inscricao.objects.all(), empty_label="Nenhum", widget=forms.Select)
	def __init__(self,evento=None, *args, **kwargs):
		super(EmailForm, self).__init__(*args, **kwargs)
		self.fields['para'].queryset = Inscricao.objects.filter(evento=evento)

	def send_mail(self, msgde):
		#subject = 'Contato Curso %s' course
		subject = self.cleaned_data['assunto']
		message = 'Nome: %(name)s;E-mail: %(email)s;%(message)s'
		context = {
			'name': msgde.first_name,
			'email': msgde.email,
			'message': self.cleaned_data['message'],
		}
		inscricao = self.cleaned_data['para']
		destinatario = inscricao.inscrito.email
		FROM_EMAIL = msgde.email
		TO_EMAIL = destinatario
		message = message % context
		send_mail(
			subject, message, FROM_EMAIL, [TO_EMAIL]
		)
   
		
	
		