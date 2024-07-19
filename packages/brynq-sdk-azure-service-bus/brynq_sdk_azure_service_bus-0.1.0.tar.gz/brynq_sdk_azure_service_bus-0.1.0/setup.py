from setuptools import setup

setup(
    name='brynq_sdk_azure_service_bus',
    version='0.1.0',
    description='Azure Service Bus wrapper from BrynQ',
    long_description='Azure Service Bus wrapper from BrynQ',
    author='BrynQ',
    author_email='support@brynq.com',
    packages=["brynq_sdk.azure_service_bus"],
    license='BrynQ License',
    install_requires=[
        'brynq-sdk-brynq>=1',
        'pandas>=2,<3',
        'azure-servicebus>=7.12',
        'pandas>=1,<3'
    ],
    zip_safe=False,
)
