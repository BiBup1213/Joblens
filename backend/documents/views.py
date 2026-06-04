from rest_framework import viewsets

from .models import ProfileDocument
from .serializers import ProfileDocumentSerializer


class ProfileDocumentViewSet(viewsets.ModelViewSet):
    queryset = ProfileDocument.objects.all()
    serializer_class = ProfileDocumentSerializer
