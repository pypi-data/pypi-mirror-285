import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class CloudWatch:
    def __init__(self, env, nome_lambda, namespace, region_name='us-east-1'):
        self.env = env
        self.cloudwatch_resource = boto3.resource('cloudwatch', region_name=region_name)
        self.nome_lambda = nome_lambda
        self.namespace = namespace

    def put_metric_data(self, nome_metrica, dominio, valor, unidade, nome_arquivo=None):
        if self.env.env() == "TAAC":
            logger.info("Cloudwatch não executado - execução TAAC")
            return

        try:
            metric = self.cloudwatch_resource.Metric(self.namespace, 'Trigger_' + nome_metrica)
            dimensions = [
                {'Name': 'dominio', 'Value': dominio},
                {'Name': 'nome_arquivo', 'Value': nome_arquivo}
            ]

            if nome_arquivo is None:
                dimensions.pop(1)

            metric.put_data(
                Namespace=self.namespace,
                MetricData=[{
                    'MetricName': 'Trigger_' + nome_metrica,
                    'Value': valor,
                    'Unit': unidade,
                    'Dimensions': dimensions
                }]
            )
        except Exception as e:
            logger.error("Erro cloudwatch >> ", str(e))

    def count(self, nome_metrica, qtd):
        if self.env.env() == "TAAC":
            logger.info("Cloudwatch não executado - execução TAAC")
            return

        self.put_metric_data(nome_metrica=nome_metrica,
                             dominio=self.nome_lambda,
                             valor=qtd,
                             unidade='Count')