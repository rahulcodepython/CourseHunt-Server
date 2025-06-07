from rest_framework.viewsets import generics
from authentication.models import Instructor
from instructor.serializers import InstructorListSerializer, InstructorDetailSerializer
from rest_framework.permissions import AllowAny


class InstructorDetailView(generics.RetrieveAPIView):
    """
    View to retrieve instructor details.
    """
    permission_classes = [AllowAny]
    queryset = Instructor.objects.all()
    serializer_class = InstructorDetailSerializer
    lookup_field = 'user'


class InstructorListView(generics.ListAPIView):
    """
    View to list all instructors.
    """
    permission_classes = [AllowAny]
    queryset = Instructor.objects.all()
    serializer_class = InstructorListSerializer


class JoinInstructorView(generics.CreateAPIView):
    """
    View to create a new instructor.
    """
    permission_classes = [AllowAny]
    queryset = Instructor.objects.all()
    serializer_class = InstructorDetailSerializer
