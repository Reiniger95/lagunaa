from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, LoginForm, DateForm, TimeSlotForm, ReservationForm
from .models import Court, CustomUser, Reservation, BBQ, BBQReservation, Modalidade, Caixa
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



@login_required(login_url='/login/')
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
    date = request.session.get('date')
    available_times = []
    total_courts = Court.objects.count()
    
    for hour in range(8, 23):
        start_time = time(hour, 0)
        reservations = Reservation.objects.filter(date=date, time_slot=start_time).count()
        if reservations >= total_courts:
            available_times.append((start_time.strftime('%H:%M'), False))  # False indicates not available
        else:
            available_times.append((start_time.strftime('%H:%M'), True))  # True indicates available

    if request.method == 'POST':
        form = TimeSlotForm(request.POST)
        if form.is_valid():
            request.session['time_slot'] = form.cleaned_data['time_slot']
            return redirect('select_court')
    else:
        form = TimeSlotForm()

    return render(request, 'select_time_slot.html', {'form': form, 'available_times': available_times})
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
        "19:00", "20:00", "21:00", "22:00"
    ]

    # Obter o dia da semana (0 = segunda-feira, 6 = domingo)
    day_of_week = date.weekday()

    if day_of_week == 5:  # Sábado
        valid_times = ["09:00", "10:00", "11:00", "12:00", "13:00", "16:00", "17:00", "18:00", "19:00", "20:00"]
    elif day_of_week == 6:  # Domingo
        valid_times = ["09:00", "10:00", "11:00", "12:00", "13:00"]
    else:  # Segunda a Sexta
        valid_times = [time for time in all_times if time >= "09:00" and time <= "22:00"]

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
    available_courts = Court.objects.exclude(
        reservation__date=date,
        reservation__time_slot=time_slot
    )
    if request.method == 'POST':
        court_id = request.POST.get('court_id')
        court = Court.objects.get(id=court_id)
        Reservation.objects.create(
            user=request.user,
            court=court,
            date=date,
            time_slot=time_slot
        )
        return redirect('home')
    return render(request, 'select_court.html', {'courts': available_courts})

@login_required
def agenda_view(request):
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    
    court_reservations = Reservation.objects.filter(date__gte=yesterday, user=request.user).order_by('date', 'time_slot')
    bbq_reservations = BBQReservation.objects.filter(date__gte=yesterday, user=request.user).order_by('date', 'time_slot')
    
    for reservation in court_reservations:
        reservation.can_delete = (reservation.date - timezone.now().date()).days > 1
    
    for reservation in bbq_reservations:
        reservation.can_delete = (reservation.date - timezone.now().date()).days > 1
    
    return render(request, 'agenda.html', {
        'court_reservations': court_reservations,
        'bbq_reservations': bbq_reservations
    })
@login_required
def delete_reservation_view(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    if (reservation.date - timezone.now().date()).days > 1:
        reservation.delete()
    return redirect('agenda')

@login_required
def delete_bbq_reservation(request, reservation_id):
    reservation = get_object_or_404(BBQReservation, id=reservation_id, user=request.user)
    if (reservation.date - timezone.now().date()).days > 1:
        reservation.delete()
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
        'error_message': error_message
    })


@staff_member_required
def delete_caixa(request, caixa_id):
    caixa = get_object_or_404(Caixa, id=caixa_id)
    caixa.delete()
    return redirect(f"{reverse('admin_schedule')}?tab=caixa")