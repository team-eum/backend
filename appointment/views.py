from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from appointment.models import Appointment
from appointment.openai import CustomOpenAI
from appointment.serializers import AppointmentSerializer


class AppointmentView(APIView):
    """
    Appointment list를 가져올 때 사용하는 API
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        try:
            appointments = Appointment.objects.filter(mentee=request.user)
            serializer = AppointmentSerializer(instance=appointments, many=True)
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                data={"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TextSummaryView(APIView):
    """
    텍스트를 요약해주는 API
    """
    permission_classes = [AllowAny]
    openai = CustomOpenAI()

    def post(self, request, *args, **kwargs):
        try:
            text: str = request.data.get("text")
            summary = self.openai.get_summary(text)
            if summary:
                return Response(
                    data={"detail": summary.choices[0].message.content},
                    status=status.HTTP_200_OK
                )
            else:
                raise Exception("OpenAI Error!")
        except Exception as e:
            return Response(
                data={"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
