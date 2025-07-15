from flask import Flask, request
import subprocess

app = Flask(__name__)


@app.route('/run-tests', methods=['POST'])
def run_tests():
    try:
        result = subprocess.run(['robot', 'tests/'], capture_output=True, text=True)
        print("yo")
        return {
            'status': 'success',
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)