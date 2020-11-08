from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.shortcuts import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import MemberProfile
from checkout.models import Order
from .forms import MemberProfileForm
from django.contrib import messages


def members_area(request):
    """ Renders profile page and all authenticated member's associated
    details """

    member_profile = get_object_or_404(MemberProfile, member=request.user)
    form = MemberProfileForm(instance=member_profile)

    if request.method == 'POST':
        form = MemberProfileForm(request.POST, instance=member_profile)
        if form.is_valid():
            form.save()
            messages.success(request, f'Saved information updated for \
                             {member_profile}')

    orders = member_profile.orders.all().order_by('-date')

    pagenum = request.GET.get('pagenum', 1)

    orders_list = list(orders)
    orders_paginated = Paginator(orders_list, 5)
    try:
        orders_page_objects = orders_paginated.page(pagenum)
    except PageNotAnInteger:
        orders_page_objects = orders_paginated.page(1)
    except EmptyPage:
        orders_page_objects = orders_paginated.page(orders_paginated.num_pages)

    context = {
        'member': member_profile,
        'memberform': form,
        'order_history': orders_page_objects,
    }
    return render(request, 'members_area/profile_page.html', context)


def rewards(request):
    """ Renders rewards page - access to login / signup """

    return render(request, 'members_area/rewards.html')


def repeat_order(request):
    """ Clears any current order items and replaces them ALL with the order
    selected to be repeated. """

    order = {}
    order_id = request.POST.get('order_id')
    repeat_order = get_object_or_404(Order, order_number=order_id)

    # Adds each food or combo item back to order dict in same structure as
    # food_order app
    for item in repeat_order.lineitems.all():
        if not item.combo_id:
            item_id = item.food_item.id
            quantity = item.quantity
            order[item_id] = quantity
    for item in repeat_order.lineitems.all():
        if item.combo_id:
            combo_id = item.combo_id
            combo_quantity = item.combo_quantity
            order[combo_id] = [item.combo_item.id, combo_quantity, {}]
            for combo_item in item.combocontents.all():
                order[combo_id][2][
                    combo_item.food_item.id] = combo_item.quantity

    # Sets session variable equal to this order, overwriting any previous items
    # inside it
    request.session['food_order'] = order

    return HttpResponseRedirect(reverse('checkout'))
