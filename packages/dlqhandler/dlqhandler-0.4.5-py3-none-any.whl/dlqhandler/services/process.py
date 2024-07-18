import json
import logging
from dlqhandler.dataprovider.send_to_aws_sqs import SendToAwsSqs
from .cloudwatch import CloudWatch
from dlqhandler.dataprovider.sqs_queue import SQSQueue

ERROR_STATUS = "ERRO"
ERROR_MESSAGE = "Número de retentativas excedido"
REPROCESSING_STATUS = "REPROCESSANDO"
ATTEMPTS_KEY = "processamento_tentativas"
STATUS_KEY = "processamento_status"
MESSAGE_KEY = "processamento_mensagem"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class ProcessMessage:
    def __init__(self, dlq_queue_url, original_queue_url, max_attempts=5, region_name='us-east-1', env=None, 
                 nome_lambda='lambda-reprocessamento-dlq', namespace='DLQ-Mensageria'):
        self.dlq_queue = dlq_queue_url
        self.original_queue_url = original_queue_url
        self.max_attempts = max_attempts
        self.region_name = region_name
        self.cloudwatch = CloudWatch(env, nome_lambda, namespace)
        self.env = env

    def execute(self, event):
        logging.info("Executing event")
        
        sqs_queue = SQSQueue(self.dlq_queue, self.region_name)
        messages_from_dlq = sqs_queue.receive_messages_dlq(event)
        
        messages = event.get('Records', [])
        if messages_from_dlq:
            messages.extend(messages_from_dlq)

        qtd_msg_capturadas = len(messages)
        if qtd_msg_capturadas == 0:
            logging.info("Não existem mensagens para extrair da DLQ orquestrador mensageria")
            return {'message': 'No messages to process'}
        else:
            logging.info(f"Quantidade de mensagens capturadas: {qtd_msg_capturadas}")    

        for message in messages:
            body = json.loads(message.get('body'))
            logging.info(f"Processing message: {body}")
            attributes = message.get('attributes')

            if not attributes.get(ATTEMPTS_KEY):
                attributes[ATTEMPTS_KEY] = 0

            attempts = attributes[ATTEMPTS_KEY]
            logging.info(f"processamento_tentativas: {attempts}")

            if attempts > self.max_attempts:
                self.set_status(attributes, ERROR_STATUS, ERROR_MESSAGE)
                logging.info(f"processamento_status: {attributes[STATUS_KEY]}")
                self.cloudwatch.count(ERROR_MESSAGE, attempts)
                # self.dlq_queue.delete_message_dlq(receipt_handle)
                logging.info(f"Máximo de retentativas alcançadas: {message}")
            else:
                logging.info(f"Mensagem para ser reprocessada: {message}")
                self.increment_attempts(attributes)
                logging.info(f"processamento_tentativas: {attempts}")
                self.set_status(attributes, REPROCESSING_STATUS)
                logging.info(f"processamento_status: {attributes[STATUS_KEY]}")
                self.send_to_aws_sqs(self.env, message)
                logging.info(f"Send Message Sqs Queue: {self.original_queue_url}")
                self.count_retry_metric(attempts)

            #self.dlq_queue.delete_message_dlq(receipt_handle)

        return {
            'message': 'Mensagem reenviada para fila',
            'sqs': message
        }

    def increment_attempts(self, attributes):
        attributes[ATTEMPTS_KEY] = attributes[ATTEMPTS_KEY] + 1

    def set_status(self, attributes, status, msg=None):
        attributes[STATUS_KEY] = status

    def send_to_aws_sqs(self, env, messagebody):
        send_to_sqs = SendToAwsSqs(env)
        send_to_sqs.send_message_to_queue(json.dumps(messagebody))

    def count_retry_metric(self, attempts):
        self.cloudwatch.count("reprocessamento_quantidade", attempts)