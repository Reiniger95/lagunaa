from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, LoginForm, DateForm, TimeSlotForm, ReservationForm
from .models import Court, CustomUser, Reservation
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
    reservations = Reservation.objects.filter(date__gte=yesterday, user=request.user).order_by('date', 'time_slot')
    for reservation in reservations:
        reservation.can_delete = (reservation.date - timezone.now().date()).days > 1
    return render(request, 'agenda.html', {'reservations': reservations})

@login_required
def delete_reservation_view(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    if (reservation.date - timezone.now().date()).days > 1:
        reservation.delete()
    return redirect('agenda')

@staff_member_required
def admin_schedule_view(request):
    date_str = request.GET.get('date', datetime.today().strftime('%Y-%m-%d'))
    error_message = None
    try:
        date_chosen = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        # Se a string enviada não estiver em formato '%Y-%m-%d', usa hoje
        date_chosen = datetime.today().date()
    # Carrega reservas do dia
    reservations_for_day = Reservation.objects.filter(date=date_chosen).order_by('time_slot')
    courts = Court.objects.all()
    hours = range(8, 23)

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

    return render(request, 'admin_schedule.html', {
        'date': date_chosen,
        'schedule_rows': schedule_rows,
        'courts': courts,
        'all_reservations': all_reservations,
        'error_message': error_message
    })