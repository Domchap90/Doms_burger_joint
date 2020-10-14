from django.shortcuts import render, get_object_or_404

from .models import MemberProfile
from .forms import MemberProfileForm
from django.contrib import messages


def members_area(request):
    member_profile = get_object_or_404(MemberProfile, member=request.user)
    form = MemberProfileForm(instance=member_profile)
    if request.method == 'POST':
        form = MemberProfileForm(request.POST, instance=member_profile)
        if form.is_valid():
            form.save()
            messages.success(request, f'Saved information updated for \
                             {member_profile}')

    orders = member_profile.orders.all()

    context = {
        'member': member_profile,
        'memberform': form,
        'order_history': orders,
    }
    return render(request, 'members_area/profile_page.html', context)


def rewards(request):
    context = {}

    return render(request, 'members_area/rewards.html', context)