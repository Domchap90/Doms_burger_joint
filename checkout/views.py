from django.shortcuts import render
from .forms import OrderForm

# Create your views here.


def checkout(request):
    form = OrderForm()

    context = {
        'form': form,
    }

    return render(request, 'checkout/checkout.html', context)
