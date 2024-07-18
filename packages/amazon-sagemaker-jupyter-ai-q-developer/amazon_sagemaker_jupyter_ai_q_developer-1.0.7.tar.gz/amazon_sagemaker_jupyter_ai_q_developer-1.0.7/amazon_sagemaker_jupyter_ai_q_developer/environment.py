import json
import logging

from amazon_sagemaker_jupyter_ai_q_developer.sagemaker_client import get_sagemaker_client

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)


class Environment:
    SM_STUDIO_SSO = "SageMaker Studio SSO"
    MD = "MD"
    _cached_env = None

    @staticmethod
    def get_environment():
        if Environment._cached_env is None:
            logging.info("Detecting environment for the first time")
            Environment._cached_env = Environment._detect_environment()
        logging.info(f"Environment is {Environment._cached_env}")
        return Environment._cached_env

    @staticmethod
    def _detect_environment():
        env = ''
        try:
            with open('/opt/ml/metadata/resource-metadata.json', 'r') as f:
                data = json.load(f)
                if 'AdditionalMetadata' in data and 'DataZoneScopeName' in data['AdditionalMetadata']:
                    env = Environment.MD
                elif 'ResourceArn' in data:
                    sm_domain_id = data['DomainId']
                    logging.info(f"DomainId - {sm_domain_id}")
                    sm_client = get_sagemaker_client()
                    domain_details = sm_client.describe_domain(sm_domain_id)
                    logging.debug(f"Studio domain level details: {domain_details}")
                    if (domain_details.get('AuthMode') == "SSO"
                            and (domain_details.get('DomainSettings') is not None
                                    and domain_details.get('DomainSettings').get('AmazonQSettings') is not None
                                    and domain_details.get('DomainSettings').get('AmazonQSettings').get('Status') == 'ENABLED')):
                        env = Environment.SM_STUDIO_SSO
        except Exception as e:
            logging.error(f"Error detecting environment: {str(e)}")
        return env
