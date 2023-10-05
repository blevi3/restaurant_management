
from ..forms import ReservationForm, DateSelectionForm
from ..models import  Reservation, Table
from .views import staff_member_required

from datetime import datetime, time, timedelta
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import JsonResponse


@staff_member_required
def all_reservations(request):
    reservations = Reservation.objects.filter(end_time__gt=timezone.now()).order_by('start_time')
    past_reservations = Reservation.objects.exclude(id__in=reservations.values_list('id', flat=True))

    return render(request, 'all_reservations.html', {'reservations': reservations, "past_reservations": past_reservations})

@staff_member_required
def mark_reservation_taken(request, reservation_id):
    # Get the reservation object
    reservation = get_object_or_404(Reservation, id=reservation_id)

    # Mark the reservation as taken (set the 'taken' attribute to True)
    reservation.taken = True
    reservation.save()

    # You can return a JSON response to indicate success or any other data if needed
    return JsonResponse({'message': 'Reservation marked as taken successfully'})
@login_required
def my_reservations(request):
    now = timezone.now()
    reservations = Reservation.objects.filter(user=request.user)
    current_reservations = sorted(reservations.filter(start_time__gte=now), key=lambda r: r.start_time)
    past_reservations = sorted(reservations.filter(end_time__lt=now), key=lambda r: r.start_time, reverse=True)
    context = {
        'reservations': reservations,
        'now': now,
        'current_reservations': current_reservations,
        'past_reservations': past_reservations
    }
    return render(request, 'my_reservations.html', context)


@login_required
def available_tables(request):
    if request.method == 'POST':
        form = DateSelectionForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            form = DateSelectionForm(initial={'date': date})
            max_future_days = 60
            if date > date.today() + timedelta(days=max_future_days):
                raise ValidationError('Selected date is too far in the future')
        else:
            date = None
    else:
        form = DateSelectionForm()
        date = None

    if date:
        tables = Table.objects.all()


        return render(request, 'reservation.html', {'tables': tables, 'date': date, 'form': form})
    else:
        return render(request, 'reservation.html', {'form': form})

'''
def get_available_times(date1, table):
    
    reserved_times = Reservation.objects.filter(start_time__date=date1, table=table).order_by('start_time')
    reserved_times_list = list(reserved_times.values_list('start_time', 'end_time'))

    # Create a list of all the possible time slots
    time_slots = []
    
    start_time = datetime.combine(date1, time(9, 0))  # Start time for reservations
    end_time = datetime.combine(date1, time(23, 0))  # End time for reservations
    while start_time < end_time:
        time_slots.append((start_time.time(), (start_time + timedelta(minutes=30)).time()))
        start_time += timedelta(minutes=30)

    # Remove any time slots that are already reserved
    available_times = []
    for time_slot in time_slots:
        if time_slot not in reserved_times_list:
            available_times.append(time_slot)

    return available_times
'''
@login_required
def reservation_table(request, table_id, date1):
    table = get_object_or_404(Table, id=table_id)
    reserved_times = Reservation.objects.all().filter(table_id = table_id).filter(start_time__contains=date1)
    reserved_times_values = []
    for i in range(len(reserved_times)):
        reserved_times_values.append({'start_time': reserved_times[i].start_time.strftime("%Y-%m-%d %H:%M"), 'end_time': reserved_times[i].end_time.strftime("%Y-%m-%d %H:%M")})
    #date1 = request.POST.get('date')
    #available_times = get_available_times(date1, table)
    #print(available_times)
    if date1 == datetime.now().strftime("%Y-%m-%d"):  # Check if date1 is today
        now = datetime.now()
        start_of_day = datetime(now.year, now.month, now.day, 8, 0)  # 08:00 AM

        past_times_values2 = []
        time_increment = timedelta(minutes=15)
        current_time = start_of_day
        while current_time < now:
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M")
            past_times_values2.append({
                'start_time': formatted_time,
                'end_time': (current_time + time_increment).strftime("%Y-%m-%d %H:%M")
            })
            current_time += time_increment

        reserved_times_values2 = past_times_values2 + reserved_times_values  # Combine past and reserved times
    else:
        reserved_times_values2 = reserved_times_values

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.table = table
            start_time_str = request.POST.get('starttime')
            end_time_str = request.POST.get('endtime')
            party_size = request.POST.get('party_size')
            try:
            
            # Validate the party size
                if int(party_size) > table.max_capacity:
                    raise ValidationError(f"Party size cannot exceed {table.max_capacity}.")
                starter = date1+" "+start_time_str
                ender = date1+" "+end_time_str
                start_time = datetime.strptime(starter, '%Y-%m-%d %H:%M:%S')
                end_time = datetime.strptime(ender, '%Y-%m-%d %H:%M:%S')
                reservation.start_time = start_time
                reservation.end_time = end_time
                reservation.save()
                messages.success(request, 'Reservation successful!')
                return redirect('home')
            
            except ValidationError as e:
            # Display the error message on the screen
                error_message = str(e)
                cleaned_message = error_message[2:-2]
                return render(request, 'reservation_table.html', {'table': table, 'error_message': cleaned_message,  'form': form, 'date1': date1, 'reserved_time': reserved_times_values, "past_times": reserved_times_values2})
    else:
        form = ReservationForm()
        

    return render(request, 'reservation_table.html', {'table': table,  'form': form, 'date1': date1, 'reserved_time': reserved_times_values, "past_times": reserved_times_values2})
