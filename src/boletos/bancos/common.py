# coding: utf-8
from datetime import date, datetime, timedelta
import os

def _split_lines(s):
    return filter(None, map(lambda l: l.strip(' '), s.split('\n')))


class Boleto(object):
    banco = None
    carteira = None
    aceite = "N"
    especie = "R$"
    moeda = "9"
    quantidade = ""
    data_base = date(1997, 10, 7)
    local_pagamento = u"Pagável em qualquer banco até o vencimento."

    def __init__(self, *args, **kwargs):
        self.valor_documento = kwargs.pop('valor_documento', 0)
        self.nosso_numero = kwargs.pop('nosso_numero', 0).zfill(8)[:8]
        self.numero_documento = kwargs.pop('numero_documento', 0)
        self.especie_documento = kwargs.pop('especie_documento', '')
        self.cedente = kwargs.pop('cedente', '')
        self.cedente_agencia = kwargs.pop('cedente_agencia', '').zfill(4)[:4]
        self.cedente_conta = kwargs.pop('cedente_conta', '').zfill(6)[:6]
        self.data_vencimento = kwargs.pop('data_vencimento', date.today() + timedelta(weeks=1))
        if isinstance(self.data_vencimento, datetime):
            self.data_vencimento = self.data_vencimento.date()
        self.data_documento = kwargs.pop('data_documento', date.today())
        if isinstance(self.data_documento, datetime):
            self.data_documento = self.data_documento.date()
        self.data_processamento = kwargs.pop('data_processamento', date.today())
        if isinstance(self.data_processamento, datetime):
            self.data_processamento = self.data_processamento.date()
        self.demonstrativo = _split_lines(kwargs.pop('demonstrativo', u"")) # 12 lines, 90 cols
        self.instrucoes = _split_lines(kwargs.pop('instrucoes', u"")) # 7 lines, 90 cols
        self.sacado = _split_lines(kwargs.pop('sacado', "")) # 3 lines, 80 cols

    def _modulo10(self, num):
        soma = 0
        peso = 2
        for i in range(len(num)-1, -1, -1):
            parcial = int(num[i]) * peso
            if parcial > 9:
                s = "%d" % parcial
                parcial = int(s[0]) + int(s[1])
            soma += parcial
            if peso == 2:
                peso = 1
            else:
                peso = 2
        resto10 = soma % 10
        if resto10 == 0:
            modulo10 = 0
        else:
            modulo10 = 10 - resto10
        return modulo10

    def _modulo11(self, num):
        soma = 0
        peso = 2
        for i in range(len(num)-1, -1, -1):
            parcial = int(num[i]) * peso
            soma += parcial
            if peso == 9:
                peso = 2
            else:
                peso += 1
        resto11 = soma % 11
        if resto11 == 0 or resto11 == 1:
            modulo11 = 1
        else:
            modulo11 = 11 - resto11
        return modulo11

    @property
    def logo_path(self):
        base_location = os.path.dirname(__file__)
        return os.path.join(base_location, 'media/%s.gif' % self.banco)

    @property
    def valor_digitavel(self):
        return ("%.2f" % self.valor_documento).replace('.', '').zfill(10)

    @property
    def nosso_numero_formatado(self):
        raise NotImplementedError()

    @property
    def banco_dv(self):
        raise NotImplementedError()

    @property
    def cedente_agencia_codigo(self):
        raise NotImplementedError()

    @property
    def linha_digitavel(self):
        raise NotImplementedError()

    @property
    def fator_vencimento(self):
        return (self.data_vencimento - self.data_base).days

    @property
    def codigo_barras(self):
        raise NotImplementedError()