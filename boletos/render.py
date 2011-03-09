# coding: utf-8
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from reportlab.pdfgen import canvas
from reportlab.lib import pagesizes
from reportlab.lib.units import mm
from reportlab.lib.colors import black
from reportlab.graphics.barcode import createBarcodeDrawing

import subprocess

GHOSTSCRIPT_COMMAND = """
gs -q -dBATCH -dNOPAUSE -sDEVICE=%s -r300 -sOutputFile=- -
"""

DATE_FORMAT = "%d/%m/%Y"


def _date_format(date):
    return date.strftime(DATE_FORMAT)


def _price_format(value):
    return ("%.2f" % value).replace('.', ',')


class BoletoLayout(object):

    def __init__(self, boleto, file, pagesize=pagesizes.A4):
        self.boleto = boleto
        self.file = file
        self.width = 190 * mm
        self.heightLine = 6.5 * mm
        self.space = 2
        self.fontSizeTitle = 6
        self.fontSizeValue = 9
        self.deltaTitle = self.heightLine - (self.fontSizeTitle + 1)
        self.deltaFont = self.fontSizeValue + 1
        self.canvas = canvas.Canvas(file, pagesize=pagesize)
        self.canvas.setStrokeColor(black)

    def _barcode(self, num, x, y):
        barcode = createBarcodeDrawing('I2of5', value=num,
                                       width=110*mm, height=13*mm, ratio=3.0,
                                       checksum=False, bearers=False)
        barcode.drawOn(self.canvas, x, y)

    def _horizontal_line(self, x, y, width):
        self.canvas.line(x, y, x + width, y)

    def _vertical_line(self, x, y, width):
        self.canvas.line(x, y, x, y + width)

    def _centre_text(self, x, y, text):
        self.canvas.drawCentredString(self.refX + x, self.refY + y, text)

    def _right_text(self, x, y, text):
        self.canvas.drawRightString(self.refX + x, self.refY + y, text)

    def _recibo(self, x, y):
        self.canvas.saveState()
        self.canvas.translate(x * mm, y * mm)

        linhaInicial = 16

        # Horizontal Lines
        self.canvas.setLineWidth(1)
        self._horizontal_line(0, linhaInicial * self.heightLine, self.width)
        self._horizontal_line(0, (linhaInicial + 1) * self.heightLine, self.width)
        self.canvas.setLineWidth(2)
        self._horizontal_line(0, (linhaInicial + 2) * self.heightLine, self.width)

        # Vertical Lines
        self.canvas.setLineWidth(1)
        self._vertical_line(self.width - (45 * mm), (linhaInicial + 0) * self.heightLine, 2 * self.heightLine)
        self._vertical_line(self.width - (45 * mm) - (30 * mm), (linhaInicial + 0) * self.heightLine, 2 * self.heightLine)
        self._vertical_line(self.width - (45 * mm) - (30 * mm) - (30*mm), (linhaInicial + 0) * self.heightLine, 2 * self.heightLine)

        # Head
        self.canvas.setLineWidth(2)
        self._vertical_line(40*mm, (linhaInicial + 2) * self.heightLine, self.heightLine)
        self._vertical_line(60*mm, (linhaInicial + 2) * self.heightLine, self.heightLine)

        logo = self.boleto.logo_path
        if logo:
            self.canvas.drawImage(logo, 0, (linhaInicial + 2) * self.heightLine + 3, 60*mm, 10*mm, preserveAspectRatio=True, anchor='sw')
        self.canvas.setFont('Helvetica-Bold', 18)
        self.canvas.drawCentredString(50*mm, (linhaInicial + 2) * self.heightLine + 3, self.boleto.banco_dv)
        self.canvas.setFont('Helvetica-Bold', 10)
        self.canvas.drawRightString(self.width, (linhaInicial + 2) * self.heightLine + 3, 'Recibo do Sacado')

        # Titles
        self.canvas.setFont('Helvetica', 6)
        self.deltaTitle = self.heightLine - (6 + 1)

        self.canvas.drawString(0, (((linhaInicial + 1)*self.heightLine)) + self.deltaTitle, 'Cedente')
        self.canvas.drawString(self.width - (45 * mm) - (30 * mm) - (30 * mm) + self.space, (((linhaInicial + 1) * self.heightLine)) + self.deltaTitle, 'Agência/Código Cedente')
        self.canvas.drawString(self.width - (45 * mm) - (30 * mm) + self.space, (((linhaInicial + 1)*self.heightLine)) + self.deltaTitle, 'Data Documento')
        self.canvas.drawString(self.width - (45 * mm) + self.space, (((linhaInicial + 1)*self.heightLine)) + self.deltaTitle, 'Vencimento')

        self.canvas.drawString(0, (((linhaInicial + 0)*self.heightLine)) + self.deltaTitle, 'Sacado')
        self.canvas.drawString(self.width - (45 * mm) - (30 * mm) - (30 * mm) + self.space, (((linhaInicial + 0) * self.heightLine)) + self.deltaTitle, 'Nosso Número')
        self.canvas.drawString(self.width - (45 * mm) - (30 * mm) + self.space, (((linhaInicial + 0)*self.heightLine)) + self.deltaTitle, 'N. do documento')
        self.canvas.drawString(self.width - (45 * mm) + self.space, (((linhaInicial + 0)*self.heightLine)) + self.deltaTitle, 'Valor Documento')

        self.canvas.drawString(0, (((linhaInicial - 1) * self.heightLine)) + self.deltaTitle, 'Demonstrativo')
        self.canvas.drawRightString(self.width, (((linhaInicial - 1) * self.heightLine)) + self.deltaTitle, 'Autenticação Mecânica')

        # Values
        self.canvas.setFont('Helvetica', 9)
        heighFont = 9 + 1

        self.canvas.drawString(0 + self.space, (((linhaInicial + 1) * self.heightLine)) + self.space, self.boleto.cedente)
        self.canvas.drawString(self.width - (45 * mm) - (30 * mm) - (30 * mm) + self.space, (((linhaInicial + 1) * self.heightLine)) + self.space, self.boleto.cedente_agencia_codigo)
        self.canvas.drawString(self.width - (45 * mm) - (30 * mm) + self.space, (((linhaInicial + 1)*self.heightLine)) + self.space,  _date_format(self.boleto.data_documento))
        self.canvas.drawString(self.width - (45 * mm) + self.space, (((linhaInicial + 1) * self.heightLine)) + self.space,  _date_format(self.boleto.data_vencimento))

        valorDocumento = _price_format(self.boleto.valor_documento)

        self.canvas.drawString(0 + self.space, (((linhaInicial + 0) * self.heightLine)) + self.space, self.boleto.sacado[0])
        self.canvas.drawString(self.width - (45 * mm) - (30 * mm) - (30 * mm) + self.space, (((linhaInicial + 0) * self.heightLine)) + self.space, self.boleto.nosso_numero_formatado)
        self.canvas.drawString(self.width - (45 * mm) - (30 * mm) + self.space, (((linhaInicial + 0) * self.heightLine)) + self.space, self.boleto.numero_documento)
        self.canvas.drawString(self.width - (45 * mm) + self.space, (((linhaInicial + 0) * self.heightLine)) + self.space, valorDocumento)

        for l in self.boleto.demonstrativo:
            self.canvas.drawString(2 * self.space, (((linhaInicial - 1) * self.heightLine)) - (self.boleto.demonstrativo.index(l) * heighFont), l)

        self.canvas.restoreState()

    def _ficha(self, x, y):
        self.canvas.saveState()

        self.canvas.translate(x*mm, y*mm)

        # De baixo para cima posicao 0,0 esta no canto inferior esquerdo
        self.canvas.setFont('Helvetica', self.fontSizeTitle)

        y = 1.5*self.heightLine
        self.canvas.drawRightString(self.width, (1.5*self.heightLine)+self.deltaTitle-1, 'Autenticação Mecânica / Ficha de Compensação')

        # Primeira linha depois do codigo de barra
        y += self.heightLine
        self.canvas.setLineWidth(2)
        self._horizontal_line(0, y, self.width)
        self.canvas.drawString(self.width - (45*mm) + self.space, y+self.space, 'Código de Baixa')
        self.canvas.drawString(0, y + self.space, 'Sacador / Avalista')

        y += self.heightLine
        self.canvas.drawString(0, y + self.deltaTitle, 'Sacado')

        # Linha grossa dividindo o Sacado
        y += self.heightLine
        self.canvas.setLineWidth(2)
        self._horizontal_line(0, y, self.width)
        self.canvas.setFont('Helvetica', self.fontSizeValue)

        for l in self.boleto.sacado:
            self.canvas.drawString(15*mm, (y - 10) - (self.boleto.sacado.index(l) * self.deltaFont), l)
        self.canvas.setFont('Helvetica', self.fontSizeTitle)


        # Linha vertical limitando todos os campos da direita
        self.canvas.setLineWidth(1)
        self._vertical_line(self.width - (45*mm), y, 9 * self.heightLine)
        self.canvas.drawString(self.width - (45*mm) + self.space, y + self.deltaTitle, '(=) Valor cobrado')


        # Campos da direita
        y += self.heightLine
        self._horizontal_line(self.width - (45*mm), y, 45*mm)
        self.canvas.drawString(self.width - (45*mm) + self.space, y + self.deltaTitle, '(+) Outros acréscimos')

        y += self.heightLine
        self._horizontal_line(self.width - (45*mm), y, 45*mm)
        self.canvas.drawString(self.width - (45*mm) + self.space, y + self.deltaTitle, '(+) Mora/Multa')

        y += self.heightLine
        self._horizontal_line(self.width - (45*mm), y, 45*mm)
        self.canvas.drawString(self.width - (45*mm) + self.space, y + self.deltaTitle, '(-) Outras deduções')

        y += self.heightLine
        self._horizontal_line(self.width - (45*mm), y, 45*mm)
        self.canvas.drawString(self.width - (45*mm) + self.space, y + self.deltaTitle, '(-) Descontos/Abatimentos')
        self.canvas.drawString(0, y + self.deltaTitle, 'Instruções')

        self.canvas.setFont('Helvetica', self.fontSizeValue)
        for l in self.boleto.instrucoes:
            self.canvas.drawString(2*self.space, y - (self.boleto.instrucoes.index(l) * self.deltaFont), l)
        self.canvas.setFont('Helvetica', self.fontSizeTitle)


        # Linha horizontal com primeiro campo Uso do Banco
        y += self.heightLine
        self._horizontal_line(0, y, self.width)
        self.canvas.drawString(0, y + self.deltaTitle, 'Uso do banco')

        self._vertical_line((30)*mm, y, 2*self.heightLine)
        self.canvas.drawString((30*mm)+self.space, y + self.deltaTitle, 'Carteira')

        self._vertical_line((30+20)*mm, y, self.heightLine)
        self.canvas.drawString(((30+20)*mm)+self.space, y + self.deltaTitle, 'Espécie')

        self._vertical_line((30+20+20)*mm, y, 2*self.heightLine)
        self.canvas.drawString(((30+40)*mm)+self.space, y + self.deltaTitle, 'Quantidade')

        self._vertical_line((30+20+20+20+20)*mm, y, 2*self.heightLine)
        self.canvas.drawString(((30+40+40)*mm)+self.space, y + self.deltaTitle, 'Valor')

        self.canvas.drawString(self.width - (45*mm) + self.space, y + self.deltaTitle, '(=) Valor documento')

        self.canvas.setFont('Helvetica', self.fontSizeValue)
        self.canvas.drawString((30*mm)+self.space, y + self.space, self.boleto.carteira)
        self.canvas.drawString(((30+20)*mm)+self.space, y + self.space, self.boleto.especie)
        self.canvas.drawString(((30+20+20)*mm)+self.space, y + self.space, self.boleto.quantidade)
        valor = _price_format(self.boleto.valor_documento)
        self.canvas.drawString(((30+20+20+20+20)*mm)+self.space, y + self.space, valor)
        valorDocumento = _price_format(self.boleto.valor_documento)
        self.canvas.drawRightString(self.width - 2*self.space, y + self.space, valorDocumento)
        self.canvas.setFont('Helvetica', self.fontSizeTitle)


        # Linha horizontal com primeiro campo Data documento
        y += self.heightLine
        self._horizontal_line(0, y, self.width)
        self.canvas.drawString(0, y + self.deltaTitle, 'Data do documento')
        self.canvas.drawString((30*mm)+self.space, y + self.deltaTitle, 'N. do documento')
        self.canvas.drawString(((30+40)*mm)+self.space, y + self.deltaTitle, 'Espécie doc')
        self._vertical_line((30+20+20+20)*mm, y, self.heightLine)
        self.canvas.drawString(((30+40+20)*mm)+self.space, y + self.deltaTitle, 'Aceite')
        self.canvas.drawString(((30+40+40)*mm)+self.space, y + self.deltaTitle, 'Data processamento')
        self.canvas.drawString(self.width - (45*mm) + self.space, y + self.deltaTitle, 'Nosso número')

        self.canvas.setFont('Helvetica', self.fontSizeValue)
        self.canvas.drawString(0, y + self.space, _date_format(self.boleto.data_documento))
        self.canvas.drawString((30*mm)+self.space, y + self.space, self.boleto.numero_documento)
        self.canvas.drawString(((30+40)*mm)+self.space, y + self.space, self.boleto.especie_documento)
        self.canvas.drawString(((30+40+20)*mm)+self.space, y + self.space, self.boleto.aceite)
        self.canvas.drawString(((30+40+40)*mm)+self.space, y + self.space, _date_format(self.boleto.data_processamento))
        self.canvas.drawRightString(self.width - 2*self.space, y + self.space, self.boleto.nosso_numero_formatado)
        self.canvas.setFont('Helvetica', self.fontSizeTitle)


        # Linha horizontal com primeiro campo Cedente
        y += self.heightLine
        self._horizontal_line(0, y, self.width)
        self.canvas.drawString(0, y + self.deltaTitle, 'Cedente')
        self.canvas.drawString(self.width - (45*mm) + self.space, y + self.deltaTitle, 'Agência/Código cedente')

        self.canvas.setFont('Helvetica', self.fontSizeValue)
        self.canvas.drawString(0, y + self.space, self.boleto.cedente)
        self.canvas.drawRightString(self.width - 2*self.space, y + self.space, self.boleto.cedente_agencia_codigo)
        self.canvas.setFont('Helvetica', self.fontSizeTitle)


        # Linha horizontal com primeiro campo Local de Pagamento
        y += self.heightLine
        self._horizontal_line(0, y, self.width)
        self.canvas.drawString(0, y + self.deltaTitle, 'Local de pagamento')
        self.canvas.drawString(self.width - (45*mm) + self.space, y + self.deltaTitle, 'Vencimento')

        self.canvas.setFont('Helvetica', self.fontSizeValue)
        self.canvas.drawString(0, y + self.space, self.boleto.local_pagamento)
        self.canvas.drawRightString(self.width - 2*self.space, y + self.space, _date_format(self.boleto.data_vencimento))
        self.canvas.setFont('Helvetica', self.fontSizeTitle)


        # Linha grossa com primeiro campo logo tipo do banco
        self.canvas.setLineWidth(3)
        y += self.heightLine
        self._horizontal_line(0, y, self.width)
        self.canvas.setLineWidth(2)
        self._vertical_line(40*mm, y, self.heightLine)
        self._vertical_line(60*mm, y, self.heightLine)

        logo = self.boleto.logo_path
        if logo:
            self.canvas.drawImage(logo, 0, y + self.space + 1, 60*mm, 10*mm, preserveAspectRatio=True, anchor='sw')
        self.canvas.setFont('Helvetica-Bold', 18)
        self.canvas.drawCentredString(50*mm, y + 2*self.space, self.boleto.banco_dv)
        self.canvas.setFont('Helvetica-Bold', 10)
        self.canvas.drawRightString(self.width, y + 2*self.space, self.boleto.linha_digitavel)

        # Codigo de barras
        self._barcode(self.boleto.codigo_barras, 3*self.space, 0)
        self.canvas.restoreState()

    def _corte(self, x, y, width):
        self.canvas.saveState()
        self.canvas.translate(x*mm, y*mm)
        self.canvas.setLineWidth(1)
        self.canvas.setDash(1, 2)
        self._horizontal_line(0, 0, width*mm)
        self.canvas.restoreState()

    def draw(self):
        self._corte(10, 100, self.width/mm)
        self._ficha(10, 105)
        self._corte(10, 205, self.width/mm)
        self._recibo(10, 165)

    def save(self):
        self.draw()
        self.canvas.showPage()
        self.canvas.save()
        return self.file


def render_to_pdf(boleto):
    return BoletoLayout(boleto, StringIO()).save()


def _render_to_ghostscript(boleto, format):
    try:
        buffer = render_to_pdf(boleto)
        process = subprocess.Popen(GHOSTSCRIPT_COMMAND % format,
                                   shell=True,
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(input=buffer.getvalue())
    finally:
        buffer.close()
    return StringIO(stdout)


def render_to_png(boleto):
    return _render_to_ghostscript(boleto, 'png16')


def render_to_jpg(boleto):
    return _render_to_ghostscript(boleto, 'jpeg')
