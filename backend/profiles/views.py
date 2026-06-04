from rest_framework import viewsets

from .models import ProfileSkill, UserProfile
from .serializers import ProfileSkillSerializer, UserProfileSerializer


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.prefetch_related("skills").all()
    serializer_class = UserProfileSerializer


class ProfileSkillViewSet(viewsets.ModelViewSet):
    queryset = ProfileSkill.objects.select_related("profile").all()
    serializer_class = ProfileSkillSerializer
