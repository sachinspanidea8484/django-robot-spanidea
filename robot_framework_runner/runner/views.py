from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import subprocess
import os
from robot_framework_runner.settings import ROBOT_FRAMEWORK_PATH
from .utils import  write_devices_to_json


class RunRobotTests(APIView):
    def post(self, request):
        try:
            # 1. Parse the incoming payload
            data = request.data
            print("THis is data ")

            devices = data["device"]
            test_case_id= data["test_case"]["test_case_id"]
            write_devices_to_json(devices, ROBOT_FRAMEWORK_PATH)
            tests_path = os.path.abspath(os.path.join(ROBOT_FRAMEWORK_PATH, "tests"))

            result = subprocess.run(['robot', '--include', test_case_id, tests_path], capture_output=True, text=True)

            return Response({
                'status': 'success',
                'stdout': result.stdout,
                'stderr': result.stderr
            })

        except Exception as e:
            return Response(
                {'status': 'error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ReceiveDevicesAPIView(APIView):
    def post(self, request):
        devices = request.data.get('devices', [])
        print("Received devices:", devices)
        # Here, you could save it to DB or process it
        print("hello from Recieving end ")
        return Response({"message": "Devices received", "count": len(devices)}, status=status.HTTP_200_OK)
