"""
This code is developed using reference from
https://docs.aws.amazon.com/rekognition/latest/customlabels-dg/ex-lambda.html
It combines Amazon Rekognition for image analysis and Amazon Comprehend for sentiment analysis.
"""

import json
import logging
import boto3
from decimal import Decimal

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Define the label we're looking for in the image
# TODO: Replace 'OBJECT_TO_DETECT' with the specific object you want to detect
LABEL = 'OBJECT_TO_DETECT'

# Initialize AWS service clients
rekognition_client = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')
comprehend_client = boto3.client('comprehend')

def float_to_decimal(obj):
    """
    Recursively convert float values to Decimal for DynamoDB compatibility.
    """
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: float_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [float_to_decimal(i) for i in obj]
    else:
        return obj

def detect_sentiment(text):
    """
    Detect sentiment of the given text using Amazon Comprehend.
    """
    if not text:
        return None
    response = comprehend_client.detect_sentiment(Text=text, LanguageCode='en')
    return response['Sentiment']

def lambda_handler(event, context):
    """
    This function is triggered by an S3 event when an image is uploaded.
    It performs image analysis using Amazon Rekognition, sentiment analysis using Amazon Comprehend,
    stores results in DynamoDB, and sends a notification via SNS.
    """
    logger.info(f"Event: {json.dumps(event)}")

    # Extract bucket and image information from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    image_key = event['Records'][0]['s3']['object']['key']

    try:
        # Detect labels in the image
        # TODO: Adjust MinConfidence if needed (0-100, higher value means more certainty)
        response_labels = rekognition_client.detect_labels(
            Image={'S3Object': {'Bucket': bucket, 'Name': image_key}},
            MinConfidence=70
        )

        # Detect text in the image
        response_text = rekognition_client.detect_text(
            Image={'S3Object': {'Bucket': bucket, 'Name': image_key}}
        )

        # Extract detected labels and texts
        detected_labels = [label['Name'].lower() for label in response_labels['Labels']]
        detected_texts = [text['DetectedText'] for text in response_text['TextDetections']]

        logger.info(f"Detected labels: {detected_labels}")
        logger.info(f"Detected texts: {detected_texts}")

        # Check if the specific LABEL is found in the detected labels
        if LABEL.lower() in detected_labels:
            status = f"Success! {LABEL} found"
        else:
            status = f"Failed! {LABEL} not found"

        # Perform sentiment analysis on detected text
        full_text = ' '.join(detected_texts)
        sentiment = detect_sentiment(full_text)
        logger.info(f"Detected sentiment: {sentiment}")

        # Prepare the result object, converting float values to Decimal
        result = {
            'ObjectKey': image_key,
            'Status': status,
            'DetectedLabels': detected_labels,
            'DetectedTexts': detected_texts,
            'Sentiment': sentiment,  # New: Add sentiment to results
            'FullLabels': float_to_decimal(response_labels['Labels']),
            'FullTexts': float_to_decimal(response_text['TextDetections'])
        }

        # Store results in DynamoDB
        # TODO: Replace 'YOUR_TABLE_NAME' with your actual DynamoDB table name
        table = dynamodb.Table('YOUR_TABLE_NAME')
        table.put_item(Item=result)

        # Prepare and send SNS notification
        sns_message = (
            f"Analysis completed for image {image_key}.\n"
            f"Status: {status}\n"
            f"Detected labels: {', '.join(detected_labels)}\n"
            f"Detected texts: {', '.join(detected_texts)}\n"
            f"Sentiment: {sentiment}"
        )
        # TODO: Replace with your own SNS Topic ARN
        sns.publish(
            TopicArn='YOUR_SNS_TOPIC_ARN',
            Message=sns_message
        )

        return {
            'statusCode': 200,
            'body': json.dumps('Image analysis completed successfully!')
        }

    except Exception as e:
        logger.error(f"Error processing image {image_key}: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error in image analysis: {str(e)}')
        }