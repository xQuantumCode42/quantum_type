import netifaces

for interface in netifaces.interfaces():
    print(f"Interface: {interface}")
    try:
        addresses = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addresses:
            print(f"IP: {addresses[netifaces.AF_INET][0]['addr']}")
    except:
        print("No IPv4 address")