# coding: utf-8
from setuptools import setup

setup(
    name = "python-boletos",
    version = "0.2.1",
    package_dir = {'boletos': 'src/boletos'},
    packages = ['boletos', 'boletos.bancos'],
    include_package_data=True,
    install_requires=['reportlab'],
    zip_safe=False,
    author = "Henrique Carvalho Alves",
    author_email = "hcarvalhoalves@gmail.com",
    description = "Biblioteca para geração de boletos bancários com reportlab",
    url = "http://github.com/hcarvalhoalves/python-boletos",
)
