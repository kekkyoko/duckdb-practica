# Proyectos Integradores
Materia: Análisis y exploración de datos

### Cuadro Sinóptico: Tipos y Métodos de Conmutación

```text
                                          ┌─ 1. Conmutación de Circuitos ──► Establece un enlace físico dedicado antes de transmitir (ej. PSTN, ISDN) [1, 2].
                                          │
                  ┌─ General (Redes/WAN) ─┼─ 2. Conmutación de Paquetes ───► Fragmenta los datos en paquetes enviados por rutas compartidas o circuitos virtuales [3-5].
                  │                       │
                  │                       └─ 3. Conmutación de Mensajes ───► Transmite el mensaje completo de nodo en nodo mediante almacenamiento y reenvío.
Tipos de          │
Conmutación ──────┤
                  │                       ┌─ 4. Store-and-Forward ─────────► Recibe la trama completa en un búfer, verifica el FCS (errores) y reenvía (estándar Cisco) [6, 7].
                  └─ En Switches (Capa 2) ┤
                                          └─ 5. Cut-Through ───────────────► Lee solo la dirección MAC de destino y reenvía la trama de inmediato sin validar FCS [6].
                                                                                └─ Variante: Fragment-Free (evalúa únicamente los primeros 64 bytes) [7].
```

---

### Descripción Breve

* **1. Conmutación de Circuitos:** Requiere la reserva previa de un canal o circuito físico dedicado entre emisor y receptor durante toda la comunicación [1, 2].
* **2. Conmutación de Paquetes:** La información se fragmenta en paquetes o tramas que contienen encabezados y viajan por redes compartidas a través de circuitos virtuales [3-5].
* **3. Conmutación de Mensajes:** Envía la información completa de un nodo intermedio a otro, almacenando el mensaje completo antes de retransmitirlo al siguiente salto.
* **4. Store-and-Forward (Método de Switch):** El switch almacena la trama completa en memoria, valida su integridad mediante el campo de verificación de errores (FCS) y luego decide su reenvío; es el modo predeterminado en switches Cisco [6, 7].
* **5. Cut-Through (Método de Switch):** El switch examina únicamente la dirección MAC de destino situada en la cabecera e inicia el reenvío bit a bit de forma inmediata para reducir la latencia, sin esperar a recibir la trama completa ni comprobar el FCS [6, 8]. Cuenta con la variante **Fragment-Free**, la cual lee los primeros 64 bytes para evitar el reenvío de tramas defectuosas por colisiones [7].