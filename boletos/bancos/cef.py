# coding: utf-8

__author__ = 'maudhof@gmail.com'

from common import Boleto


class BoletoCEF(Boleto):
    banco = '104'

    carteira = 'SR'

    local_pagamento = u"PREFERENCIALMENTE NAS CASAS LOTÉRICAS ATÉ O VALOR LIMITE"

    prefixo_nosso_numero = '82'

    cedente_operacao = '003'

    def __init__(self, *args, **kwargs):

        if 'cedente_operacao' in kwargs:
            self.cedente_operacao = kwargs.pop('cedente_operacao')

        super(BoletoCEF, self).__init__(*args, **kwargs)

    def _cedente_agencia_codigo(self, formatado):
        code = [
            self.cedente_agencia.zfill(4)[:4],
            self.cedente_operacao.zfill(3)[:3],
            self.cedente_conta.zfill(8)[:8],
        ]

        if not formatado:
            return ''.join(code)

        code.append(self._modulo11(''.join(code)))

        return '%s.%s.%s-%s' % tuple(code)

    @property
    def nosso_numero_formatado(self):
        # output = '{:{fill}{align}10}'.format(self.nosso_numero, fill='0', align='>')

        self.prefixo_nosso_numero = str(self.prefixo_nosso_numero).ljust(2, '0')

        output = '%s%s' % (
            self.prefixo_nosso_numero,  #deve ter duas posicoes
            self.nosso_numero  #ja vem com 8 posicoes
        )

        return '%s-%s' % (output, self._modulo11(output))

    @property
    def cedente_agencia_codigo(self):
        return self._cedente_agencia_codigo(True)

    @property
    def banco_dv(self):
        return "%s-%s" % (
            self.banco,
            self._modulo11(self.banco)
        )

    @property
    def codigo_barras(self):
        barcode = [  # tam   descricao
                     self.banco,  # 3 - banco
                     self.moeda,  # 1 - código da moeda (9) real
                     str(self.fator_vencimento),  # 4 - fator vencimento
                     self.valor_digitavel,  #10 - valor documento
                     self.nosso_numero.zfill(10)[:10],  #10 - nosso numero (sem dv)
                     self._cedente_agencia_codigo(False)  #15 - Codigo beneficiario (sem dv)
        ]

        dv = self._modulo11(''.join(barcode))

        barcode.insert(5, str(dv))

        return ''.join(barcode)

    @property
    def linha_digitavel(self):
        barcode = self.codigo_barras

        #2 codigo do banco
        #1 moeda
        #5 posicao 20  a 25 do codigo de barras
        blk_1 = [
            self.banco,
            self.moeda,
            barcode[19:25],
        ]

        dv = str(self._modulo10(''.join(blk_1)))

        blk_1.append(dv)

        blk_1 = ''.join(blk_1)

        blk_2 = barcode[24:33]

        dv = str(self._modulo10(blk_2))

        blk_2 = '%s%s' % (blk_2, dv)

        blk_3 = barcode[34:43]

        dv = str(self._modulo10(blk_3))

        blk_3 = '%s%s' % (blk_3, dv)

        blk_4 = barcode[4]

        blk_5 = "%4s%10s" % (
            self.fator_vencimento,
            self.valor_digitavel,
        )

        return "%s.%s  %s.%s  %s.%s  %s  %s" % (
            blk_1[0:5],
            blk_1[5:],
            blk_2[0:5],
            blk_2[5:],
            blk_3[0:5],
            blk_3[5:],
            blk_4,
            blk_5
        )

    def _modulo11(self, num):
        resultado = self.__modulo_11_base__(num)
        if resultado > 9:
            return 0
        return resultado
