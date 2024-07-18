from setuptools import setup


setup(
    name='salure_helpers_brynq',
    version='2.0.0',
    description='Brynq Python SDK',
    long_description='Brynq Python SDK',
    author='D&A Salure',
    author_email='support@brynq.com',
    packages=["salure_helpers.brynq"],
    license='Brynq License',
    install_requires=[
        'requests>=2,<=3'
    ],
    zip_safe=False,
)
