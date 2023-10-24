from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from django.shortcuts import render, redirect
from ..models import Cart, CartItem, Profile, Reservation, Coupons
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.contrib.auth.models import User
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.core.mail import send_mail
from django.db import connection
import psutil


def dashboard(request):
    total_sales = Cart.objects.filter(is_paid=True).aggregate(total_sales=Sum('amount_to_be_paid'))
    popular_items = CartItem.objects.values('item__name').annotate(total_sold=Sum('quantity')).order_by('-total_sold')[:10]

    inactive_users_count = inactive_users()
    unique_coupons_count = unique_coupons()
    total_reservations, total_tables_booked = reservations_statistics()
    top_customers = top_customers_with_spent()
    chart_image = sales_chart()
    new_users_data = new_users()
    active_users_data = active_users()

    context =  {
        'total_sales': total_sales['total_sales'],
        'popular_items': popular_items,
        'unique_coupons': unique_coupons_count,
        'total_reservations': total_reservations,
        'total_tables_booked': total_tables_booked,
        'top_customers': top_customers,
        'sales_chart_image': chart_image,
        'new_users': new_users_data,
        'active_users': active_users_data,
        'inactive_users': inactive_users_count,
        }

    return render(request, 'dashboard.html', context)


def unique_coupons():
    unique_coupon_codes = CartItem.objects.filter(cart__ordered=True).values('item__category', 'item__name').distinct()
    unique_coupons_count = len(unique_coupon_codes)
    return unique_coupons_count

def reservations_statistics():
    reservations = Reservation.objects.all()
    total_reservations = reservations.count()
    total_tables_booked = len(set(reservation.table for reservation in reservations))
    return total_reservations, total_tables_booked
def top_customers_with_spent():
    user_spent = Cart.objects.filter(is_paid=True).values('user').annotate(total_spent=Sum('amount_to_be_paid'))
    top_customers = Cart.objects.values('user__username').annotate(total_orders=Count('user')).order_by('-total_orders')[:10]
    top_customers_with_spent = []
    for customer in top_customers:
        username = customer['user__username']
        total_orders = customer['total_orders']
        
        # Order the user_spent queryset by user ID and get the first result
        total_spent_result = user_spent.filter(user__username=username).order_by('user').first()
        total_spent = total_spent_result['total_spent'] if total_spent_result else 0

        top_customers_with_spent.append({'username': username, 'total_orders': total_orders, 'total_spent': total_spent})
    return top_customers_with_spent


def sales_chart():
    import random
    from datetime import datetime, timedelta
    today = datetime.now().date()                                                   #sample data
    dates = [today - timedelta(days=i) for i in range(30)]                          #sample data
    total_sales_for_graph = [random.randint(1000, 5000) for _ in range(30)]         #sample data

    #sales_data = list(sales_over_time)
    #dates = [item['date'] for item in sales_data]
    #total_sales_for_graph = [item['total_sales'] for item in sales_data]

    # Combine the data into a list of dictionaries
    plt.figure(figsize=(10, 6))
    plt.plot(dates, total_sales_for_graph, marker='o', linestyle='-', color='b')    #sample data
    #plt.plot(dates, total_sales_for_graph, marker='o', linestyle='-', color='b')

    plt.title('Sales Trends Over Time (Sample Data)')
    plt.xlabel('Date')
    plt.ylabel('Total Sales')
    plt.grid(True)

    # Save the Matplotlib chart to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)

    # Encode the Matplotlib chart as base64
    return base64.b64encode(buffer.read()).decode()

def new_users():
    today = timezone.now()
    one_day_ago = today - timezone.timedelta(days=1)
    one_week_ago = today - timezone.timedelta(weeks=1)
    one_month_ago = today - timezone.timedelta(weeks=4)
    six_months_ago = today - timezone.timedelta(weeks=26)
    one_year_ago = today - timezone.timedelta(weeks=52)

    new_users_day = User.objects.filter(date_joined__gte=one_day_ago).count()
    new_users_week = User.objects.filter(date_joined__gte=one_week_ago).count()
    new_users_month = User.objects.filter(date_joined__gte=one_month_ago).count()
    new_users_six_months = User.objects.filter(date_joined__gte=six_months_ago).count()
    new_users_year = User.objects.filter(date_joined__gte=one_year_ago).count()
    new_users_data = {
        'day': new_users_day,
        'week': new_users_week,
        'month': new_users_month,
        'six_month': new_users_six_months,
        'year': new_users_year,
    }
    return new_users_data


def active_users():
    three_months_ago = timezone.now() - timezone.timedelta(weeks=12)
    active_users = User.objects.filter(last_login__gte=three_months_ago).count()
    return active_users

def inactive_users():
    three_months_ago = timezone.now() - timezone.timedelta(minutes=12)
    inactive_users = User.objects.filter(last_login__lt=three_months_ago).count()
    return inactive_users


@require_POST
def send_coupons_to_inactive_users(request):
    # Logic to send emails and assign coupons
    inactive_users = User.objects.filter(last_login__lt=timezone.now() - timezone.timedelta(minutes=3))
    for user in inactive_users:
        print(user.email)
        # Send email to the user
        send_mail(
            'We miss you!',
            'Its been too long since we last saw you. We have sent you a 500Ft coupon so maybe you stop by next time ;).',
            '',
            [user.email],
            fail_silently=False,
        )
        
        import random
        import string
        code_length = 10
        code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(code_length))
        coupon = Coupons(coupon_type='fixed', fixed_amount=500, code = code, is_unique=True, user_id=user.id, product=None)
        coupon.save()

    return JsonResponse({'message': 'Coupons sent and assigned to inactive users.'})



def server_status(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_result = cursor.fetchone()
            db_status = 1 if db_result and db_result[0] == 1 else 0
    except Exception as e:
        db_status = 0

    try:
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        if cpu_usage < 80 and memory_usage < 80:
            resource_status = 1
        else:
            resource_status = 0
    except Exception as e:
        resource_status = 0

    combined_status = 1 if db_status == 1 and resource_status == 1 else 0

    return JsonResponse({
        'db_status': db_status,
        'resource_status': resource_status,
        'combined_status': combined_status
    })