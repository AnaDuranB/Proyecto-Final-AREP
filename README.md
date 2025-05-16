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

```
Frontend (este código) → API Gateway AWS → Backend de análisis (Rekognition/Lambda)
```

## Requisitos técnicos

- Navegador moderno con soporte para:
  - getUserMedia API (para acceso a cámara)
  - Canvas API
  - Fetch API
- Conexión a internet para comunicarse con el backend
- Permisos para acceder a la cámara del dispositivo

## Configuración

1. Reemplazar `AWS_CONFIG.apiUrl` en `script.js` con el endpoint de tu API Gateway
2. Asegurarse que el backend esté configurado para recibir imágenes en base64 y devolver un JSON con `{ stressDetected: boolean }`

## Uso

1. Abrir `index.html` en un navegador
2. Permitir el acceso a la cámara cuando se solicite
3. El sistema comenzará automáticamente a analizar las expresiones faciales
4. El estado se mostrará en la pantalla:
   - Verde: Estado normal
   - Rojo: Estrés detectado (se envía alerta al supervisor)

## Estructura de archivos

- `index.html`: Interfaz principal
- `script.js`: Lógica de captura y análisis
- `styless.css`: Estilos visuales

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
