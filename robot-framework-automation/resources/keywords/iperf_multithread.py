import threading
import time
import subprocess
from robot.api.deco import keyword

class IperfMultithread:

    def __init__(self):
        self.threads = []

    @keyword('Start Iperf Server')
    def start_iperf_server(self, host, username, password):
        def server():
            print(f"Starting iperf3 server on {host}...")
            subprocess.run([
                "sshpass", "-p", password, "ssh",
                f"{username}@{host}", "nohup iperf3 -s > /tmp/iperf3_server.log 2>&1 &"
            ])
        t = threading.Thread(target=server)
        t.start()
        self.threads.append(t)

    @keyword('Start Iperf Client')  # Custom name for Robot Framework
    def start_iperf_client(self, client_host, username, password, server_ip, duration=20, bandwidth="450M"):
        def client():
            print(f"Starting iperf3 client on {client_host} to {server_ip}...")
            subprocess.run([
                "sshpass", "-p", password, "ssh",
                f"{username}@{client_host}",
                f"iperf3 -c {server_ip} -b {bandwidth} -t {duration}"
            ])
        t = threading.Thread(target=client)
        t.start()
        self.threads.append(t)

    @keyword('Monitor OpenWRT')  # Custom name for Robot Framework
    def monitor_openwrt(self, host, username, password, duration=20):
        def monitor():
            print(f"Monitoring CPU and memory on {host}...")
            subprocess.run([
                "sshpass", "-p", password, "ssh",
                f"{username}@{host}",
                f"sar -u 1 {duration} > /tmp/cpu_during_iperf.log & sar -r 1 {duration} > /tmp/mem_during_iperf.log &"
            ])
        t = threading.Thread(target=monitor)
        t.start()
        self.threads.append(t)

    @keyword('Wait For All')  # Custom name for Robot Framework
    def wait_for_all(self):
        for t in self.threads:
            t.join()
