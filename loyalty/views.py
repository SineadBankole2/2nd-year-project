from django.shortcuts import render
from .models import Loyalty
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt  
from django.http import HttpResponse

@csrf_exempt  
@login_required
def view_loyalty(request):
    try:
        
        loyalty = Loyalty.objects.get(user=request.user)
    except Loyalty.DoesNotExist:
        
        loyalty = Loyalty.objects.create(user=request.user)
        print(f"New loyalty record created for user {request.user.username}")

    return render(request, 'loyalty/view_loyalty.html', {'loyalty': loyalty})


def create_loyalty_for_user(user):
   
    if not Loyalty.objects.filter(user=user).exists():
       
        Loyalty.objects.create(user=user)
        print(f"Loyalty record created for user {user.username}")
    else:
        print(f"Loyalty record already exists for user {user.username}")
