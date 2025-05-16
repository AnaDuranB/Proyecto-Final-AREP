// Configuración
const AWS_CONFIG = {
    region: 'us-east-1',
    apiUrl: 'https://z7pl9c79n3.execute-api.us-east-1.amazonaws.com/prod' // Reemplazar con tu API Gateway
};

// Elementos del DOM
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const statusDiv = document.getElementById('status');

// Variables de estado
let isAnalyzing = false;
let lastCaptureTime = 0;
const CAPTURE_COOLDOWN = 10000; // 10 segundos entre capturas

// Iniciar cámara
async function initCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                facingMode: 'user',
                width: { ideal: 640 },
                height: { ideal: 480 }
            },
            audio: false
        });
        video.srcObject = stream;
        statusDiv.textContent = "Cámara activa - Analizando expresiones...";
        
        setInterval(analyzeExpression, 2000);
    } catch (err) {
        statusDiv.textContent = `Error: ${err.message}`;
        console.error(err);
    }
}

// Analizar expresión facial
async function analyzeExpression() {
    if (isAnalyzing) return;
    isAnalyzing = true;
    
    try {
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        const imageBase64 = canvas.toDataURL('image/jpeg').split(',')[1];
        
        const response = await fetch(`${AWS_CONFIG.apiUrl}/detect-stress`, {
            method: 'POST',
            body: JSON.stringify({ image: imageBase64 }),
            headers: { 'Content-Type': 'application/json' }
        });
        
        const result = await response.json();
        
        if (result.stressDetected) {
            statusDiv.textContent = "🚨 Alerta de estrés enviada al supervisor";
            statusDiv.style.color = "red";
        } else {
            statusDiv.textContent = "Estado normal";
            statusDiv.style.color = "green";
        }
    } finally {
        isAnalyzing = false;
    }
}

// Iniciar aplicación
initCamera();