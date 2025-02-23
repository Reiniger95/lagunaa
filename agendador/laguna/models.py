from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.conf import settings
import datetime
from datetime import date, timedelta
from django.utils import timezone
DAYS_OF_WEEK_CHOICES = [
    (0, "Segunda"),
    (1, "Terça"),
    (2, "Quarta"),
    (3, "Quinta"),
    (4, "Sexta"),
    (5, "Sábado"),
    (6, "Domingo"),
]

TIME_SLOT_CHOICES = [
    ("06:00", "06:00"),
    ("07:00", "07:00"),
    ("08:00", "08:00"),
    ("09:00", "09:00"),
    ("10:00", "10:00"),
    ("11:00", "11:00"),
    ("12:00", "12:00"),
    ("13:00", "13:00"),
    ("14:00", "14:00"),
    ("15:00", "15:00"),
    ("16:00", "16:00"),
    ("17:00", "17:00"),
    ("18:00", "18:00"),
    ("19:00", "19:00"),
    ("20:00", "20:00"),
    ("21:00", "21:00"),
    ("22:00", "22:00"),
    ("23:00", "23:00"),
    # Adicione quantos horários precisar.
]
class Court(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class BBQ(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class BBQReservation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bbq = models.ForeignKey(BBQ, on_delete=models.CASCADE)
    date = models.DateField()
    time_slot = models.TimeField()
    name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.email} - {self.bbq.name} - {self.date} {self.time_slot}"

class Reservation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    court = models.ForeignKey(Court, on_delete=models.CASCADE)
    date = models.DateField()
    time_slot = models.TimeField()
    name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.email} - {self.court.name} - {self.date} {self.time_slot}"
    
class CustomUserManager(BaseUserManager):
    def create_user(self, email, phone, full_name=None, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, phone=phone, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, phone,full_name=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, phone, full_name, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    full_name = models.CharField(max_length=255, blank=True, null=True)  # Adicionando o campo full_name
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_member = models.BooleanField(default=False)  # Novo campo para indicar se o usuário é sócio
    membership_venc_date = models.DateField(blank=True, null=True)  # Novo campo para a data da última mensalidade paga

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']

    def __str__(self):
        return self.email
    
    def check_membership_status(self):
        if self.membership_venc_date and self.membership_venc_date < date.today():
            self.is_member = False
            self.save()

    def renew_membership(self):
        if self.membership_venc_date and self.membership_venc_date >= date.today():
            self.membership_venc_date += timedelta(days=30)
        else:
            self.membership_venc_date = timezone.now().date() + timedelta(days=30)
        self.is_member = True
        self.save()
    
class RecurringReservation(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    court = models.ForeignKey(Court, on_delete=models.CASCADE)
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK_CHOICES)
    # Se quiser armazenar como time verdadeiro, use um TimeField e converta a escolha; 
    # ou guarde como CharField para simplificar.
    time_slot = models.CharField(
        max_length=5,
        choices=TIME_SLOT_CHOICES,
        help_text="Selecione o horário fixo (hh:mm)"
    )
    name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Recorrente: {self.user.email} - {self.court.name} (Dia {self.day_of_week}, {self.time_slot})"

class Modalidade(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Caixa(models.Model):
    METODO_PAGAMENTO_CHOICES = [
        ('dinheiro', 'Dinheiro'),
        ('pix', 'Pix'),
        ('cartao_debito', 'Cartão Débito'),
        ('cartao_credito', 'Cartão Crédito'),
        ('fiado', 'Fiado'),
    ]

    modalidade = models.ForeignKey(Modalidade, on_delete=models.CASCADE)
    data = models.DateField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pagamento = models.CharField(max_length=20, choices=METODO_PAGAMENTO_CHOICES)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.modalidade.nome} - {self.data} - {self.valor} - {self.metodo_pagamento}"