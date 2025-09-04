from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, LoginForm, DateForm, TimeSlotForm, ReservationForm
from .models import Court, CustomUser, Reservation, BBQ, BBQReservation, Modalidade, Caixa, RecurringReservation
from django.contrib import messages
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime, time, timedelta
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'registro.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})



@login_required(login_url='login/')
def home_view(request):
    return render(request, 'home.html')



@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def select_date_view(request):
    if request.method == 'POST':
        form = DateForm(request.POST)
        if form.is_valid():
            request.session['date'] = form.cleaned_data['date'].isoformat()
            return redirect('select_time_slot')
    else:
        form = DateForm()
    return render(request, 'select_date.html', {'form': form})

@login_required
def select_date_bbq_view(request):
    if request.method == 'POST':
        form = DateForm(request.POST)
        if form.is_valid():
            request.session['date'] = form.cleaned_data['date'].isoformat()
            return redirect('select_time_slot_bbq')
    else:
        form = DateForm()
    return render(request, 'select_date_bbq.html', {'form': form})


@login_required
def select_time_slot_view(request):
    date_str = request.session.get('date')
    if not date_str:
        return redirect('select_date')
    
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    available_times = []
    total_courts = Court.objects.count()
    
    # Exemplo de horários disponíveis
    all_times = [
        "09:00", "10:00", "11:00", "12:00", "13:00",
        "14:00", "15:00", "16:00", "17:00", "18:00",
        "19:00", "20:00", "21:00", 
    ]

    # Obter o dia da semana (0 = segunda-feira, 6 = domingo)
    day_of_week = date.weekday()

    if day_of_week == 5:  # Sábado
        valid_times = ["09:00", "10:00", "11:00", "12:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00"]
    elif day_of_week == 6:  # Domingo
        valid_times = ["10:00", "11:00", "15:00", "16:00"]
    else:  # Segunda a Sexta
        valid_times = [time for time in all_times if time >= "09:00" and time <= "21:00"]

    for time_str in valid_times:
        hour, minute = map(int, time_str.split(':'))
        start_time = time(hour, minute)
        reservations = Reservation.objects.filter(date=date, time_slot=start_time).count()
        if reservations >= total_courts:
            available_times.append((time_str, False))  # False indicates not available
        else:
            available_times.append((time_str, True))  # True indicates available

    if request.method == 'POST':
        form = TimeSlotForm(request.POST)
        if form.is_valid():
            request.session['time_slot'] = form.cleaned_data['time_slot']
            return redirect('select_court')
    else:
        form = TimeSlotForm()

    return render(request, 'select_time_slot.html', {'form': form, 'available_times': available_times})
@login_required
def select_time_slot_bbq_view(request):
    date = request.session.get('date')
    available_times = []
    total_bbqs = BBQ.objects.count()
    
    # Defina os horários específicos para churrasqueiras
    time_slots = [time(12, 0), time(18, 0)]
    
    for start_time in time_slots:
        reservations = BBQReservation.objects.filter(date=date, time_slot=start_time).count()
        if reservations >= total_bbqs:
            available_times.append((start_time.strftime('%H:%M'), False))  # False indicates not available
        else:
            available_times.append((start_time.strftime('%H:%M'), True))  # True indicates available

    if request.method == 'POST':
        form = TimeSlotForm(request.POST)
        if form.is_valid():
            request.session['time_slot'] = form.cleaned_data['time_slot']
            return redirect('select_bbq')
    else:
        form = TimeSlotForm()

    return render(request, 'select_time_slot_bbq.html', {'form': form, 'available_times': available_times})
@login_required
def select_bbq_view(request):
    date = request.session.get('date')
    time_slot = request.session.get('time_slot')
    available_bbqs = BBQ.objects.exclude(
        bbqreservation__date=date,
        bbqreservation__time_slot=time_slot
    )
    if request.method == 'POST':
        bbq_id = request.POST.get('bbq_id')
        bbq = BBQ.objects.get(id=bbq_id)
        BBQReservation.objects.create(
            user=request.user,
            bbq=bbq,
            date=date,
            time_slot=time_slot
        )
        return redirect('home')
    return render(request, 'select_bbq.html', {'bbqs': available_bbqs})
