from django.views.generic import TemplateView
from ..models import Menuitem, Cart, CartItem, Profile , Coupons
from .invoice_views import generate_pdf_receipt, send_email_with_pdf

from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt 
import stripe



def get_user_cart_items(user):
    # Retrieve the cart for the user
    cart = Cart.objects.filter(user_id=user.id, ordered=0, is_delivered=0, is_paid=0, is_ready=0).first()

    if cart:
        cart_items = CartItem.objects.filter(cart_id=cart.id)
        line_items2 = []

        for cart_item in cart_items:
            menu_item = Menuitem.objects.get(id=cart_item.item_id)
            line_item2=[int(cart_item.total_price), menu_item.name, cart_item.quantity]
            line_items2.append(line_item2)

        return line_items2, cart
    else:
        return []

@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_TEST_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)
    
@csrf_exempt
def create_checkout_session(request):
    if request.method == 'GET':
        domain_url = 'http://localhost:8000/'
        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
        try:
            user_items, cart= get_user_cart_items(request.user)
            line_items = []
            for item in user_items:
                line_item = {
                    'price_data': {
                        'currency': 'huf',
                        'unit_amount': item[0]*100,  
                        'product_data': {
                            'name': item[1],    
                        },
                    },
                    'quantity': item[2],  
                }
                line_items.append(line_item)

            discount = 0
            if cart.applied_coupon_type == 'fixed':
                discount = Coupons.objects.filter(id=cart.discount).first().fixed_amount
                print("discount: ",discount)
            
                coupon = stripe.Coupon.create(
                        percent_off=None,
                        amount_off=int(discount)*100,  # The discount value in cents (-500ft)
                        currency="huf",
                        duration="once",  # Adjust duration as needed
                    )


                checkout_session = stripe.checkout.Session.create(
                    client_reference_id=request.user.id if request.user.is_authenticated else None,
                    success_url=domain_url + 'cart',
                    cancel_url=domain_url + 'cancelled/',
                    payment_method_types=['card'],
                    mode='payment',
                    
                    line_items=line_items,
                    discounts=[{
                        'coupon': coupon.id,
                    }],
                )

            else:
                checkout_session = stripe.checkout.Session.create(
                    client_reference_id=request.user.id if request.user.is_authenticated else None,
                    success_url=domain_url + 'cart',
                    cancel_url=domain_url + 'cancelled/',
                    payment_method_types=['card'],
                    mode='payment',
                    line_items=line_items,
                )


            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})

class SuccessView(TemplateView):
    template_name = 'payment_success.html'


class CancelledView(TemplateView):
    template_name = 'payment_cancelled.html'


@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['client_reference_id']
        print("user id: ",user_id)
        user = User.objects.get(id=user_id)
        cart = Cart.objects.filter(user=user, ordered=0, is_delivered=0, is_paid=0, is_ready=0).first()

        if cart:
            if cart.discount !=0:
                used_coupon = Coupons.objects.filter(id=cart.discount).first()
                if used_coupon.is_unique == 1:
                    used_coupon.delete()
            cart.ordered = 1
            cart.is_paid = 1
            cart.discount = 0
            cart.applied_coupon_type = None
            cart.reduced_price = 0
            cart.save()
            print("cart: ",cart)
            
            
        print("Payment was successful. Cart updated.")
        user_items = CartItem.objects.filter(cart_id=cart.id)
        subtotal = 0
        for item in user_items:
            total_item_price = item.item.price * item.quantity
            subtotal += total_item_price
        profile = Profile.objects.get(id=user_id)
        profile.points += subtotal/100
        print("user email: ",user.email)
        profile.save()
        pdf_response = generate_pdf_receipt(cart.id, user_items, user, session['payment_intent'])

    
        try:
            send_email_with_pdf(cart.id, pdf_response, user.email)
            print("PDF receipt sent via email.")
        except Exception as e:
            print("Error sending PDF receipt via email: ", str(e))


    return HttpResponse(status=200)