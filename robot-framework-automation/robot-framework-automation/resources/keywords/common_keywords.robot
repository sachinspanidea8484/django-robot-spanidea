*** Settings ***
Library     SeleniumLibrary
Library     OperatingSystem
Library     DateTime
Library     SSHLibrary
Library     JSONLibrary
Library     Collections
Library     String
Library     BuiltIn  # For Sleep and other functions


*** Variables ***
${MAX_RETRIES}    3
${RETRY_INTERVAL}    2s
${DEVICE_FILE}     ${CURDIR}/../../devices/device_config.json
${LOG_FOLDER}      ${CURDIR}/../../logs

*** Keywords ***

#Setup Environment
#    Generate Device Config From Variables
#    Initialize Custom Log File
#
#Generate Device Config From Variables
#    # Create the device_config.json file directly from environment variables passed in the command
#    ${devices}=    Create List
#    FOR    ${i}    IN    RANGE    1    100  # Arbitrary large number to cover many devices
#        ${ip}=    Get Environment Variable    IP${i}
#        Run Keyword If    '${ip}' == ''    Break  # Stop if there's no IPx (end of devices)
#        ${user}=    Get Environment Variable    USER${i}
#        ${pass}=    Get Environment Variable    PASS${i}
#        ${device}=    Create Dictionary    ip=${ip}    username=${user}    password=${pass}
#        Append To List    ${devices}    ${device}
#    END
#    # Create device config dictionary
#    ${device_config}=    Create Dictionary    devices=${devices}
#    # Convert the device config dictionary to JSON
#    ${device_config_json}=    Evaluate    json.dumps(${device_config})    modules=json
#    # Save to devices/device_config.json
#    Create File    devices/device_config.json    ${device_config_json}

Initialize Custom Log File
    ${timestamp}=    Get Current Date    %Y%m%d_%H%M%S
    ${log_file}=     Set Variable    ${LOG_FOLDER}/custom_log_${timestamp}.log
    Set Suite Variable    ${LOG_FILE}    ${log_file}

Log Message To Custom File
    [Arguments]    ${message}
    ${timestamp}=    Get Current Date    %Y-%m-%d %H:%M:%S
    Append To File   ${LOG_FILE}    [INFO][${timestamp}] ${message}\n

Get Current Date
    [Arguments]    ${result_format}
    ${now}=    Evaluate    __import__('datetime').datetime.now().strftime('${result_format}')    modules=datetime
    RETURN    ${now}


Get Device Credentials
    [Arguments]    ${device}
    ${ip}=           Get From Dictionary    ${device}    ip
    ${user}=         Get From Dictionary    ${device}    username
    ${pass}=         Get From Dictionary    ${device}    password
    RETURN    ${ip}    ${user}    ${pass}

Connect To Device
    [Arguments]    ${ip}    ${user}    ${pass}
    Open Connection    ${ip}
    Login              ${user}    ${pass}

Disconnect From Device
    Close Connection

Get Devices From JSON
    [Documentation]    Load the device configurations from the JSON file
    ${json}=    Load JSON From File    ${DEVICE_FILE}
    ${devices}=    Get From Dictionary    ${json}    devices
    Log To Console   Devices: ${devices}  # Debugging line
    RETURN   ${devices}

Ping Host And Validate
    [Arguments]    ${host}    ${version}=ipv4
    ${cmd}=    Set Variable If    '${version}'=='ipv6'    ping6 -c 4 ${host}    ping -c 4 ${host}
    ${result}=    Execute Command    ${cmd}
    Log Message To Custom File    Ping ${version} result:\n${result}
    Should Contain    ${result}    0% packet loss
    RETURN    ${result}

Get MAC Addresses From Device
    ${output}=    SSHLibrary.Execute Command    ifconfig | grep -Eoi '([a-f0-9]{2}:){5}[a-f0-9]{2}'
    ${lines}=     Split String    ${output}    \n
    @{macs}=      Create List
    FOR    ${line}    IN    @{lines}
        ${mac}=    Strip String    ${line}
        Append To List    ${macs}    ${mac}
    END
    RETURN    @{macs}

Validate MAC Address Uniqueness
    [Arguments]    @{macs}
    ${unique_macs}=     Remove Duplicates    ${macs}
    ${mac_count}=       Get Length    ${macs}
    ${unique_count}=    Get Length    ${unique_macs}
    ${duplicate_count}=   Evaluate    ${mac_count} - ${unique_count}
    ${duplicates}=      Evaluate    [mac for mac in set(${macs}) if ${macs}.count(mac) > 1]

    ${all_macs_str}=     Catenate    SEPARATOR=\n    @{macs}
    ${unique_macs_str}=  Catenate    SEPARATOR=\n    @{unique_macs}
    ${duplicates_str}=   Catenate    SEPARATOR=\n    @{duplicates}

    Log Message To Custom File    All MACs:\n${all_macs_str}
    Log Message To Custom File    Unique MACs:\n${unique_macs_str}
    Log Message To Custom File    Duplicate MACs:\n${duplicates_str}
    Log Message To Custom File    Total MACs: ${mac_count}
    Log Message To Custom File    Unique MACs: ${unique_count}
    Log Message To Custom File    Duplicate Count: ${duplicate_count}

#    Should Be Equal    ${mac_count}    ${unique_count}    msg=Duplicate MAC addresses found!

Validate IPv4 DHCP Assignment
    [Arguments]    ${interface}    ${ip}
    ${ip4_output}=    Execute Command    ip -4 -o addr show ${interface} | awk '{print $4}' | cut -d/ -f1
    Log Message To Custom File    IPv4 Output for ${interface}:\n${ip4_output}
    ${status_ipv4}=    Run Keyword And Return Status    Should Match Regexp    ${ip4_output}    \\d{1,3}(\\.\\d{1,3}){3}
    Run Keyword If    not ${status_ipv4}    Log Message To Custom File    IPv4 address validation failed: ${ip4_output}
    Set Suite Variable    ${STATUS_IPV4}    ${status_ipv4}

Validate IPv6 DHCP Assignment
    [Arguments]    ${interface}    ${ip}
    ${ip6_output}=    Execute Command    ip -6 -o addr show dev ${interface} | awk '$3 == "inet6" && $4 !~ /^fe80/ {print $4}' | cut -d/ -f1
    Log Message To Custom File    IPv6 Output for ${interface}:\n${ip6_output}
    ${status_ipv6}=    Run Keyword And Return Status    Should Match Regexp    ${ip6_output}    [0-9a-fA-F]{1,4}(:[0-9a-fA-F]{1,4}){7}
    Run Keyword If    not ${status_ipv6}    Log Message To Custom File    IPv6 address validation failed: ${ip6_output}
    Set Suite Variable    ${STATUS_IPV6}    ${status_ipv6}

Validate DHCP Process Running
    ${dhcp_proc}=    Execute Command    ps | grep -E "udhcpc|dhclient|dhcpcd"
    Log Message To Custom File    DHCP Process Output:\n${dhcp_proc}
    ${status_dhcp}=    Run Keyword And Return Status    Should Contain Any    ${dhcp_proc}    udhcpc    dhclient    dhcpcd
    Run Keyword If    not ${status_dhcp}    Log Message To Custom File    DHCP process not found:\n${dhcp_proc}
    Set Suite Variable    ${STATUS_DHCP}    ${status_dhcp}

Execute Command
    [Arguments]    ${command}
    ${output}=    Execute Command    ${command}
    RETURN    ${output}