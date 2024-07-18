from setuptools import setup

setup(
    name='brynq_sdk_visma_lon_hr',
    version='0.1.0',
    description='Visma Lon & HR wrapper from BrynQ',
    long_description='Visma Lon & HR wrapper from BrynQ',
    author='BrynQ',
    author_email='support@brynq.com',
    packages=["brynq_sdk.visma_lon_hr"],
    license='BrynQ License',
    install_requires=[
        'brynq-sdk-brynq>=1',
        'pandas>=2,<3'
    ],
    zip_safe=False,
)
