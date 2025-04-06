import django.contrib.auth.decorators
from django.shortcuts import render
@django.contrib.auth.decorators.login_required
def user_notifications(request):
    notifications = request.user.notifications.order_by('-created_at')
    return render(request, 'notifications/user_notifications.html', {'notifications': notifications})