*** Settings ***
Library           ../../resources/keywords/wifi_lan.py
Library           OperatingSystem
Library           JSONLibrary
Library           SSHLibrary
Library           Collections
Library           String
Library           BuiltIn
Resource          ../../resources/keywords/common_keywords.robot
Suite Setup       Initialize Custom Log File

*** Variables ***
${CONFIG_FILE}    ${CURDIR}/../../devices/tc_02.json
${LOG_FOLDER}      ${CURDIR}/../../logs
${DURATION}       10
${BANDWIDTH}      450M
${INTERFACE}      wlan0

*** Test Cases ***
WiFi LAN RPi Performance Test via OpenWRT
    # Load configuration
    [Tags]    BB-INT-WWAN-001
    ${config}=        Load JSON From File    ${CONFIG_FILE}
    ${devices}=       Get From Dictionary    ${config}    devices
    ${OPENWRT}=       Get From Dictionary    ${devices}    openwrt
    ${RPI1}=          Get From Dictionary    ${devices}    RPI1
    ${RPI2}=          Get From Dictionary    ${devices}    RPI2
    ${SSID}=          Get From Dictionary    ${config}     SSID
    ${PSK}=           Get From Dictionary    ${config}     PSK
    ${ENCRYPTION}=    Get From Dictionary    ${config}     encryption

    Log Message To Custom File    ==== Starting WiFi LAN RPi Performance Test ====

    # Setup OpenWRT WiFi
    Log Message To Custom File     Connecting to OpenWRT: ${OPENWRT['ip']}
    Open Connection    ${OPENWRT['ip']}
    Login              ${OPENWRT['user']}    ${OPENWRT['password']}
    Log Message To Custom File     SSH connected to OpenWRT
    Configure OpenWRT Wireless    ${OPENWRT['ip']}    ${SSID}    ${PSK}
    Close Connection
    Log Message To Custom File     Configured WiFi on OpenWRT with SSID ${SSID}

    # Setup RPi1
    Log Message To Custom File     Configuring WiFi on RPi1 (${RPI1['ip']})
    Configure Rpi Static Ip And Wpa    ${RPI1['ip']}    ${RPI1['user']}    ${RPI1['password']}    ${RPI1['ip']}    ${SSID}    ${PSK}    ${ENCRYPTION}
    Log Message To Custom File     Configured WiFi on RPi1

    # Setup RPi2
    Log Message To Custom File     Configuring WiFi on RPi2 (${RPI2['ip']})
    Configure Rpi Static Ip And Wpa    ${RPI2['ip']}    ${RPI2['user']}    ${RPI2['password']}    ${RPI2['ip']}    ${SSID}    ${PSK}    ${ENCRYPTION}
    Log Message To Custom File     Configured WiFi on RPi2

    Sleep    15s
    Log Message To Custom File     Waited 15s for WiFi to stabilize

    # Ensure iperf3
    Ensure Iperf3 Installed    ${RPI1['ip']}    ${RPI1['user']}    ${RPI1['password']}
    Ensure Iperf3 Installed    ${RPI2['ip']}    ${RPI2['user']}    ${RPI2['password']}
    Log Message To Custom File     iperf3 installed on both RPis

    # Baseline system stats
    Log Message To Custom File     Capturing baseline system stats from OpenWRT
    Capture Baseline System Stats    ${OPENWRT['ip']}    ${OPENWRT['user']}    ${OPENWRT['password']}

    # Start iperf3 servers
    Log Message To Custom File     Starting iperf3 servers
    Start Iperf Server    ${RPI1['ip']}    ${RPI1['user']}    ${RPI1['password']}    5201
    Start Iperf Server    ${RPI2['ip']}    ${RPI2['user']}    ${RPI2['password']}    5202
    Log Message To Custom File     iperf3 servers started

    # Start monitoring
    Log Message To Custom File     Starting resource monitoring on OpenWRT
    Start Monitoring During Iperf    ${OPENWRT['ip']}    ${OPENWRT['user']}    ${OPENWRT['password']}

    # Start iperf3 clients in parallel (bidirectional)
    Log Message To Custom File     Starting bidirectional iperf3 clients
    Start Iperf Client Parallel    ${RPI1['ip']}    ${RPI1['user']}    ${RPI1['password']}    ${RPI2['ip']}    ${DURATION}    ${BANDWIDTH}    5202
    Start Iperf Client Parallel    ${RPI2['ip']}    ${RPI2['user']}    ${RPI2['password']}    ${RPI1['ip']}    ${DURATION}    ${BANDWIDTH}    5201

    # Wait for both to finish
    Wait For All Iperf Clients
    Log Message To Custom File     All iperf3 clients finished

    # Stop monitoring
    Stop Monitoring
    Log Message To Custom File     Monitoring stopped

    # Post-test stats
    Log Message To Custom File     Capturing post-test system stats
    Capture Post Test System Stats    ${OPENWRT['ip']}    ${OPENWRT['user']}    ${OPENWRT['password']}

    # Done
    Log Message To Custom File    ==== Completed WiFi LAN RPi Performance Test ====