@login_required
def select_court_view(request):
    date = request.session.get('date')
    time_slot = request.session.get('time_slot')
    
    # Log para depuração
    print(f"Select Court - Date: {date}, Time Slot: {time_slot}")
    
    # Obter todas as quadras
    all_courts = Court.objects.all()
    print(f"Total courts: {all_courts.count()}")
    
    # Obter quadras já reservadas para esta data e horário
    reserved_courts_ids = Reservation.objects.filter(
        date=date,
        time_slot=time_slot
    ).values_list('court_id', flat=True)
    
    print(f"Reserved court IDs: {list(reserved_courts_ids)}")
    
    # Filtrar apenas as quadras disponíveis
    available_courts = all_courts.exclude(id__in=reserved_courts_ids)
    print(f"Available courts: {available_courts.count()}")

    # Se não houver quadras disponíveis, adicione uma mensagem de erro
    if not available_courts:
        print("Atenção: Não há quadras disponíveis para este horário!")
    
    if request.method == 'POST':
        court_id = request.POST.get('court_id')
        court = Court.objects.get(id=court_id)
        
        # Verificar novamente se a quadra está disponível antes de criar a reserva
        if Reservation.objects.filter(court=court, date=date, time_slot=time_slot).exists():
            print(f"ERRO: Court ID {court_id} já está reservado para {date} às {time_slot}")
            # Aqui você pode adicionar uma mensagem de erro para o usuário
            return redirect('select_court')
        
        # Criar a reserva
        Reservation.objects.create(
            user=request.user,
            court=court,
            date=date,
            time_slot=time_slot
        )
        print(f"Reserva criada com sucesso para Court ID {court_id}")
        return redirect('home')
    
    return render(request, 'select_court.html', {'courts': available_courts})
@login_required
def agenda_view(request):
    now = timezone.now()
    yesterday = now.date() - timedelta(days=1)
    
    # Carregar as reservas
    court_reservations = Reservation.objects.filter(date__gte=yesterday, user=request.user).order_by('date', 'time_slot')
    bbq_reservations = BBQReservation.objects.filter(date__gte=yesterday, user=request.user).order_by('date', 'time_slot')
    
    # Depuração para verificar valores
    print(f"Current time: {now}")
    
    for reservation in court_reservations:
        # Combine a data e hora da reserva em um objeto datetime
        reservation_datetime = datetime.combine(reservation.date, reservation.time_slot)
        # Converta para um objeto aware (com timezone)
        reservation_datetime = timezone.make_aware(reservation_datetime)
        
        # Calcular a diferença de tempo
        time_diff = reservation_datetime - now
        hours_diff = time_diff.total_seconds() / 3600
        
        # Debug - imprimir informações
        print(f"Court Reservation: {reservation.id}, Date: {reservation.date}, Time: {reservation.time_slot}")
        print(f"Reservation datetime: {reservation_datetime}")
        print(f"Time difference: {hours_diff:.2f} hours")
        
        # Verifique se faltam mais de 24 horas
        reservation.can_delete = time_diff.total_seconds() > 24 * 3600
        print(f"Can delete: {reservation.can_delete}")
    
    for reservation in bbq_reservations:
        # Combine a data e hora da reserva em um objeto datetime
        reservation_datetime = datetime.combine(reservation.date, reservation.time_slot)
        # Converta para um objeto aware (com timezone)
        reservation_datetime = timezone.make_aware(reservation_datetime)
        
        # Calcular a diferença de tempo
        time_diff = reservation_datetime - now
        hours_diff = time_diff.total_seconds() / 3600
        
        # Debug - imprimir informações
        print(f"BBQ Reservation: {reservation.id}, Date: {reservation.date}, Time: {reservation.time_slot}")
        print(f"Reservation datetime: {reservation_datetime}")
        print(f"Time difference: {hours_diff:.2f} hours")
        
        # Verifique se faltam mais de 24 horas
        reservation.can_delete = time_diff.total_seconds() > 24 * 3600
        print(f"Can delete: {reservation.can_delete}")
    
    return render(request, 'agenda.html', {
        'court_reservations': court_reservations,
        'bbq_reservations': bbq_reservations
    })
