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
        logger.info("Executing event")
        try:
            sqs_queue = SQSQueue(self.dlq_queue, self.region_name)
            messages = sqs_queue.receive_messages_dlq(event)

            qtd_msg_capturadas = len(messages)
            
            if qtd_msg_capturadas == 0:
                logger.info("Não existem mensagens para extrair da DLQ orquestrador mensageria: Conteúdo vazio!")
                return {'message': 'No messages to process'}
            else:
                logging.info("Quantidade de mensagens capturadas: %s", str(qtd_msg_capturadas))
            
            response_list = []
            qtd_msg_processadas = 0
            logger.info(f"Processing message 01: {messages}")
            for msg in messages:
                logger.info(f"Processing message 02: {msg[0]}")
                msg_a_ser_processada = msg[0]
                logger.info(f"Processing message 03: {msg_a_ser_processada}")
                try:
                    logger.info(f"Processing message 04: {msg_a_ser_processada}")
                    dict_msg = json.loads(msg_a_ser_processada)
                    logger.info(f"Processing message 05: {dict_msg}")
                    response = self.process_message(dict_msg)
                    response_list.append(response)
                    logger.info("Mensagem reenviada para fila orquestrador com sucesso!")
                    qtd_msg_processadas += 1
                except Exception as ex:
                    logging.error("Erro ao processar a mensagem: %s", str(msg_a_ser_processada))
                    logging.error("Exception gerada: %s", str(ex))
            
            if qtd_msg_capturadas == qtd_msg_processadas:
                logging.info("Todas as mensagens capturadas foram processadas!")
            else:
                logging.error("Foram capturadas %s mensagens porém foram processadas %s", qtd_msg_capturadas, qtd_msg_processadas)
            
            return response_list
        
        except Exception as ex:
            logging.error("Erro no reprocessamento da mensagems para fila do orquestrador %s", str(ex))
            return {'error': str(ex)}


    def process_message(self, message):
        
        logger.info(f"Processing message: {message}")
        try:
            
            if not message.get(ATTEMPTS_KEY):
                message[ATTEMPTS_KEY] = 0
            
            attempts = message[ATTEMPTS_KEY]
            logger.info(f"processamento_tentativas: {attempts}")
            
            if attempts >= self.max_attempts:
                self.set_status(message, ERROR_STATUS, ERROR_MESSAGE)
                logger.info(f"processamento_status: {message[STATUS_KEY]}")
                logging.error(f"Máximo de retentativas alcançadas: {attempts}")
                self.cloudwatch.count("Máximo de retentativas alcançadas", 5)
                # self.dlq_queue.delete_message_dlq(receipt_handle)
            else:
                self.increment_attempts(message)
                logger.info(f"processamento_tentativas: {message[ATTEMPTS_KEY]}")
                self.set_status(message, REPROCESSING_STATUS)
                logger.info(f"processamento_status: {message[STATUS_KEY]}")
                logger.info(f"Send Message Sqs Queue: {self.original_queue_url}")
                self.send_to_aws_sqs(self.env, message)
                self.count_retry_metric(attempts)
                #self.dlq_queue.delete_message_dlq(receipt_handle)
            
            return {
                "message": "Mensagem reenviada para fila",
                "sqs": message
            }
        except Exception as ex:
            logging.error("Erro no reprocessamento da mensagem %s", str(ex))
            return {'error': str(ex)}

    def increment_attempts(self, message):
        message[ATTEMPTS_KEY] = message[ATTEMPTS_KEY] + 1


    def set_status(self, message, status, msg=None):
        message[STATUS_KEY] = status


    def send_to_aws_sqs(self, env, messagebody):
        send_to_sqs = SendToAwsSqs(env)
        logger.info(f"\n############   messagebody ############## : {messagebody}\n")
        messagetest = json.dumps(messagebody)
        logger.info(f"\n############ messagetest ############: {messagetest}\n")
        send_to_sqs.send_message_to_queue(json.dumps(messagetest))


    def count_retry_metric(self, attempts):
        self.cloudwatch.count("reprocessamento_quantidade", attempts)