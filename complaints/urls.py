from django.urls import path

from .views import (
    api_root,
    ComplaintCreateAPIView,
    ComplaintCreateAudioAPIView,
    ComplaintListAPIView,
    ComplaintDetailAPIView,
    ComplaintStatusAPIView,
    VerifyEmailView,
    register_view,
)

urlpatterns = [
    # API index
    path("", api_root, name="api-root"),
    # Auth/API endpoints (mounted under /api/ in project urls)
    path("register/", register_view, name="register"),
    path("verify-email/<uidb64>/<token>/", VerifyEmailView.as_view(), name="verify_email"),
    path("complaints/create/", ComplaintCreateAPIView.as_view(), name="complaint_create"),
    path("complaints/create-audio/", ComplaintCreateAudioAPIView.as_view(), name="complaint_create_audio"),
    path("complaints/", ComplaintListAPIView.as_view(), name="complaint_list"),
    path("complaints/<int:pk>/", ComplaintDetailAPIView.as_view(), name="complaint_detail"),
    path("complaints/<int:pk>/status/", ComplaintStatusAPIView.as_view(), name="complaint_status"),
]