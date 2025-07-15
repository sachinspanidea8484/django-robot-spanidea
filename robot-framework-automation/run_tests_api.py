from fastapi import FastAPI, HTTPException
import subprocess
import uvicorn
import re
import os

app = FastAPI()


# Function to generate the .env file from the robot command
def generate_env_file(robot_command):
    # Regular expression to extract variables from the robot command
    pattern = r'--variable (\w+):([^ ]+)'

    # Find all the variable-value pairs in the robot command
    matches = re.findall(pattern, robot_command)

    device_count = len(matches) // 3  # Since each device has 3 variables (IP, USER, PASS)

    # Prepare the .env content
    env_content = [f"DEVICE_COUNT={device_count}"]

    for i in range(device_count):
        ip = matches[i * 3 + 0][1]
        user = matches[i * 3 + 1][1]
        password = matches[i * 3 + 2][1]

        # Add variables to the .env content
        env_content.append(f"IP{i + 1}={ip}")
        env_content.append(f"USER{i + 1}={user}")
        env_content.append(f"PASS{i + 1}={password}")

    # Write to .env file
    with open('.env', 'w') as f:
        f.write("\n".join(env_content))


@app.post("/run-tests")
def run_tests(test_suite: str = "tests/interfaces/mac_networking_dynamic.robot",
              robot_command: str = None,
              tags: str = None):
    try:
        # If the robot command is passed, generate the .env file
        if robot_command:
            generate_env_file(robot_command)

        # Prepare the Robot Framework command
        command = ["robot"]

        # If tags are specified, add them to the command
        if tags:
            command.extend(["--include", tags])

        # Add the test suite to the command
        command.append(test_suite)

        # Run Robot Framework command
        result = subprocess.run(
            command,
            capture_output=True, text=True
        )

        return {
            "status": "completed",
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("run_tests_api:app", host="0.0.0.0", port=8000, reload=True)
