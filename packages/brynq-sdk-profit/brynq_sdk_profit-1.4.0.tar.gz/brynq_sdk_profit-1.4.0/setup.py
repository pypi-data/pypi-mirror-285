from setuptools import setup


setup(
    name='brynq_sdk_profit',
    version='1.4.0',
    description='Profit wrapper from BrynQ',
    long_description='Profit wrapper from BrynQ',
    author='BrynQ',
    author_email='support@brynq.com',
    packages=["brynq_sdk.profit"],
    license='BrynQ License',
    install_requires=[
        'brynq-sdk-brynq>=1',
        'brynq-sdk-functions>=0',
        'aiohttp>=3,<=4',
        'pandas>=1,<3',
        'requests>=2,<=3',
        'tenacity>=8,<9',
    ],
    zip_safe=False,
)