@login_required
def delete_reservation_view(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    
    now = timezone.now()
    reservation_datetime = datetime.combine(reservation.date, reservation.time_slot)
    reservation_datetime = timezone.make_aware(reservation_datetime)
    
    time_diff = reservation_datetime - now
    hours_diff = time_diff.total_seconds() / 3600
    
    print(f"Delete Court Reservation: {reservation.id}")
    print(f"Current time: {now}")
    print(f"Reservation datetime: {reservation_datetime}")
    print(f"Time difference: {hours_diff:.2f} hours")
    
    if time_diff.total_seconds() > 24 * 3600:
        reservation.delete()
        print("Reservation deleted successfully")
    else:
        print(f"Não é possível excluir reservas com menos de 24 horas de antecedência. Faltam {hours_diff:.2f} horas.")
    
    return redirect('agenda')

@login_required
def delete_bbq_reservation_view(request, reservation_id):
    reservation = get_object_or_404(BBQReservation, id=reservation_id, user=request.user)
    
    now = timezone.now()
    reservation_datetime = datetime.combine(reservation.date, reservation.time_slot)
    reservation_datetime = timezone.make_aware(reservation_datetime)
    
    time_diff = reservation_datetime - now
    hours_diff = time_diff.total_seconds() / 3600
    
    print(f"Delete BBQ Reservation: {reservation.id}")
    print(f"Current time: {now}")
    print(f"Reservation datetime: {reservation_datetime}")
    print(f"Time difference: {hours_diff:.2f} hours")
    
    if time_diff.total_seconds() > 24 * 3600:
        reservation.delete()
        print("BBQ Reservation deleted successfully")
    else:
        print(f"Não é possível excluir reservas com menos de 24 horas de antecedência. Faltam {hours_diff:.2f} horas.")
    
    return redirect('agenda')
@staff_member_required
def admin_schedule_view(request):
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    date_str = request.GET.get('date', datetime.today().strftime('%Y-%m-%d'))
    error_message = None
    bbq_reservations = BBQReservation.objects.filter(date__gte=yesterday).order_by('date', 'time_slot')
    try:
        date_chosen = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        # Se a string enviada não estiver em formato '%Y-%m-%d', usa hoje
        date_chosen = datetime.today().date()
    # Carrega reservas do dia
    reservations_for_day = Reservation.objects.filter(date=date_chosen).order_by('time_slot')
    courts = Court.objects.all()
    hours = range(8, 23)
    members = CustomUser.objects.filter(is_member=True).order_by('membership_venc_date')
    
    for member in members:
        member.check_membership_status()

    if request.method == 'POST' and 'renew_membership' in request.POST:
        user_id = request.POST.get('user_id')
        user = CustomUser.objects.get(id=user_id)
        user.renew_membership()
        try:
            sociedade_mod = Modalidade.objects.get(nome__iexact='sociedade')
        except Modalidade.DoesNotExist:
        # Você pode criar a modalidade se quiser, neste exemplo apenas ignoramos
            sociedade_mod = None

        if sociedade_mod:
            Caixa.objects.create(
                modalidade=sociedade_mod,
                data=timezone.now().date(),
                valor=300,
                metodo_pagamento='dinheiro',
                usuario=user
            )

        return redirect(f"{reverse('admin_schedule')}?tab=socios")
    elif 'create_caixa' in request.POST:
            modalidade_id = request.POST.get('modalidade')
            data = request.POST.get('data')
            valor = request.POST.get('valor')
            metodo_pagamento = request.POST.get('metodo_pagamento')
            usuario_id = request.POST.get('usuario')
            usuario = CustomUser.objects.get(id=usuario_id) if usuario_id else None

            modalidade = Modalidade.objects.get(id=modalidade_id)
            Caixa.objects.create(
                modalidade=modalidade,
                data=data,
                valor=valor,
                metodo_pagamento=metodo_pagamento,
                usuario=usuario
            )
            if modalidade.nome.lower() == "sociedade" and usuario:
                usuario.renew_membership()
                usuario.save()
    
            return redirect(f"{reverse('admin_schedule')}?tab=caixa")

    # Carrega todas as reservas (para a outra aba)
    all_reservations = Reservation.objects.all().order_by('date', 'time_slot')

    # Gera estrutura: lista de linhas, cada linha = hora + listagem das quadras
    schedule_rows = []
    for hour in hours:
        row = {'hour': hour, 'slots': []}
        for court in courts:
            found_res = None
            for reservation in reservations_for_day:
                if reservation.court == court and reservation.time_slot.hour == hour:
                    found_res = reservation
                    break
            row['slots'].append({'court': court, 'reservation': found_res})
        schedule_rows.append(row)

    if request.method == 'POST':
        action = request.POST.get('action')
        court_name = request.POST.get('court')
        time_slot_str = request.POST.get('time_slot')
        time_obj = datetime.strptime(time_slot_str, '%H:%M').time()
        c = Court.objects.get(name=court_name)

        if action == 'create':
            name = request.POST.get('name')
            if Reservation.objects.filter(court=c, date=date_chosen, time_slot=time_obj).exists():
                error_message = "Este horário já está cheio."
            else:
                Reservation.objects.create(
                    user=request.user,
                    court=c,
                    date=date_chosen,
                    time_slot=time_obj,
                    name=name
                )
        elif action == 'delete':
            Reservation.objects.filter(court=c, date=date_chosen, time_slot=time_obj).delete()

        return redirect(f"{reverse('admin_schedule')}?date={date_str}")

    modalidades = Modalidade.objects.all()
    caixas = Caixa.objects.all().order_by('-data')
    users = CustomUser.objects.all()
    filtro_metodo = request.GET.get('metodo', '')
    filtro_data_inicio = request.GET.get('data_inicio', '')
    filtro_data_fim = request.GET.get('data_fim', '')
    caixas_qs = Caixa.objects.all()

    if filtro_metodo:
        caixas_qs = caixas_qs.filter(metodo_pagamento__iexact=filtro_metodo)
    if filtro_data_inicio and filtro_data_fim:
        caixas_qs = caixas_qs.filter(data__range=[filtro_data_inicio, filtro_data_fim])
    filtro_usuario_id = request.GET.get('user_id', '')
    if filtro_usuario_id:
        caixas_qs = caixas_qs.filter(usuario__id=filtro_usuario_id)
    # Ordena por data desc e limita a 30
    caixas = caixas_qs.order_by('-data')[:30]


    recurring_reservations = RecurringReservation.objects.all().order_by('day_of_week', 'time_slot')
    
    # Tratar parâmetro de tab na URL
    active_tab = request.GET.get('tab', '')

    return render(request, 'admin_schedule.html', {
        'date': date_chosen,
        'schedule_rows': schedule_rows,
        'courts': courts,
        'all_reservations': all_reservations,
        'bbq_reservations': bbq_reservations,
        'members': members,
        'modalidades': modalidades,
        'caixas': caixas,
        'users': users,
        'error_message': error_message,
        'recurring_reservations': recurring_reservations,  # Nova variável
        'active_tab': active_tab,  # Para ativar a aba correta
        
    })


@staff_member_required
def delete_caixa(request, caixa_id):
    caixa = get_object_or_404(Caixa, id=caixa_id)
    caixa.delete()
    return redirect(f"{reverse('admin_schedule')}?tab=caixa")

def update_recurring_reservations(request):
    """Atualiza todas as reservas recorrentes para os próximos 90 dias."""
    if not request.user.is_staff:
        messages.error(request, "Você não tem permissão para acessar esta função.")
        return redirect('home')
    
    # Data atual
    hoje = date.today()
    # Data até 90 dias no futuro
    fim = hoje + timedelta(days=90)
    
    # Obter todas as reservas recorrentes
    recurring_reservations = RecurringReservation.objects.all()
    
    count_novas = 0
    
    for recorrente in recurring_reservations:
        dia_atual = hoje
        while dia_atual <= fim:
            # Verificar se o dia da semana corresponde
            if dia_atual.weekday() == recorrente.day_of_week:
                # Converter o time_slot de string para objeto time
                hour, minute = map(int, recorrente.time_slot.split(':'))
                time_obj = time(hour, minute)
                
                # Evitar duplicar caso já exista
                ja_existe = Reservation.objects.filter(
                    user=recorrente.user,
                    court=recorrente.court,
                    date=dia_atual,
                    time_slot=time_obj
                ).exists()
                
                if not ja_existe:
                    # Criar nova reserva
                    Reservation.objects.create(
                        user=recorrente.user,
                        court=recorrente.court,
                        date=dia_atual,
                        time_slot=time_obj,
                        name=recorrente.name
                    )
                    count_novas += 1
            
            dia_atual += timedelta(days=1)
    
    messages.success(
        request, 
        f"As reservas recorrentes foram atualizadas com sucesso! {count_novas} novas reservas foram criadas."
    )
    return redirect(f"{reverse('admin_schedule')}?tab=reservas")

@staff_member_required
def bulk_create_reservations(request):
    if request.method == 'POST':
        date_str = request.POST.get('date')
        name = request.POST.get('name')
        courts = request.POST.getlist('courts[]')
        times = request.POST.getlist('times[]')
        
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Criar todas as reservas
            created_count = 0
            for i in range(len(courts)):
                court_name = courts[i]
                time_str = times[i]
                
                court = Court.objects.get(name=court_name)
                time_obj = datetime.strptime(time_str, '%H:%M').time()
                
                # Verificar se já existe
                if not Reservation.objects.filter(court=court, date=date_obj, time_slot=time_obj).exists():
                    Reservation.objects.create(
                        user=request.user,
                        court=court,
                        date=date_obj,
                        time_slot=time_obj,
                        name=name
                    )
                    created_count += 1
            
            messages.success(request, f"{created_count} reservas foram criadas com sucesso.")
        except Exception as e:
            messages.error(request, f"Erro ao criar reservas: {str(e)}")
        
        # Redirecionar de volta para a página de agenda
        return redirect(f"{reverse('admin_schedule')}?date={date_str}")
    
    return redirect('admin_schedule')

@staff_member_required
def bulk_delete_reservations(request):
    if request.method == 'POST':
        date_str = request.POST.get('date')
        courts = request.POST.getlist('courts[]')
        times = request.POST.getlist('times[]')
        
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Excluir todas as reservas
            deleted_count = 0
            for i in range(len(courts)):
                court_name = courts[i]
                time_str = times[i]
                
                court = Court.objects.get(name=court_name)
                time_obj = datetime.strptime(time_str, '%H:%M').time()
                
                # Encontrar e excluir a reserva
                deleted = Reservation.objects.filter(
                    court=court, date=date_obj, time_slot=time_obj
                ).delete()[0]
                
                deleted_count += deleted
            
            messages.success(request, f"{deleted_count} reservas foram excluídas com sucesso.")
        except Exception as e:
            messages.error(request, f"Erro ao excluir reservas: {str(e)}")
        
        # Redirecionar de volta para a página de agenda
        return redirect(f"{reverse('admin_schedule')}?date={date_str}")
    
    return redirect('admin_schedule')