# Capturas de pantalla — MAC Flooding

Capturas del laboratorio en orden de demostración.

| Archivo | Descripción |
|---------|-------------|
| `01_topologia.png` | Topología en PNETLab con nombre y matrícula visibles |
| `02_cam_antes.png` | `show mac address-table count` en SW2 antes del ataque |
| `03_ataque_ejecutandose.png` | Script corriendo — contador de paquetes en tiempo real |
| `04_cam_desbordada.png` | SW2 con la tabla CAM llena de MACs falsas |
| `05_trafico_expuesto.png` | `tcpdump` en Kali mostrando tráfico unicast de otros hosts (fail-open) |
| `06_contramedida_aplicada.png` | Port Security configurado en SW2 |
| `07_post_mitigacion.png` | Puerto en `err-disabled` tras detectar el flooding |
