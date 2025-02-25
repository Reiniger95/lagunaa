from django.urls import path
from .views import register_view, delete_caixa, select_bbq_view, delete_bbq_reservation, select_date_bbq_view, select_time_slot_bbq_view, delete_reservation_view, agenda_view, login_view, logout_view, home_view, select_date_view, select_time_slot_view, select_court_view, admin_schedule_view
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('', home_view, name='home'),
    path('select_date/', select_date_view, name='select_date'),
    path('select_date_bbq/', select_date_bbq_view, name='select_date_bbq'),
    path('select_time_slot/', select_time_slot_view, name='select_time_slot'),
    path('select_time_slot_bbq/', select_time_slot_bbq_view, name='select_time_slot_bbq'),
    path('select_bbq/', select_bbq_view, name='select_bbq'),
    path('select_court/', select_court_view, name='select_court'),
    path('admin_schedule/', admin_schedule_view, name='admin_schedule'),
    path('reservas/', agenda_view, name='agenda'),
    path('delete_caixa/<int:caixa_id>/', delete_caixa, name='delete_caixa'),
    path('reservas/delete/<int:reservation_id>/', delete_reservation_view, name='delete_reservation'),
    path('delete_bbq_reservation/<int:reservation_id>/', delete_bbq_reservation, name='delete_bbq_reservation'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
]