import os
import sys
import shlex
import subprocess
from colorama import Fore, Style, init

init(autoreset=True)

if os.getuid() != 0:
    print(Fore.RED + "[-] Requires root privileges! Run with sudo." + Style.RESET_ALL)
    sys.exit(1)

BANNER = f"""{Fore.CYAN}
    __  ___                        ____          
   /  |/  /___ _______________ ____ / __/__  _____ 
  / /|_/ / __ `/ ___/ ___/ __ \ __ \/ /_/ _ \/ ___/ 
 / /  / / /_/ / /__(__  ) /_/ / /_/ / __/  __ / /     
/_/  /_/\__,_/\___/____/ .___/\____/_/  \___/_/      
                      /_/                            
{Style.RESET_ALL}"""

def clear_screen():
    subprocess.run("clear", shell=True)

def run(cmd):
    r = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
    return r

def get_interfaces():
    result = run("ip -o link show")
    interfaces = []
    for line in result.stdout.splitlines():
        parts = line.split(": ")
        if len(parts) > 1:
            if "lo" not in parts[1] and "POINTOPOINT" not in parts[1]:
                interfaces.append(parts[1].split("@")[0].strip())
    return interfaces

def change_mac(interface, option, val=""):
    print(Fore.YELLOW + f"[*] Disabling interface {interface}..." + Style.RESET_ALL)
    run(f"ip link set {interface} down")
    
    cmd = f"macchanger {option} {val} {interface}".strip()
    result = run(cmd)
    
    if result.returncode == 0:
        print(Fore.GREEN + f"[+] Successfully changed MAC for {interface}!" + Style.RESET_ALL)
        show_res = run(f"macchanger -s {interface}")
        for line in show_res.stdout.splitlines():
            if "Current MAC" in line:
                print(Fore.CYAN + f"    {line.strip()}" + Style.RESET_ALL)
    else:
        print(Fore.RED + f"[-] Error: {result.stderr.strip()}" + Style.RESET_ALL)
        
    print(Fore.YELLOW + f"[*] Enabling interface {interface}..." + Style.RESET_ALL)
    run(f"ip link set {interface} up")

def interactive_mode():
    clear_screen()
    print(BANNER)
    print(Fore.GREEN + "[+] Welcome to Interactive Mode\n" + Style.RESET_ALL)
    
    interfaces = get_interfaces()
    if not interfaces:
        print(Fore.RED + "[-] No network interfaces found!" + Style.RESET_ALL)
        sys.exit(1)
        
    print(Fore.YELLOW + "[*] Available interfaces:" + Style.RESET_ALL)
    for i, iface in enumerate(interfaces, 1):
        print(f"    {i}. {iface}")
        
    choice = input(Fore.CYAN + "\n[?] Select interface number: " + Style.RESET_ALL)
    try:
        selected_iface = interfaces[int(choice) - 1]
    except (ValueError, IndexError):
        print(Fore.RED + "[-] Invalid selection!" + Style.RESET_ALL)
        sys.exit(1)
        
    print("\nChoose MAC modification type:")
    print("  1. Fully Random (-r)")
    print("  2. Same vendor (-a)")
    print("  3. Keep ending (-e)")
    print("  4. Custom MAC (-m)")
    print("  5. Restore permanent (-p)")
    
    opt_choice = input(Fore.CYAN + "\n[?] Enter choice (1-5): " + Style.RESET_ALL)
    
    if opt_choice == "1":
        change_mac(selected_iface, "-r")
    elif opt_choice == "2":
        change_mac(selected_iface, "-a")
    elif opt_choice == "3":
        change_mac(selected_iface, "-e")
    elif opt_choice == "4":
        custom_mac = input(Fore.CYAN + "[?] Enter MAC (XX:XX:XX:XX:XX:XX): " + Style.RESET_ALL)
        change_mac(selected_iface, "-m", custom_mac)
    elif opt_choice == "5":
        change_mac(selected_iface, "-p")
    else:
        print(Fore.RED + "[-] Invalid option!" + Style.RESET_ALL)

def main():
    if len(sys.argv) < 2 or sys.argv[1].lower() == "cli":
        interactive_mode()
    else:
        if len(sys.argv) < 3:
            clear_screen()
            print(BANNER)
            print(Fore.RED + "[-] Usage: python MacSpofer.py <interface> <option> [value]" + Style.RESET_ALL)
            print(Fore.YELLOW + "[*] Or type 'python MacSpofer.py cli' for interactive mode." + Style.RESET_ALL)
            sys.exit(1)
            
        interface = sys.argv[1]
        option = sys.argv[2]
        val = sys.argv[3] if len(sys.argv) > 3 else ""
        
        clear_screen()
        print(BANNER)
        change_mac(interface, option, val)

if __name__ == "__main__":
    main()
