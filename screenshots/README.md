# Capturas de pantalla — MAC Flooding

Capturas del laboratorio en orden de demostración.

| # | Archivo | Descripción |
|---|---------|-------------|
| 1 | [01_topologia.png](screenshots/01_topologia.png) | Topología en PNETLab con nombre y matrícula visibles |
| 2 | [02_cam_antes.png](screenshots/02_cam_antes.png) | `show mac address-table count` en SW2 antes del ataque |
| 3 | [03_ataque_ejecutandose.png](screenshots/03_ataque_ejecutandose.png) | Script corriendo — contador de paquetes en tiempo real |
| 4 | [04_cam_desbordada.png](screenshots/04_cam_desbordada.png) | SW2 con la tabla CAM llena de MACs falsas |
| 5 | [05_trafico_expuesto.png](screenshots/05_trafico_expuesto.png) | `tcpdump` en Kali mostrando tráfico unicast de otros hosts |
| 6 | [06_contramedida_aplicada.png](screenshots/06_contramedida_aplicada.png) | Port Security configurado en SW2 |
| 7 | [07_post_mitigacion.png](screenshots/07_post_mitigacion.png) | Puerto en `err-disabled` tras detectar el flooding |
