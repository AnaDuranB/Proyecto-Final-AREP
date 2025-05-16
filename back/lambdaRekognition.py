import json
import boto3
import os
import time
from datetime import datetime, timedelta
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
heart_rate_table = dynamodb.Table('HeartRateData')
facial_table = dynamodb.Table('FacialAnalysisData')

def lambda_handler(event, context):
    try:
        logger.info("Evento recibido: " + json.dumps(event))
        
        body = json.loads(event['body']) if 'body' in event else event
        
        required_fields = ['driverId', 'heartRate']
        if not all(field in body for field in required_fields):
            raise ValueError(f"Faltan campos requeridos: {required_fields}")
        
        timestamp = int(time.time()) if 'timestamp' not in body else int(body['timestamp'])
        heart_rate = int(body['heartRate'])
        
        item = {
            'driverId': body['driverId'],
            'timestamp': timestamp,
            'heartRate': heart_rate,
            'stressLevel': calculate_stress_level(heart_rate)
        }
        
        # Guardar en DynamoDB
        heart_rate_table.put_item(Item=item)
        logger.info(f"Datos cardíacos guardados: {item}")
        
        # Verificar estrés combinado
        check_combined_stress(body['driverId'], timestamp)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Datos cardíacos guardados',
                'timestamp': timestamp
            })
        }
        
    except Exception as e:
        logger.error("Error: " + str(e), exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def calculate_stress_level(heart_rate):
    if heart_rate > 90:
        return 'HIGH'
    elif heart_rate > 75:
        return 'MEDIUM'
    return 'LOW'

def check_combined_stress(driver_id, timestamp):
    try:
        timestamp_dt = datetime.fromtimestamp(timestamp)
        start_time = int((timestamp_dt - timedelta(minutes=2)).timestamp())
        end_time = int((timestamp_dt + timedelta(minutes=2)).timestamp())
        
        logger.info(f"Buscando datos faciales entre {start_time} y {end_time}")
        
        facial_data = facial_table.query(
            KeyConditionExpression='driverId = :driver AND #ts BETWEEN :start AND :end',
            ExpressionAttributeNames={'#ts': 'timestamp'},
            ExpressionAttributeValues={
                ':driver': driver_id,
                ':start': start_time,
                ':end': end_time
            }
        ).get('Items', [])
        
        if not facial_data:
            logger.info("No se encontraron datos faciales en la ventana temporal")
            return
        latest_facial = max(facial_data, key=lambda x: x['timestamp'])
        logger.info(f"Datos faciales más recientes: {latest_facial}")
        
        heart_data = heart_rate_table.get_item(
            Key={
                'driverId': driver_id,
                'timestamp': timestamp
            }
        ).get('Item', {})
        
        if not heart_data:
            logger.warning("No se encontraron los datos cardíacos recién guardados")
            return
            
        if (latest_facial.get('stressDetected', False) and 
            heart_data.get('stressLevel') in ['MEDIUM', 'HIGH']):
            
            send_combined_alert(
                driver_id=driver_id,
                heart_rate=heart_data['heartRate'],
                stress_level=heart_data['stressLevel'],
                facial_emotion=latest_facial.get('dominantEmotion', 'DESCONOCIDO'),
                timestamp=timestamp
            )
            
    except Exception as e:
        logger.error(f"Error en verificación combinada: {str(e)}", exc_info=True)
        raise

def send_combined_alert(driver_id, heart_rate, stress_level, facial_emotion, timestamp):
    """Envía alerta SNS cuando se detecta estrés combinado"""
    try:
        alert_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')
        
        message = (
            "🚨 ALERTA COMBINADA DE ESTRÉS 🚨\n\n"
            f"Conductor ID: {driver_id}\n"
            f"Fecha y Hora: {alert_time}\n"
            f"Frecuencia Cardíaca: {heart_rate} bpm\n"
            f"Nivel de Estrés: {stress_level}\n"
            f"Emoción Facial Detectada: {facial_emotion}\n\n"
            "Acción Requerida: Por favor, evalúe la situación del conductor."
        )
        
        # Publicar el mensaje en SNS
        sns_client = boto3.client('sns')
        sns_client.publish(
            TopicArn=os.environ.get('SNS_TOPIC_ARN'),  # Asegúrate de tener el ARN del tópico SNS en las variables de entorno
            Message=message,
            Subject='Alerta de Estrés Combinado'
        )
        
        logger.info(f"Alerta enviada para conductor {driver_id} a las {alert_time}")
        
    except Exception as e:
        logger.error(f"Error al enviar alerta SNS: {str(e)}", exc_info=True)
        raise