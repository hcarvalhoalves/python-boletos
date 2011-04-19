# coding: utf-8
import unittest
from datetime import date


ITAU_TEST_DATA = {
    'valor_documento': 64.00,
    'nosso_numero': "00001001",
    'numero_documento': "00001",
    'data_vencimento': date(2011, 6, 1),
    'cedente': 'Rede Colibri Desenvolvimento e Serviços de Internet LTDA',
    'cedente_agencia': '8450',
    'cedente_conta': '091874',
    'instrucoes': u"""
    Cobrar multa de 2% após o vencimento.
    Não receber após 30 dias da data de vencimento.
    """,
    'demonstrativo': u"""
    Rede Colibri (Plano Imobiliária R$ 64,00)
    """,
    'sacado': u"""
    Cliente
    Av. Paulista, 10 - Centro - São Paulo - CEP 00001-010
    """,
}


class BoletoItauValidationTest(unittest.TestCase):

    def setUp(self):
        from boletos.bancos import itau
        self.boleto = itau.BoletoItau(**ITAU_TEST_DATA)

    def test_valor_digitavel(self):
        self.assertEqual(
            self.boleto.valor_digitavel, '0000006400'
        )

    def test_cedente_agencia_codigo(self):
        self.assertEqual(
            self.boleto.cedente_agencia_codigo, '8450/09187-4'
        )

    def test_nosso_numero(self):
        self.assertEqual(
            self.boleto.nosso_numero_formatado, '175/00001001-2'
        )

    def test_linha_digitavel(self):
        self.assertEqual(
            self.boleto.linha_digitavel,
            '34191.75009  00100.128453  00918.740002  3  49850000006400'
        )

    def test_codigo_barras(self):
        self.assertEqual(
            len(self.boleto.codigo_barras), 44
        )
        self.assertEqual(
            self.boleto.codigo_barras,
            '34193498500000064001750000100128450091874000'
        )


class RenderTest(object):
    def _test_render(self, method, filename):
        fmt_filename = filename % self.boleto.__class__.__name__
        with open(fmt_filename, 'wb') as f:
            f.write(method(self.boleto).getvalue())

    def test_render_to_pdf(self):
        from boletos.render import render_to_pdf
        self._test_render(render_to_pdf, '/tmp/%s-test.pdf')

    def test_render_to_png(self):
        from boletos.render import render_to_png
        self._test_render(render_to_png, '/tmp/%s-test.png')

    def test_render_to_jpg(self):
        from boletos.render import render_to_jpg
        self._test_render(render_to_jpg, '/tmp/%s-test.jpg')


class BoletoItauRenderTest(RenderTest, unittest.TestCase):
    def setUp(self):
        from boletos.bancos import itau
        self.boleto = itau.BoletoItau(**ITAU_TEST_DATA)


if __name__ == '__main__':
    unittest.main()
