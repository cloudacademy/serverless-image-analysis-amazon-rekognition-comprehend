![Architecture Diagram](/images/architecture.png)

<h1 align="center">Building a Serverless Image Analysis Solution With Amazon Rekognition and Amazon Comprehend</h1>

<p align="center">
  <a href="https://cloudacademy.com/">
    <img src="https://img.shields.io/badge/-Start Lesson-blue" alt="">
  </a>
</p>

This serverless architecture integrates multiple AWS services to create an automated image analysis pipeline. The solution processes images, detects objects, extracts and analyzes text, and stores results without the need for server management.

## Architecture Overview

1. **Image Upload**: The process begins when an image is uploaded to a designated Amazon S3 bucket.

2. **Event Trigger**: S3 generates an event upon image upload, which triggers an AWS Lambda function.

3. **Image Analysis**: The Lambda function performs two main analysis tasks:
   - Uses Amazon Rekognition to detect specified objects and extract text from the image.
   - Uses Amazon Comprehend to analyze the sentiment of any extracted text.

4. **Data Storage**: Analysis results are stored in Amazon DynamoDB for persistence and easy retrieval.

5. **Notification**: Amazon SNS sends a notification containing a summary of the analysis results.

This event-driven architecture allows for automatic processing of images as they are uploaded, with results readily available for further use or review. The solution is scalable, processing images in parallel as needed, and cost-effective, utilizing resources only when processing occurs.

## Setup

1. Create a DynamoDB table named `ImageAnalysisResults` with partition key `ObjectKey` (String).
2. Create an SNS topic named `ImageAnalysisNotifications` and subscribe to it with your email.
3. Create a Lambda function using Python runtime.
4. Copy the Lambda function code from [image_analysis_lambda.py](image_analysis_lambda.py) into your function.
5. Update the Lambda function configuration:
   - Set the timeout to 1 minute
   - Attach policies: AmazonRekognitionFullAccess, AmazonDynamoDBFullAccess, AmazonSNSFullAccess, AmazonS3FullAccess, AmazonComprehendFullAccess
6. Create an S3 bucket with an `input` folder.
7. Set up an S3 event notification to trigger the Lambda function on file uploads to the `input` folder.

## Usage

1. Upload an image to the `input` folder of your S3 bucket.
2. The Lambda function will automatically process the image.
3. Check your email for the analysis notification.
4. View detailed results in the DynamoDB table.

## Customization

- Modify the `LABEL` variable in the Lambda function to detect different objects.
- Adjust analysis parameters as needed for your specific use case.

## Security Note

For production environments, apply the principle of least privilege by refining IAM permissions.

## Testing

Two test images are provided:
1. `plane.jpg`: Contains an airplane and neutral text.
2. `positive-image.jpg`: Contains a person and positive sentiment text.

To test with these images:
- For `plane.jpg`: Update the `LABEL` variable in the Lambda function to "airplane".
- For `positive-image.jpg`: Update the `LABEL` variable to "person".

After updating the `LABEL`, redeploy your Lambda function before uploading the corresponding test image to the S3 bucket. This ensures the function is looking for the correct object in each image.

Upload these images to test object detection and sentiment analysis capabilities.