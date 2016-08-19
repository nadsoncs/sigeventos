from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.

class UserProfile(models.Model):
	opt_sexo = (
		('M', 'Masculino'),
		('F', 'Feminino'),
	)
	opt_estado = (
		('ac', 'Acre'),
		('al', 'Alagoas'),
		('am', 'Amazonas'),
		('ap', 'Amapá'),
		('ba', 'Bahia'),
		('ce', 'Ceará'),
		('df', 'Distrito Federal'),
		('es', 'Espírito Santo'),
		('go', 'Goiás'),
		('ma', 'Maranhão'),
		('mt', 'Mato Grosso'),
		('ms', 'Mato Grosso do Sul'),
		('mg', 'Minas Gerais'),
		('pa', 'Pará'),
		('pb', 'Paraíba'),
		('pr', 'Paraná'),
		('pe', 'Pernambuco'),
		('pi', 'Piauí'),
		('rj', 'Rio de Janeiro'),
		('rn', 'Rio Grande do Norte'),
		('ro', 'Rondônia'),
		('rs', 'Rio Grande do Sul'),
		('rr', 'Roraima'),
		('sc', 'Santa Catarina'),
		('se', 'Sergipe'),
		('sp', 'São Paulo'),
		('to', 'Tocantins'),
	)
	user   = models.OneToOneField('auth.User', related_name="profile")
	sexo = models.CharField(max_length=1, choices=opt_sexo)
	cep = models.CharField('CEP', max_length=9)
	estado = models.CharField(max_length=2, choices=opt_estado)
	cidade = models.CharField('Cidade', max_length=100)
	bairro = models.CharField('Bairro', max_length=100)
	logradouro = models.CharField('Logradouro', max_length=200)
	numero = models.PositiveSmallIntegerField('Número')
	complemento = models.CharField('Complemento', max_length=200, blank=True, null=True)
	avatar = models.ImageField("Imagem perfil", upload_to="images/users", blank=True, null=True)
	def __str__(self):
		return self.user.username

	def avatar_image(self):
		return (MEDIA_URL + self.avatar.name) if self.avatar else None

class Evento(models.Model):
	"""docstring for Evento"""
	opt_tipo = (
		('P', 'Pago'),
		('G', 'Gratuito'),
	)
	nome = models.CharField(max_length=100)
	local = models.CharField(max_length=100)
	descricao = models.TextField(max_length=200)
	dt_inicio = models.DateTimeField('Data de início do evento')
	dt_fim = models.DateTimeField('Data final do evento')
	dt_ini_inscricao = models.DateTimeField('Início das inscrições')
	dt_fim_inscricao = models.DateTimeField('Fim das inscrições')
	logomarca = models.ImageField(upload_to='logoeventos/%Y/%m/%d', null=True)
	tipo = models.CharField(max_length=1, choices=opt_tipo)
	url = models.URLField(blank=True, null=True)

	def __str__(self):
		return self.nome

	def get_doscentes(self):
		return self.inscricao.all().filter(papel = 'D')

	def is_organizador(self, usuario):
		if Inscricao.objects.filter(papel ='O', inscrito=usuario, evento=self).exists():
			return True
		else:
			return False
	
	def get_atividade(self, usuario):
		if Inscricao.objects.filter(inscrito=usuario, evento=self).exists():
			inscricao = Inscricao.objects.get(inscrito=usuario, evento=self, status='C')
			if inscricao.papel == 'D':
				return Atividade.objects.get(evento=self, doscente=inscricao)
			elif inscricao.papel == 'P':
				ins_at = Inscricao_atividade.objects.get(inscricao=inscricao)
				return ins_at.atividade
			else:
				return None
		else:
			False

class Inscricao(models.Model):
	"""docstring for Inscricao"""
	opt_status = (
		('S', 'Solicitado'),
		('C', 'Confirmado'),
	)
	opt_papel = (
		('P', 'Participante'),
		('O', 'Organizador'),
		('D', 'Doscente'),
	)

	inscrito = models.ForeignKey('auth.User')
	evento = models.ForeignKey(Evento)
	papel = models.CharField(max_length=1, choices=opt_papel)
	status = models.CharField(max_length=1, choices=opt_status)

	def __str__(self):
		return "%s %s" % (self.inscrito.first_name, self.inscrito.last_name)


class Atividade(models.Model):
	"""docstring for Atividade"""
	opt_tipo = (
		('P', 'Palestra'),
		('C', 'Curso'),
	)
	opt_certificado = (
		('S', 'Sim'),
		('N', 'Não'),
	)
	evento = models.ForeignKey(Evento)
	nome = models.CharField(max_length=100)
	descricao = models.TextField(max_length=200)
	tipo = models.CharField(max_length=1, choices=opt_tipo)
	doscente = models.ForeignKey(Inscricao)
	certificado = models.CharField(max_length=1, choices=opt_certificado)
	cargahoraria = models.PositiveSmallIntegerField()
	porcent_minimo = models.PositiveSmallIntegerField()
	num_vagas = models.PositiveSmallIntegerField()
	def __str__(self):
		return "%s" % (self.nome)

	def is_doscente(self, usuario):
		if self.doscente.inscrito == usuario:
			return True
		else:
			return False

	def is_aluno(self, usuario):
		if Inscricao.objects.filter(papel ='P', inscrito=usuario, evento=self.evento, status='C').exists():
			aluno = Inscricao.objects.get(papel ='P', inscrito=usuario, evento=self.evento, status='C')
			if Inscricao_atividade.objects.filter(inscricao=aluno, atividade=self).exists():
				return True
			else:
				return False
		else:
			return False


class Inscricao_atividade(models.Model):
	"""docstring for Inscricao_atividade"""
	inscricao = models.ForeignKey(Inscricao)
	atividade = models.ForeignKey(Atividade)
	
		
class Arquivo(models.Model):
	"""docstring for Arquivo"""
	atividade = models.ForeignKey(Atividade)
	filename = models.CharField(max_length=100)
	upload = models.FileField(upload_to='uploads/atividades/')
	

class Aula(models.Model):
	"""docstring for cronograma"""
	atividade = models.ForeignKey(Atividade)
	descricao = models.TextField(max_length=200)
	dt_inicio = models.DateTimeField('Data')
	hr_inicio = models.TimeField('Hora de início')
	hr_fim = models.TimeField('Hora fim')
	#dt_fim = models.DateTimeField('Data final da atividade')
	

class Presenca(models.Model):
	"""docstring for Presenca"""
	opt_presenca = (
		('P', 'Presente'),
		('F', 'Faltou'),
	)
	participante = models.ForeignKey(Inscricao)
	aula = models.ForeignKey(Aula)
	presente = models.CharField(max_length=1, choices=opt_presenca)
	
	