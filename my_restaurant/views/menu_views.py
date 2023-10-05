from django.shortcuts import render, get_object_or_404
from ..models import Menuitem, CartItem
from django.contrib.auth.decorators import login_required

def drinks(request):
    drinks = Menuitem.objects.all().filter(type = 0)  
    categories = []
    for categorie in drinks:
        categories.append(categorie.category)
    cat = list(set(categories))
    

    foods = Menuitem.objects.all().filter(type = 1)
    categories2 = []
    for food in foods:
        categories2.append(food.category)
    cat2 = list(set(categories2))
    
    return render(request, 'drinks.html', {'drinks': drinks, 'categories':cat, 'foods': foods, 'categories2': cat2})

def menu(request):
    foods = Menuitem.objects.all().filter(type = 1)
    categories = []
    for food in foods:
        categories.append(food.category)
    cat = list(set(categories))

    return render(request, 'foods.html', {'foods': foods, 'categories': cat})

@login_required
def items_list(request):
    
    item_list = Menuitem.objects.all()
    categories = item_list.values_list('category', flat=True).distinct()
    if request.method == 'POST':
        

        if 'edit' in request.POST:
            item = get_object_or_404(Menuitem, pk=request.POST['editItemID'])
            item.name = request.POST.get('edit')
            item.price = request.POST.get('price')
    
            item.save()
        elif 'remove' in request.POST:
            item = get_object_or_404(Menuitem, pk=request.POST['remove'])
            item.delete()
        elif 'add' in request.POST:
            if request.POST.get('type') == "Food":
                newtype = 1
            else:
                newtype = 0
            Menuitem.objects.create(
                name=request.POST.get('add'),
                price=request.POST.get('price'),
                type = newtype,
                category = request.POST.get('category')
            )
            
    return render(request, 'data.html', {'item_list': item_list, 'categories': categories})



def get_recommendations(cart_items, num_recommendations=3):
    from collections import Counter
    from itertools import groupby

    order_history = CartItem.objects.all().values_list('cart_id', 'item_id')

    product_pairs = Counter()
    for cart_id, items in groupby(order_history, key=lambda x: x[0]):
        ordered_items = set(items)
        for item1 in ordered_items:
            for item2 in ordered_items:
                if item1 != item2:
                    product_pairs[(item1[1], item2[1])] += 1

    cart_products = cart_items
    recommendations = []
    for product_pair, frequency in product_pairs.items():
        if product_pair[0] in cart_products and product_pair[1] not in cart_products:
            recommendations.append((product_pair[1], frequency))
        elif product_pair[1] in cart_products and product_pair[0] not in cart_products:
            recommendations.append((product_pair[0], frequency))
    recommendations.sort(key=lambda x: x[1], reverse=True)
    unique_recommendations = list(set(recommendations))
    unique_recommendations.sort(key=lambda x: x[1], reverse=True)
    unique_product_ids = [product_id for product_id, _ in unique_recommendations]
    recom = list(set(unique_product_ids))[:num_recommendations]
    return recom

