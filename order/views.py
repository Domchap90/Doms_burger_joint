from django.shortcuts import render

# Create your views here.

def order(request):
    """ Order page view """

    return render(request, 'order/order.html')
