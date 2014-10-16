# coding: utf-8
__author__ = 'mauricio'


from ..bancos import cef
from ..render import render_to_pdf, render_to_png, render_to_jpg
from datetime import date
from decimal import Decimal
import unittest
import os



CAIXA_BOLETO = {
    'valor_documento': 1234.56,
    'nosso_numero': "00001001",
    'numero_documento': "00001",
    'data_vencimento': date(2014, 5, 31),
    'cedente': 'Emprese Teste Ltda',
    'cedente_agencia': 1234,
    'cedente_conta': 12345,
    'instrucoes': u"""
    Cobrar multa de 2% após o vencimento.
    Não receber após 30 dias da data de vencimento.
    """,
    'demonstrativo': u"""
    Teste Teste  Teste Teste Teste Teste Teste Teste
    """,
    'sacado': u"""
    Cliente
    Av. Paulista, 10 - Centro - São Paulo - CEP 00001-010
    """,
}

CODIGO_DE_BARRAS = '10491608000001234568200001001123400300012345'
#                       |-> DV = 1


class BoletoItauValidationTest(unittest.TestCase):

    def setUp(self):
        self.boleto = cef.BoletoCEF(**CAIXA_BOLETO)

    def test_valor_digitavel(self):
        self.assertEqual(self.boleto.valor_digitavel, '0000123456')

    def test_cedente_agencia_codigo(self):
        self.assertEqual(self.boleto.cedente_agencia_codigo, '1234.003.00012345-5')

    def test_nosso_numero(self):
        self.assertEqual(self.boleto.nosso_numero_formatado, '820001001-3')

    def test_linha_digitavel(self):

        blk_1 = '%s%s' % (CODIGO_DE_BARRAS[0:3], CODIGO_DE_BARRAS[19:23])
        blk_2 = CODIGO_DE_BARRAS[24:33]
        blk_3 = CODIGO_DE_BARRAS[34:43]
        blk_4 = CODIGO_DE_BARRAS[4]

        blk_5 = '%s%s'  % ( CODIGO_DE_BARRAS[5:8], CODIGO_DE_BARRAS[9:18].zfill(14))

        linha_digitavel = '%s.%s %s.%s %s.%s %s %s' % (
            blk_1[:5], blk_1[6:],
            blk_2[:5], blk_2[6:],
            blk_3[:5], blk_3[6:],
            blk_4,
            blk_5
        )

        self.assertEqual(self.boleto.linha_digitavel, linha_digitavel)

    def test_codigo_barras(self):

        #10491608000001234568200001001123400300012345
        #    |-> DV = 1

        self.assertEqual(len(self.boleto.codigo_barras), 44)

        self.assertEqual(self.boleto.codigo_barras, '10491608000001234568200001001123400300012345')


class RenderTest(object):
    def _test_render(self, method, filename):
        fmt_filename = filename % self.boleto.__class__.__name__
        with open(fmt_filename, 'wb') as f:
            f.write(method(self.boleto).getvalue())

    def test_render_to_pdf(self):
        self._test_render(render_to_pdf, '/tmp/%s-cef-test.pdf')

    def test_render_to_png(self):
        self._test_render(render_to_png, '/tmp/%s-cef-test.png')

    def test_render_to_jpg(self):
        self._test_render(render_to_jpg, '/tmp/%s-cef-test.jpg')


class BoletoCaixaRenderTest(RenderTest, unittest.TestCase):
    def setUp(self):
        self.boleto = cef.BoletoCEF(**CAIXA_BOLETO)


if __name__ == '__main__':
    unittest.main()
