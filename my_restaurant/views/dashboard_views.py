from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from django.shortcuts import render, redirect
from ..models import Cart, CartItem, Profile, Reservation
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def dashboard(request):
    total_sales = Cart.objects.filter(is_paid=True).aggregate(total_sales=Sum('amount_to_be_paid'))

    popular_items = CartItem.objects.values('item__name').annotate(total_sold=Sum('quantity')).order_by('-total_sold')[:10]

    unique_coupon_codes = CartItem.objects.filter(cart__ordered=True).values('item__category', 'item__name').distinct()
    unique_coupons_count = len(unique_coupon_codes)
    print(unique_coupons_count)


    customer_profiles = Profile.objects.all()

    reservations = Reservation.objects.all()
    total_reservations = reservations.count()
    total_tables_booked = len(set(reservation.table for reservation in reservations))
    sales_over_time = Cart.objects.filter(ordered=True).annotate(date=TruncDate('order_time')).values('date').annotate(total_sales=Sum('amount_to_be_paid')).order_by('date')

    
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
    chart_image = base64.b64encode(buffer.read()).decode()


    top_customers = Cart.objects.values('user__username').annotate(total_orders=Count('user')).order_by('-total_orders')[:10]

    context =  {
        'total_sales': total_sales['total_sales'],
        'popular_items': popular_items,
        'unique_coupons': unique_coupons_count,
        'customer_profiles': customer_profiles,
        'total_reservations': total_reservations,
        'total_tables_booked': total_tables_booked,
        #'sales_over_time': sales_over_time,
        'top_customers': top_customers,
        'sales_chart_image': chart_image,



        }

    return render(request, 'dashboard.html', context)