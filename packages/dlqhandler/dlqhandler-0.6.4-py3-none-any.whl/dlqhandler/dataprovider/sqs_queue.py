import boto3
import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class SQSQueue:
    def __init__(self, queue_url, region_name='us-east-1'):
        self.queue_url = queue_url
        self.session = boto3.Session()
        self.sqs_client = boto3.client("sqs", region_name=region_name)

    def receive_messages_dlq(self, event=None, max_number=10, wait_time=0):
        try:
            logger.info('Starting to read messages from the queue')
            
            messages = self.sqs_client.receive_message(
                QueueUrl=self.queue_url,
                AttributeNames=['All'],
                MaxNumberOfMessages=max_number,
                WaitTimeSeconds=wait_time
            )

            logger.info('\nReceived messages: %s\n', messages)

            if 'Messages' not in messages:
                if not event.get('Records'):
                    logger.info('No messages to retrieve from SQS: Empty content')
                    return []
                else:
                    messages = event
                    logger.info('\nReceived messages event: %s\n', messages)
                    return [(msg['body'], msg['attributes']) for msg in messages['Records']]

            return [(msg['Body'], msg['ReceiptHandle']) for msg in messages['Messages']]
        
        except Exception as e:
            logger.exception("Error receiving messages: %s", e)
            return []

    def delete_message_dlq(self, receipt_handle):
        try:
            self.sqs_client.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle
            )
            logger.info(f"Message with receipt handle {receipt_handle} deleted successfully.")
        except Exception as e:
            logger.exception("Error deleting message: %s", e)
            raise e