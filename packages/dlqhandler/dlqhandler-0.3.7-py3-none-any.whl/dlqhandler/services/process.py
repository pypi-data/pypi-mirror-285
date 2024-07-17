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
        messages = sqs_queue.receive_messages_dlq(event)
        
        qtd_msg_capturadas = len(messages)
        if qtd_msg_capturadas == 0:
            logging.info("Não existem mensagens para extrair da DlQ orquestrador mensageria")
            return {'message': 'No messages to process'}
        else:
            logging.info(f"Quantidade de mensagens capturadas: {qtd_msg_capturadas}")

        for body, receipt_handle in messages:
            message = json.loads(body)
            logger.info(f"Processing message: {message}")

            if not receipt_handle.get(ATTEMPTS_KEY):
                receipt_handle[ATTEMPTS_KEY] = 0

            attempts = receipt_handle[ATTEMPTS_KEY]    

            logger.info(f"processamento_tentativas: {attempts}")
            if attempts > self.max_attempts:
                self.set_status(message, ERROR_STATUS, ERROR_MESSAGE)
                self.cloudwatch.count('maximo_reprocessamento_alcancada', attempts)
                #self.dlq_queue.delete_message_dlq(receipt_handle)
                logger.error(f"Máximo de retentativas alcançadas: {message}")
                
            else:
                logger.info(f"Mensagem para ser reprocessada: {message}")
                self.increment_attempts(receipt_handle)
                self.set_status(receipt_handle, REPROCESSING_STATUS)
                self.send_to_aws_sqs(self.env, message)
                self.count_retry_metric(message)

            #self.dlq_queue.delete_message_dlq(receipt_handle)

        return {
            'message': 'Mensagem reenviada para fila',
            'sqs': message
        }

    def increment_attempts(self, receipt_handle):
        receipt_handle[ATTEMPTS_KEY] = receipt_handle[ATTEMPTS_KEY] + 1

    def set_status(self, receipt_handle, status, msg=None):
        receipt_handle[STATUS_KEY] = status

    def send_to_aws_sqs(self, env, messagebody):
        send_to_sqs = SendToAwsSqs(env)
        send_to_sqs.send_message_to_queue(json.dumps(messagebody))

    def count_retry_metric(self, message):
        self.cloudwatch.count("reprocessamento_quantidade", 1)