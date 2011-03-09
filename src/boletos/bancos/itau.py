# coding: utf-8
from common import Boleto


class BoletoItau(Boleto):
    banco = "341"
    carteira = "175"
    local_pagamento = u"Até o vencimento pague preferencialmente no Itaú"

    def _dac_nosso_numero(self):
        num = "%s%s%s%s" % (
            self.cedente_agencia,
            self.cedente_conta[:-1],
            self.carteira,
            self.nosso_numero,
        )
        return self._modulo10(num)

    def _dac_codigo_barras(self):
        num = "%3s%1s%4s%10s%3s%8s%1s%4s%6s000" % (
            self.banco,
            self.moeda,
            self.fator_vencimento,
            self.valor_digitavel,
            self.carteira,
            self.nosso_numero,
            self._dac_nosso_numero(),
            self.cedente_agencia,
            self.cedente_conta,
        )
        return self._modulo11(num)

    @property
    def cedente_agencia_codigo(self):
        return "%s/%s-%s" % (
            self.cedente_agencia,
            self.cedente_conta[:-1],
            self.cedente_conta[-1:]
        )

    @property
    def nosso_numero_formatado(self):
        return "%s/%s-%s" % (
            self.carteira,
            self.nosso_numero,
            self._dac_nosso_numero()
        )

    @property
    def banco_dv(self):
        return "%s-%s" % (
            self.banco,
            self._modulo11(self.banco)
        )

    @property
    def linha_digitavel(self):
        bloco1 = "%3s%1s%3s%2s" % (
            self.banco,
            self.moeda,
            self.carteira,
            self.nosso_numero[:2],
        )
        bloco1dv = self._modulo10(bloco1)

        bloco2 = "%6s%1s%3s" % (
            self.nosso_numero[2:],
            self._dac_nosso_numero(),
            self.cedente_agencia[0:3],
        )
        bloco2dv = self._modulo10(bloco2)

        bloco3 = "%1s%6s000" % (
            self.cedente_agencia[3:],
            self.cedente_conta,
        )
        bloco3dv = self._modulo10(bloco3)

        bloco4 = self._dac_codigo_barras()

        bloco5 = "%4s%10s" % (
            self.fator_vencimento,
            self.valor_digitavel,
        )

        return "%s.%s%s  %s.%s%s  %s.%s%s  %s  %s" % (
            bloco1[0:5],
            bloco1[5:],
            bloco1dv,
            bloco2[0:5],
            bloco2[5:],
            bloco2dv,
            bloco3[0:5],
            bloco3[5:],
            bloco3dv,
            bloco4,
            bloco5,
        )

    @property
    def codigo_barras(self):
        return "%3s%1s%1s%4s%10s%3s%8s%1s%4s%6s000" % (
            self.banco,
            self.moeda,
            self._dac_codigo_barras(),
            self.fator_vencimento,
            self.valor_digitavel,
            self.carteira,
            self.nosso_numero,
            self._dac_nosso_numero(),
            self.cedente_agencia,
            self.cedente_conta,
        )
