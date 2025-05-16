# Monitor de Estrés para Conductores - Prototipo

## Descripción

Este prototipo implementa un sistema de detección de estrés en tiempo real para conductores de transporte público mediante análisis facial. El sistema captura imágenes del conductor a través de la cámara web y las analiza para detectar signos de estrés, alertando al supervisor cuando se identifica una situación de riesgo.

## Características principales

- 🎥 Captura de video en tiempo real desde la cámara del dispositivo
- 🤖 Análisis facial para detectar expresiones de estrés
- 🚨 Notificación visual cuando se detecta estrés
- ⏱️ Límite de capturas para evitar sobrecarga (10 segundos entre análisis)
- ☁️ Integración con API backend en AWS

## Arquitectura del sistema

![PROYECTO_AREP-MVP drawio](https://github.com/user-attachments/assets/a0385b0e-dad2-43ca-a6c5-81addd5ff5ab)

El sistema está compuesto por un frontend y un backend, con la siguiente arquitectura:

- Frontend:

  - Interfaz web (index.html, script.js, styles.css) para captura de video, análisis facial, y visualización del estado.

- Backend:
  
  - Script de Google Apps Script (AppScript.js) para obtener datos de frecuencia cardíaca desde Google Fit y enviarlos a aws.
  - AWS Lambda (lambdaSmartwatch.py): Procesa datos de frecuencia cardíaca recibidos desde el smartwatch, los almacena en DynamoDB, y calcula el nivel de estrés.
  - AWS Lambda (lambdaRekognition.py): Procesa datos de frecuencia cardíaca y verifica estrés combinado con datos faciales, enviando alertas SNS cuando se detecta estrés.
  - Amazon API Gateway: Expone endpoints para recibir datos de frecuencia cardíaca y análisis facial.
  - Amazon DynamoDB:
    - Tabla DriverStressMetrics: Almacena datos de frecuencia cardíaca desde el smartwatch.
    - Tabla FacialAnalysisData: Almacena resultados del análisis facial.
  - Amazon SNS: Envía notificaciones cuando se detecta estrés combinado (frecuencia cardíaca alta y expresión facial de estrés).

## Configuración

### 🔧 Configuración Rápida

1. **Google Fit → AWS**
    - Ejecutar `AppScript.js` en Google Apps Script
    - Autorizar permisos: `fitness.heart_rate.read`
2. **AWS Backend**
    - Desplegar Lambdas (`lambdaSmartwatch.py` y `lambdaRekognition.py`)
    - Crear tablas DynamoDB:
        - `DriverStressMetrics` (PK: `deviceId`, SK: `timestamp`)
        - `FacialAnalysisData` (PK: `driverId`, SK: `timestamp`)
    - Configurar SNS: Tema `COMBINED_ALERTS_TOPIC`
3. **Frontend**
    - Modificar `AWS_CONFIG.apiUrl` en `script.js`
    - Hostear `index.html` en servidor web
4. **Pruebas**
    - Enviar datos de prueba a `/heartrate`:CopyDownload
        
        json
        
        ```
        {
          "deviceId": "001",
          "heartRate": 85,
          "timestamp": 1715304120
        }
        ```
        

**Listo!** El sistema comenzará a monitorear y alertar.

> 💡 Nota: Verificar logs en CloudWatch para diagnóstico.
>

## Uso

### 🚀 Uso del Sistema

### **1. Inicio del Monitoreo**

- **Smartwatch**:
    - Asegúrate de que esté conectado a Google Fit y compartiendo datos de frecuencia cardíaca.
- **Cámara**:
    - Abre la interfaz web (`index.html`) y permite el acceso a la cámara.

### **2. Flujo Automático**

- **Cada 60 minutos**:
    - El script `AppScript.js` envía datos cardíacos a AWS.
- **Análisis Facial (Tiempo Real)**:
    - La cámara captura imágenes cada 2 segundos y las envía a `lambdaRekognition.py`.

### **3. Alertas**

- **Condición para Alerta**:
    - Si se detecta **ambos** en una ventana de ±2 minutos:
        - Frecuencia cardíaca ≥ 75 bpm (`MEDIUM/HIGH`)
        - Emoción `ANGRY/FEAR` con ≥50% de confianza.
- **Notificación**:
    - Llega al tópico SNS (`COMBINED_ALERTS_TOPIC`) con detalles:CopyDownload
        
        plaintext
        
        ```
        🚨 ALERTA: Conductor 003 - 129 bpm (HIGH) + ANGRY (85%)
        ```

## Estructura de archivos

```
backend/
├── google-fit/
│   └── AppScript.js          # Integración Google Fit → AWS
├── lambdas/
│   ├── lambdaSmartwatch.py   # Procesamiento datos cardíacos
│   └── lambdaRekognition.py  # Análisis facial + alertas
frontend/
├── index.html                # Interfaz de monitoreo
├── script.js                 # Lógica de cámara
└── styles.css                # Estilos

```

## Limitaciones conocidas

- Prototipo inicial con análisis básico
- Dependencia de la calidad de la cámara y condiciones de iluminación
- Intervalo fijo entre análisis (2 segundos)
- Requiere configuración del backend para funcionamiento completo

## Mejoras futuras

- Implementar modelo de machine learning más sofisticado
- Añadir retroalimentación visual de los puntos faciales detectados
- Incluir métricas de nivel de estrés (no solo binario)
- Opción para calibrar según el conductor
- Integración con sistemas de telemetría del vehículo

## Integrantes

- Laura Natalia Rojas
- Maria Valentina Torres
- Ana Maria Duran
