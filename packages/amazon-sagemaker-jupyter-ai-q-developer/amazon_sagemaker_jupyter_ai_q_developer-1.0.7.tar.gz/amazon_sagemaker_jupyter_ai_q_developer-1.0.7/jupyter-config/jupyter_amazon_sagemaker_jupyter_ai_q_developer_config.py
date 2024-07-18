from sagemaker_jupyterlab_extension_common.identity import SagemakerIdentityProvider

c.AiExtension.default_language_model = "amazon-q:Q-Developer"
c.ServerApp.identity_provider_class = SagemakerIdentityProvider
