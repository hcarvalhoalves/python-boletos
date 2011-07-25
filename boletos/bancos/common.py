# coding: utf-8
from datetime import date, datetime, timedelta
from decimal import Decimal
import os
import sys


DATE_PARSE_FORMAT = '%d%m%y'
CURRENCY_PARSE_FORMAT = '%d.%d'

def _parse_date(s):
    try:
        return datetime.strptime(s, DATE_PARSE_FORMAT).date()
    except ValueError:
        return None

def _parse_currency(s):
    return Decimal(CURRENCY_PARSE_FORMAT % (int(s[:-2]), int(s[-2:])))

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
        self.nosso_numero = str(kwargs.pop('nosso_numero', 0)).zfill(8)[:8]
        self.numero_documento = kwargs.pop('numero_documento', 0)
        self.especie_documento = kwargs.pop('especie_documento', '')
        self.cedente = kwargs.pop('cedente', '')
        self.cedente_agencia = str(kwargs.pop('cedente_agencia', '')).zfill(4)[:4]
        self.cedente_conta = str(kwargs.pop('cedente_conta', '')).zfill(6)[:6]
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
        for i in range(len(str(num))-1, -1, -1):
            parcial = int(str(num)[i]) * peso
            if parcial > 9:
                parcial = int(str(parcial)[0]) + int(str(parcial)[1])
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
        for i in range(len(str(num))-1, -1, -1):
            parcial = int(str(num)[i]) * peso
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
        try:
            return (data_vencimento - self.data_base).days
        except TypeError:
            return (data_vencimento.date() - self.data_base).days

    @property
    def codigo_barras(self):
        raise NotImplementedError()


class CnabParsingError(Exception):
    pass


class CnabParser(object):

    def __init__(self, filename):
        with open(filename, 'r') as fd:
            self._parse(fd.readlines())

    def _parse(self, data):
        try:
            self.header = self._parse_header(data[0])
            self.transactions = self._parse_transactions(data[1:-1])
            self.trailer = self._parse_trailer(data[-1])
        except Exception, e:
            raise CnabParsingError(unicode(e)), None, sys.exc_info()[2]

    @staticmethod
    def _parse_header(h):
        return {
            'agencia': int(h[26:30]),
            'conta': int(h[33:38]),
            'data_geracao': _parse_date(h[94:100]),
            'data_credito': _parse_date(h[113:119]),
            'num_arquivo_retorno': int(h[108:113]),
        }

    def _parse_transactions(self, transactions):
        return [self._parse_transaction(t) for t in transactions]

    @staticmethod
    def _parse_transaction(t):
        return {
            'nosso_numero': int(t[62:70]),
            'carteira': int(t[82:85]),
            'valor_documento': _parse_currency(t[152:165]),
            'valor_tarifa': _parse_currency(t[175:188]),
            'valor_descontos': _parse_currency(t[240:253]),
            'valor_credito': _parse_currency(t[253:266]),
            'valor_juros': _parse_currency(t[266:279]),
            'data_vencimento': _parse_date(t[146:152]),
            'data_ocorrencia': _parse_date(t[110:116]),
            'data_credito': _parse_date(t[295:301]),
        }

    @staticmethod
    def _parse_trailer(t):
        return {
            'registros_total': int(t[212:220]),
            'valor_total_documento': _parse_currency(t[220:234]),
        }
