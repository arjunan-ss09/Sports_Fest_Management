from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout
from management.models import ParticipantProfile

class BannedUserMiddleware:
    """
    Middleware that logs out and redirects banned users.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only check if user is authenticated and if we're not already on the logout or home page
        if request.user.is_authenticated:
            try:
                profile = request.user.participantprofile
                if profile.is_banned:
                    logout(request)
                    messages.error(request, "You have been banned from participating. Please contact the organizers.")
                    return redirect('home')
            except ParticipantProfile.DoesNotExist:
                # If the user doesn't have a participant profile, no need to check ban status
                pass

        response = self.get_response(request)
        return response
