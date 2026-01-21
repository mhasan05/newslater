from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import EmailSubscriptionForm
from .models import Email


def index(request):
    form = EmailSubscriptionForm()
    
    if request.method == 'POST':
        form = EmailSubscriptionForm(request.POST)
        if form.is_valid():
            try:
                # Create the email record but don't save yet
                email_obj = form.save(commit=False)
                # Since we've verified the email via SMTP, mark it as verified
                email_obj.is_verified = True
                email_obj.save()
                
                # Since the email has been validated via SMTP, we can confirm successful subscription
                
                messages.success(request, 'Thank you for subscribing to our newsletter! Your email has been successfully registered.')
                return HttpResponseRedirect(reverse('index'))
            except Exception as e:
                messages.error(request, f'There was an error saving your email: {str(e)}')
        else:
            # Form is not valid, check if it's because of duplicate email
            if 'email' in form.errors:
                error_msg = form.errors['email'][0]
                if 'already registered' in error_msg:
                    messages.error(request, error_msg)
                else:
                    messages.error(request, 'Please enter a valid email address.')
    
    context = {
        'form': form,
        'subscribers_count': Email.objects.filter(is_verified=True).count(),
    }
    return render(request, 'newsletter/index.html', context)

