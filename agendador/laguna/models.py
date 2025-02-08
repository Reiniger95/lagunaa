from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.conf import settings
import datetime
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
    ("09:00", "09:00"),
    ("10:00", "10:00"),
    ("21:00", "21:00"),
    # Adicione quantos horários precisar.
]
class Court(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Reservation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    court = models.ForeignKey(Court, on_delete=models.CASCADE)
    date = models.DateField()
    time_slot = models.TimeField()
    name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.email} - {self.court.name} - {self.date} {self.time_slot}"
    
class CustomUserManager(BaseUserManager):
    def create_user(self, email, phone, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, phone, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']

    def __str__(self):
        return self.email
    
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