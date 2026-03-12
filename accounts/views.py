from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ProfileForm
from .models import Profile


@login_required
def profile(request):
    profile, _created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            request.user.first_name = form.cleaned_data.get('first_name', '')
            request.user.last_name = form.cleaned_data.get('last_name', '')
            request.user.save()

            profile.phone_number = form.cleaned_data.get('phone_number', '')
            profile.save()

            messages.success(request, 'Your profile has been updated.')
            return redirect('profile')
    else:
        form = ProfileForm(
            initial={
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'phone_number': profile.phone_number,
            }
        )

    return render(request, 'accounts/profile.html', {'form': form})


