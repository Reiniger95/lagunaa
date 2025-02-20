from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Court, Reservation, RecurringReservation, CustomUser, BBQ, BBQReservation
from datetime import date, timedelta

class CustomAdminSite(admin.AdminSite):
    site_header = 'Administração do Sistema'
    site_title = 'Administração'
    index_title = 'Painel de Administração'

    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        for app in app_list:
            for model in app['models']:
                if model['object_name'] == 'Court':
                    model['name'] = 'Quadras'
                elif model['object_name'] == 'Reservation':
                    model['name'] = 'Reservas'
                elif model['object_name'] == 'RecurringReservation':
                    model['name'] = 'Reservas Recorrentes'
                elif model['object_name'] == 'CustomUser':
                    model['name'] = 'Usuários'
                elif model['object_name'] == 'BBQ':
                    model['name'] = 'Churrasqueiras'
                elif model['object_name'] == 'BBQReservation':
                    model['name'] = 'Reservas de Churrasqueiras'
        return app_list

custom_admin_site = CustomAdminSite(name='custom_admin')

@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'court', 'date', 'time_slot')

@admin.register(BBQ)
class BBQAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')

@admin.register(BBQReservation)
class BBQReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'bbq', 'date', 'time_slot')

@admin.register(RecurringReservation)
class RecurringReservationAdmin(admin.ModelAdmin):
    list_display = ['user', 'court', 'day_of_week', 'time_slot', 'name']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Após salvar o novo registro, cria as reservas para os próximos 30 dias
        hoje = date.today()
        fim = hoje + timedelta(days=30)

        dia_atual = hoje
        while dia_atual <= fim:
            if dia_atual.weekday() == obj.day_of_week:
                # Evita duplicar caso já exista
                ja_existe = Reservation.objects.filter(
                    user=obj.user,
                    court=obj.court,
                    date=dia_atual,
                    time_slot=obj.time_slot
                ).exists()
                if not ja_existe:
                    Reservation.objects.create(
                        user=obj.user,
                        court=obj.court,
                        date=dia_atual,
                        time_slot=obj.time_slot,
                        name=obj.name
                    )
            dia_atual += timedelta(days=1)

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'phone', 'full_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('phone', 'full_name')}),
        ('Permissões', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login',)}),  # Remova 'date_joined'
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone', 'full_name', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email', 'phone', 'full_name')
    ordering = ('email',)

admin.site = custom_admin_site
admin.site.register(Court, CourtAdmin)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(BBQ, BBQAdmin)
admin.site.register(BBQReservation, BBQReservationAdmin)
admin.site.register(RecurringReservation, RecurringReservationAdmin)
admin.site.register(CustomUser, CustomUserAdmin)