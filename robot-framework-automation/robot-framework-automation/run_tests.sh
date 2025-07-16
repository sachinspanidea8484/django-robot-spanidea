#!/bin/bash

# Ensure the results folder exists
mkdir -p results

# Check if a specific test file and tags were passed, or use defaults
TEST_SUITE="${1:-tests/interfaces/mac_networking_dynamic.robot}"
TAGS="${2:-}"

# Generate the .env file dynamically based on the robot command
# You can pass the full robot command dynamically for more flexibility
python3 generate_env.py "robot --variable IP1:192.168.1.1 --variable USER1:admin --variable PASS1:secret \
      --variable IP2:192.168.1.2 --variable USER2:admin --variable PASS2:secret $TEST_SUITE"

# Source the .env file to make sure the environment variables are available for the robot command
export $(cat .env | xargs)

# Prepare the Robot Framework command
ROBOT_COMMAND="robot --output results/output.xml --log results/log.html --report results/report.html \
               --logtitle 'Execution Log' --reporttitle 'Execution Report'"

# Add tags to the command if specified
if [ -n "$TAGS" ]; then
  ROBOT_COMMAND="$ROBOT_COMMAND --include $TAGS"
fi

# Run Robot Framework with proper output paths
$ROBOT_COMMAND $TEST_SUITE

