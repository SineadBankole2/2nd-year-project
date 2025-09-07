from .models import Loyalty

def loyalty_points(request):
    if request.user.is_authenticated:
        try:
            loyalty = Loyalty.objects.get(user=request.user)
        except Loyalty.DoesNotExist:
            loyalty = None
    else:
        loyalty = None

    return {'loyalty': loyalty}
