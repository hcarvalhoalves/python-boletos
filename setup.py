# coding: utf-8
from setuptools import setup

setup(
    name = "python-boletos",
    version = "0.3.0",
    packages = ['boletos', 'boletos.bancos'],
    install_requires=['reportlab'],
    test_suite='boletos.tests.run_tests',
    include_package_data=True,
    zip_safe=False,
    author = "Henrique Carvalho Alves",
    author_email = "hcarvalhoalves@gmail.com",
    description = "Biblioteca para geração de boletos bancários com reportlab",
    url = "http://github.com/hcarvalhoalves/python-boletos",
)
