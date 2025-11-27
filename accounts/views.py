from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
import urllib.parse
import requests
from django.utils import timezone
from datetime import timedelta
from .models import UserToken
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


class GoogleAuthInit(APIView):
    def get(self, request):
        redirect_uri = "http://localhost:8000/accounts/google/callback/"

        oauth_url = (
            "https://accounts.google.com/o/oauth2/v2/auth?"
            "response_type=code&"
            f"client_id={settings.GOOGLE_CLIENT_ID}&"
            f"redirect_uri={urllib.parse.quote(redirect_uri)}&"
            "scope=openid%20email%20profile%20"
            "https://www.googleapis.com/auth/userinfo.email%20"
            "https://www.googleapis.com/auth/userinfo.profile%20"
            "https://www.googleapis.com/auth/gmail.readonly%20"
            "https://www.googleapis.com/auth/gmail.compose%20"
            "https://www.googleapis.com/auth/gmail.modify&"
            "access_type=offline&"
            "prompt=consent"
        )

        return Response({"login_url": oauth_url})


@method_decorator(csrf_exempt, name="dispatch")
class GoogleAuthCallback(APIView):
    def get(self, request):
        print("CALLBACK HIT")
        code = request.GET.get("code")
        redirect_uri = "http://localhost:8000/accounts/google/callback/"

        # Step 1: Exchange code for access token
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }

        r = requests.post(token_url, data=data)
        tokens = r.json()

        access_token = tokens["access_token"]

        # Step 2: Fetch user profile
        userinfo_url = "https://openidconnect.googleapis.com/v1/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        google_userinfo = requests.get(userinfo_url, headers=headers).json()

        # DEBUG CHECK
        print("GOOGLE USER INFO:", google_userinfo)

        if "email" not in google_userinfo:
            return Response({"error": "Email not returned by Google", "data": google_userinfo})

        email = google_userinfo["email"]

        # Step 3: Create or get Django user
        user, created = User.objects.get_or_create(
            username=email,
            defaults={"email": email}
        )

        # Step 4: Log the user in
        login(request, user)
        request.session.save()

        # Step 5: Save tokens
        UserToken.objects.update_or_create(
            user=user,
            provider="gmail",
            defaults={
                "access_token": tokens["access_token"],
                "refresh_token": tokens.get("refresh_token"),
                "token_expiry": timezone.now() + timedelta(seconds=tokens["expires_in"])
            }
        )

        response = redirect("http://localhost:3000/dashboard")

        response.set_cookie(
            key=settings.SESSION_COOKIE_NAME,
            value=request.session.session_key,
            httponly=True,
            secure=True,
            samesite="None",
            path="/"
        )

        print("SESSION KEY:", request.session.session_key)

        for k, v in response.items():
            print("RESPONSE HEADER:", k, "=", v)

        return response


class WhoAmI(APIView):
    def get(self, request):
        return Response({
            "user": str(request.user),
            "is_authenticated": request.user.is_authenticated
        })
