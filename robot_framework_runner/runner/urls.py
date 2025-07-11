from django.urls import path
from .views import RunRobotTests

urlpatterns = [
    path('run-robot/', RunRobotTests.as_view(), name='run-robot'),

]
