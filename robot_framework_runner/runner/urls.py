from django.urls import path
from .views import ReceiveDevicesAPIView,RunRobotTests

urlpatterns = [
    path('run-robot/', RunRobotTests.as_view(), name='run-robot'),
    path('receive-devices/',ReceiveDevicesAPIView.as_view(),name='receive-devices')
]
