from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import subprocess
import os
import json
import logging
import threading
import requests
from datetime import datetime
from robot_framework_runner.settings import ROBOT_FRAMEWORK_PATH
from .utils import write_devices_to_json

logger = logging.getLogger(__name__)

# OpenWISP server configuration
OPENWISP_SERVER_URL = "http://0.0.0.0:8000"  # Update with your OpenWISP server
OPENWISP_API_ENDPOINT = "/api/v1/test-management/test-case-execution/result/"

class RunRobotTests(APIView):
    def post(self, request):
        try:
            # 1. Log the incoming request for debugging
            print("="*80)
            print("Request received from OpenWISP")
            print(f"Request data: {json.dumps(request.data, indent=2)}")
            print("="*80)
            
            # 2. Extract data with proper error handling
            data = request.data
            
            # Check if data is empty
            if not data:
                return Response({
                    'status': 'error',
                    'message': 'Empty request body'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Extract required fields
            devices = data.get("devices", [])
            test_suites = data.get("test_suites", {})
            execution_metadata = data.get("execution_metadata", {})
            
            # Validate required data
            if not devices:
                return Response({
                    'status': 'error',
                    'message': 'No devices provided'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            test_cases = test_suites.get("test_cases", [])
            if not test_cases:
                return Response({
                    'status': 'error',
                    'message': 'No test cases provided'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            print(f"Processing {len(test_cases)} test cases for {len(devices)} devices")
            
            # 3. Start background processing
            thread = threading.Thread(
                target=self.process_tests_in_background,
                args=(devices, test_suites, execution_metadata)
            )
            thread.daemon = True
            thread.start()
            
            # 4. Return immediate response
            return Response({
                'status': 'accepted',
                'message': f'Processing {len(test_cases)} test cases',
                'test_suite_id': test_suites.get("test_suite_id"),
                'test_suite_name': test_suites.get("test_suite_name"),
                'device_count': len(devices),
                'test_count': len(test_cases)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error in RunRobotTests: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def process_tests_in_background(self, devices, test_suites, execution_metadata):
        """Process all test cases in background thread"""
        try:
            test_cases = test_suites.get("test_cases", [])
            print(f"\n[BACKGROUND] Starting processing of {len(test_cases)} test cases")
            
            # Process each test case
            for idx, test_case in enumerate(test_cases, 1):
                print(f"\n[BACKGROUND] Processing test {idx}/{len(test_cases)}")
                self.execute_single_test(devices, test_case)
                
            print(f"\n[BACKGROUND] All test cases completed")
            
        except Exception as e:
            print(f"[BACKGROUND] Error in background processing: {str(e)}")
            import traceback
            traceback.print_exc()

    def execute_single_test(self, devices, test_case):
        """Execute a single Robot Framework test case"""
        test_case_id = test_case.get("test_case_id")
        test_case_name = test_case.get("test_case_name")
        execution_id = test_case.get("execution_id")
        
        print(f"\n[TEST EXECUTION] Starting test: {test_case_id}")
        print(f"  Test Name: {test_case_name}")
        print(f"  Execution ID: {execution_id}")
        print("🖥️🖥️🖥️🖥️🖥️🖥️🖥️🖥️🖥️🖥️🖥️🖥️🖥️🖥️🖥️🖥️🖥️🖥️🖥️🖥️🖥️",test_case_name)

        
        try:
            # 1. Update status to RUNNING
            # self.update_test_status(
            #     execution_id,
            #     status="running",
            #     started_at=datetime.now().isoformat()
            # )
            
            # 2. Write device configuration
            print(f"  Writing device configuration...")
            # write_devices_to_json(devices, ROBOT_FRAMEWORK_PATH)
            
            # 3. Prepare Robot Framework execution
            tests_path = os.path.abspath(os.path.join(ROBOT_FRAMEWORK_PATH, "tests"))
            output_dir = os.path.join(ROBOT_FRAMEWORK_PATH, "outputs", str(execution_id))
            os.makedirs(output_dir, exist_ok=True)
            
            # 4. Run Robot Framework command
            # robot --include BB-TRF-BRG-001 tests/
            cmd = [
                'robot',
                '--include', test_case_id,
                '--outputdir', output_dir,
                '--output', 'output.xml',
                '--log', 'log.html',
                '--report', 'report.html',
                tests_path
            ]
            
            print(f"  Running command: {' '.join(cmd)}")
            
            # Execute Robot Framework
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                # timeout=300000000  # 5 minute timeout
            )
            
            # 5. Process results
            exit_code = result.returncode
            stdout = result.stdout
            stderr = result.stderr
            
            test_status = "success" if exit_code == 0 else "failed"
            
            # print(f"  Test completed with status: {test_status}")
            # print(f"  Exit code: {exit_code}")
            
            if stdout:
                print(f"  STDOUT preview: {stdout[:200]}...")
            if stderr:
                print(f"  STDERR: {stderr[:200]}...")
            
            # 6. Update test status in OpenWISP


            # exit_code = 0
            # stdout = "executed test"
            # stderr = ""
            
            # test_status = "success" if exit_code == 0 else "failed"
            self.update_test_status(
                execution_id,
                status=test_status,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                # completed_at=datetime.now().isoformat()
            )
            
        # except subprocess.TimeoutExpired:
        #     print(f"  Test execution timed out!")
        #     self.update_test_status(
        #         execution_id,
        #         status="timeout",
        #         error_message="Test execution timed out after 5 minutes",
        #         completed_at=datetime.now().isoformat()
        #     )
            
        except Exception as e:
            print(f"  Error executing test: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # self.update_test_status(
            #     execution_id,
            #     status="failed",
            #     stderr=str(e),
            #     error_message=f"Robot Framework execution error: {str(e)}",
            #     completed_at=datetime.now().isoformat()
            # )

    def update_test_status(self, execution_id, **kwargs):
        """Update test execution status in OpenWISP"""
        try:
            # Prepare payload
            payload = {
                "execution_id": execution_id,
                **kwargs
            }
            
            print(f"\n[STATUS UPDATE] Updating execution {execution_id}")
            print(f"  Status: {kwargs.get('status')}")
            
            # For development - just log what would be sent
            print(f"  Payload: {json.dumps(payload, indent=2)}")
            
            # Uncomment below to actually send to OpenWISP
            # url = f"{OPENWISP_SERVER_URL}{OPENWISP_API_ENDPOINT}"
            # url = f"http://192.168.122.1:8000/api/v1/test-management/robot-test-result/" # local
            # url = f"http://54.234.248.241:8000/api/v1/test-management/robot-test-result/" # live 

            url = f"http://192.168.201.37:8000/api/v1/test-management/robot-test-result/" # local kalyani




            headers = {
                "Content-Type": "application/json",
                # "Authorization": f"Bearer {OPENWISP_API_TOKEN}"
            }
            
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=3000
            )
            
            if response.status_code == 200:
                print(f"  ✓ Successfully updated status in OpenWISP")
            else:
                print(f"  ✗ Failed to update status. Response: {response.status_code}")
                print(f"    Response text: {response.text}")
            
        except Exception as e:
            print(f"  Error updating test status: {str(e)}")