import json
import boto3
import time
from datetime import datetime
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('DriverStressMetrics')

def lambda_handler(event, context):
    try:
        logger.info("Evento recibido: " + json.dumps(event))
        
        if 'body' in event:
            body = json.loads(event['body'])
        else:
            body = event
        
        required_fields = ['deviceId', 'heartRate']
        if not all(field in body for field in required_fields):
            raise ValueError(f"Faltan campos requeridos: {required_fields}")
        
        device_id = body['deviceId']
        heart_rate = int(body['heartRate'])
        
        timestamp = body.get('timestamp', datetime.utcnow().isoformat())
        
        if isinstance(timestamp, (int, float)):
            timestamp = str(timestamp)

        stress_level = "LOW"
        if heart_rate > 90:
            stress_level = "HIGH"
        elif heart_rate > 75:
            stress_level = "MEDIUM"

        item = {
            'deviceId': device_id,
            'timestamp': timestamp, 
            'heartRate': heart_rate,
            'stressLevel': stress_level
        }
        
        logger.info("Escribiendo en DynamoDB: " + json.dumps(item))
        response = table.put_item(Item=item)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Datos guardados',
                'data': item,
                'dynamoResponse': response
            })
        }
        
    except Exception as e:
        logger.error("Error: " + str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'eventReceived': event
            })
        }