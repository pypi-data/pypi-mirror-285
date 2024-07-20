import json
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class SendToAwsSqs:
    def __init__(self, env):
        self.env = env

    def send_message_to_queue(self, messagebody):
        try:
            logger.info("enviar_mensagem_sqs >> %s", json.loads(messagebody))
            
            sqs_link = self.env.url_sqs_orquestrador()
            session = boto3.Session()
            sqs = session.client(service_name="sqs")

            if self.env != "TAAC":
                sqs.send_message(
                    QueueUrl=sqs_link,
                    MessageBody=messagebody
                )

            return {
                "sucesso": True,
                "sqs": json.loads(messagebody)
            }
        except Exception as e:
            logger.error("Erro reenviar mensagem para fila orquestrador >> %s", str(e))
            raise e