from django.shortcuts import render


# Create your views here.
def members_area(request):
    context = {

    }
    return render(request, 'members_area/profile_page.html', context)
