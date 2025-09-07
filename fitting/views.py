from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import SizeProfile
from .forms import SizeProfileForm

@login_required
def profile_view(request):
    profile, created = SizeProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = SizeProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('fitting:profile')
    else:
        form = SizeProfileForm(instance=profile)

    return render(request, 'fitting/profile.html', {
        'form': form,
        'user': request.user,
        'profile': profile,
    })
