# coding: utf-8
from common import Boleto


class BoletoBancoReal(Boleto):
    banco = "356"
    carteira = "57"

    def _digitao_cobranca(self):
        num = "%s%s%s" % (self.nosso_numero, self.cedente_agencia, self.cedente_conta)
        return self._modulo10(num)

    def _digitao_codigo_barras(self):
        num = "%3s%1s%4s%10s%4s%7s%1s%13s" % (
            self.banco,
            self.moeda,
            self.fator_vencimento,
            self.valor_digitavel,
            self.cedente_agencia,
            self.cedente_conta,
            self._digitao_cobranca(),
            self.nosso_numero,
        )
        return self._modulo11(num)

    @property
    def cedente_agencia_codigo(self):
        dv = self._digitao_cobranca()
        return "%s/%s-%s" % (self.cedente_agencia, self.cedente_conta, dv)

    @property
    def banco_dv(self):
        return "%s-%s" % (self.banco, self._modulo11(self.banco))

    @property
    def linha_digitavel(self):
        bloco1 = "%3s%1s%1s%3s%1s" % (
            self.banco,
            self.moeda,
            self.cedente_agencia[0],
            self.cedente_agencia[1:],
            self.cedente_conta[0]
        )
        bloco1dv = self._modulo10(bloco1)

        bloco2 = "%6s%1s%3s" % (
            self.cedente_conta[1:],
            self._digitao_cobranca(),
            self.nosso_numero[0:3]
        )
        bloco2dv = self._modulo10(bloco2)

        bloco3 = "%10s" % (
            self.nosso_numero[3:]
        )
        bloco3dv = self._modulo10(bloco3)

        bloco4 = self._digitao_codigo_barras()

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
        return "%3s%1s%1s%4s%10s%4s%7s%1s%13s" % (
            self.banco,
            self.moeda,
            self._digitao_codigo_barras(),
            self.fator_vencimento,
            self.valor_digitavel,
            self.cedente_agencia,
            self.cedente_conta,
            self._digitao_cobranca(),
            self.nosso_numero,
        )
