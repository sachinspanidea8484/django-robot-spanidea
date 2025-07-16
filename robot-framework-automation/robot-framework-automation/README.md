# 🚀 Dynamic Robot Framework for Networking Automation

This project implements a scalable and dynamic Robot Framework-based test automation suite tailored for SSH-enabled network device testing.

---

## 📁 Project Structure

```
POCRobot/
├── data/
│   └── testdata.json
├── devices/
│   └── device_config.json
├── libraries/
│   └── device_utils.py
├── logs/
├── results/
├── resources/
│   ├── keywords/
│   │   └── common_keywords.robot
│   └── variables/
│       ├── env_variables.json
│       └── global_variables.robot
├── tests/
│   ├── interfaces/
│   │   ├── mac_verification.robot
│   │   └── mac_networking_dynamic.robot
│   └── networking/
│       ├── dhcpclientverification.robot
│       └── network.robot
├── run_tests.sh
├── run_tests.bat
├── run_tests_api.py
└── requirements.txt
```

---

## 🔧 Setup Instructions

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
```

---

## 🚦 Running Tests

### 🔹 Shell (Linux/macOS)
```bash
./run_tests.sh
```

### 🔹 Batch (Windows)
```cmd
run_tests.bat
```

### 🔹 API Trigger
```bash
curl -X POST http://localhost:8000/run-tests
```

---

## 🛠 API Endpoint

| Method | Endpoint        | Description                  |
|--------|------------------|------------------------------|
| POST   | `/run-tests`     | Triggers Robot test execution |

---

## 📑 Configuration Files

### `device_config.json`
```json
{
  "devices": [
    { "ip": "192.168.1.1", "username": "admin", "password": "pass" },
    { "ip": "192.168.1.2", "username": "admin", "password": "pass" }
  ]
}
```

### `testdata.json`
```json
{
  "mac_verification": "ip link show | grep ether",
  "interface_status": "ip addr show"
}
```

---

## 📬 Logs and Reports
- All runtime logs stored under `logs/`
- Test results (log.html, report.html, output.xml) saved in `results/`

---

## 🌐 Notes
- REST API (`run_tests_api.py`) requires `uvicorn`: `pip install fastapi uvicorn`
- Make sure your test devices are reachable from the host
- Customize validation logic in `common_keywords.robot`

---

Made with ❤️ for dynamic network automation
