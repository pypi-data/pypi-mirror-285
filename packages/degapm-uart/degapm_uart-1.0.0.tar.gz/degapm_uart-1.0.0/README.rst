Package: degapm_uart
=====================

Module Introduction
--------------------
This module is designed for A2000 test platform backplane control via uart port, which includes  
1. Get target slot device's voltage and current
2. Set target slot device's voltage 


Function Definition
--------------------
1. get_voltage_current_uart
    - Parameter: 
        - tray: int, specify the device number (0~11)
    - Return:
        - Success: return a tuple (voltage, current)
        - Fail: return false

2. set_voltage_uart
    - Parameter: 
        - tray: int, specify the device number (0~11)
        - value: int, specify the voltage to set_led_status
    - Return:
        - Success: return True
        - Fail: return false

Sample Code
--------------
1. get_voltage_current  

::

    # python3
    from degapm_uart import degapm_uart

    tray_number = 1
    result = degapm_uart.get_voltage_current_uart(tray_number)
    if result:
        voltage, current = result
        print("device {0} voltage: {1}, current: {2}").format(tray_number, voltage, current)
    else:
    print("Get device {0} voltage & current fail!").format(tray_number)  

2. set_voltage_uart

::

    # python3
    from degapm_uart import degapm_uart

    tray_number = 1
    voltage_value = 12000
    if degapm_uart.set_voltage_uart(tray_number, voltage_value):
        print("Set device {0} voltage to {1}").format(tray_number, voltage_value)
    else:
        print("Set device {0} voltage fail!").format(tray_number)  


Contact us
-----------------------------------------------------------------------------------
1. Official website: <https://degastorage.com/>
2. Author E-mail: <jiaming.shi@degastorage.com>