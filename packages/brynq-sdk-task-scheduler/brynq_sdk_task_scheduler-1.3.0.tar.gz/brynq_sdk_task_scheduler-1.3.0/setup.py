from setuptools import setup


setup(
    name='brynq_sdk_task_scheduler',
    version='1.3.0',
    description='Code to execute tasks in BrynQ.com with the task scheduler',
    long_description='Code to execute tasks in the BrynQ.com platform with the task scheduler',
    author='BrynQ',
    author_email='support@brynq.com',
    packages=["brynq_sdk.task_scheduler"],
    license='BrynQ License',
    install_requires=[
        'brynq-sdk-brynq>=1',
        'brynq-sdk-functions>=1',
        'brynq-sdk-mysql>=1',
        'brynq-sdk-mandrill>=1',
        'brynq-sdk-elastic>=2'
    ],
    zip_safe=False,
)