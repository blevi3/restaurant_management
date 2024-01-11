from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from ..models import Cart
from ..forms import CreateCouponForm , CouponRedemptionForm
from ..models import Coupons, Menuitem, Cart, CartItem
from django.contrib import messages
from decimal import Decimal


@staff_member_required
def create_coupon(request):
    coupons = Coupons.objects.all()  # Retrieve all coupons

    if request.method == 'POST':
        form = CreateCouponForm(request.POST)

        if form.is_valid():
            coupon_type = form.cleaned_data['coupon_type']
            code = form.cleaned_data['code']
            product = form.cleaned_data['product']
            is_unique = form.cleaned_data['is_unique']

            # Initialize coupon object based on the selected coupon type
            if coupon_type == 'fixed':
                fixed_amount = form.cleaned_data['percentage']
                coupon = Coupons(
                    coupon_type=coupon_type,
                    fixed_amount=fixed_amount,
                    code=code,
                    product=product if coupon_type == 'percentage' else None,
                    is_unique=is_unique
                )
            elif coupon_type == 'percentage':
                percentage = form.cleaned_data['percentage']
                coupon = Coupons(
                    coupon_type=coupon_type,
                    percentage=percentage,
                    code=code,
                    product=product,
                    is_unique=is_unique
                )
            else:
                # Handle any other coupon types if needed
                pass

            coupon.save()
            return redirect('create_coupon')  # Redirect to the coupon list page after creation

    else:
        # Display the form for creating a new coupon
        form = CreateCouponForm()

    return render(request, 'create_coupon.html', {'form': form, 'coupons': coupons})

@staff_member_required
def remove_coupon(request, coupon_id):
    if request.method == 'POST':
        try:
            coupon = Coupons.objects.get(pk=coupon_id)
            coupon.delete()
        except Coupons.DoesNotExist:
            pass 
    return redirect('create_coupon') 

@login_required
def remove_coupon_from_cart(request):
    if request.method == 'POST':
        cart = Cart.objects.get(user=request.user, ordered=False)
        if cart.discount != 0:
            # Get the coupon code and associated discount
            removed_coupon = Coupons.objects.get(id=cart.discount)
            
            # Revert the prices of items that were discounted by the coupon
            cart_items = CartItem.objects.filter(cart=cart)
            if removed_coupon.coupon_type == 'fixed':
                print("fixed")
                # Revert fixed amount coupon
                cart.amount_to_be_paid += removed_coupon.fixed_amount
                cart.reduced_price = 0
                cart.discount = 0
                cart.applied_coupon_type = None
                cart.save()

            elif removed_coupon.coupon_type == 'percentage':
                for cart_item in cart_items:
                    if cart_item.item.id == Menuitem.objects.filter(name = removed_coupon.product).first().id:
                        # Retrieve the original price from the Menuitem model
                        original_price = Menuitem.objects.get(id=cart_item.item.id).price
                        print("original proce",original_price)

                        # Update the CartItem's total_price with the original price
                        cart_item.total_price = original_price+cart_item.get_extras_price()
                        cart_item.final_price = cart_item.total_price*cart_item.quantity+cart_item.get_extras_price()


                        cart_item.save()
                cart.discount = 0
                cart.applied_coupon_type = None
                cart.save()
            cart.save()
            messages.success(request, 'Coupon removed successfully.')
        else:
            messages.warning(request, 'No coupon to remove.')

    return redirect('cart') 


def redeem_coupon(request):
    profile = request.user.profile

    available_coupons = {
        "percentage_coupon_1": {
            "name": "Mort Subite",
            "type": "percentage",
            "percentage": Decimal('10.00'),
            "product": "Mort Subite",
            "fixed_amount": None,
        },
        "fixed_coupon_1": {
            "name": "Összeg",
            "type": "fixed",
            "percentage": None,
            "product": None,
            "fixed_amount": Decimal('500.00'),
        },
        "percentage_coupon_2": {
            "name": "Staropramen",
            "type": "percentage",
            "percentage": Decimal('15.00'),
            "product": "Staropramen",
            "fixed_amount": None,
        },
        "fixed_coupon_2": {
            "name": "Összeg",
            "type": "fixed",
            "percentage": None,
            "product": None,
            "fixed_amount": Decimal('750.00'),
        },
    }


    if request.method == 'POST':
        form = CouponRedemptionForm(request.POST, available_coupons=available_coupons)
        if form.is_valid():
            selected_coupon_key = form.cleaned_data['selected_coupon']
            selected_coupon_data = available_coupons[selected_coupon_key]
            print("selected coupon data: ", selected_coupon_data)

            coupon_price = Decimal('5.00')

            if profile.points >= coupon_price:
                print("have enough points")
                # Generate a random coupon code
                import random
                import string
                code_length = 10
                code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(code_length))

                # Create the coupon object based on the selected coupon type
                if selected_coupon_data['type'] == 'percentage':
                    Coupons.objects.create(
                        coupon_type = "percentage",
                        is_unique = 1,
                        percentage=selected_coupon_data['percentage'],
                        code=code,
                        product=selected_coupon_data['product'],
                        user_id = request.user.id,
                    )
                elif selected_coupon_data['type'] == 'fixed':
                    Coupons.objects.create(
                        is_unique = 1,
                        coupon_type = "fixed",
                        percentage=None,
                        code=code,
                        product=selected_coupon_data['product'],
                        fixed_amount=selected_coupon_data['fixed_amount'],
                        user_id = request.user.id,

                    )

                # Deduct points from the user's profile
                profile.points -= coupon_price
                profile.save()

                messages.success(request, "Coupon redeemed successfully.")
                return redirect('profile')  # Redirect to the user's profile page
            else:
                messages.error(request, "You don't have enough points to redeem this coupon.")
    else:
        form = CouponRedemptionForm(available_coupons=available_coupons)

    return render(request, 'coupon_redeem.html', {'form': form, 'available_coupons': available_coupons})