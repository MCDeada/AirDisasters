import copy

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus.frames import Frame
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import ParagraphStyle as PS
from typing import Dict, Any, List

from reportlab.platypus import (
    TableStyle, Table, Paragraph, PageBreak,
    BaseDocTemplate, PageTemplate,
)
from reportlab.platypus.tableofcontents import TableOfContents

from interfaces.connection_config import url
from table_consts import pdf_headers, disasters_filters_meta


def footer(canvas, doc):
    """
    Функция печатающая нижние колонтитулы
    """
    canvas.saveState()
    canvas.setFont('Roboto', 9)
    canvas.drawString(inch, 0.75 * inch, "Страница %d " % doc.page)
    canvas.restoreState()


class ReportPdfTemplate(BaseDocTemplate):
    """
    Класс pdf-документа
    """
    def __init__(self, filename, **kw):
        self.allowSplitting = 0
        BaseDocTemplate.__init__(self, filename, **kw)
        # Установка шаблона определенных размеров с указанием
        # Применения функции нижнего колонтитула для каждой страницы
        template = PageTemplate('normal', [
            Frame(3.25 * cm, 2.5 * cm, 15 * cm, 25 * cm)], onPageEnd=footer)
        self.addPageTemplates(template)

    def afterFlowable(self, flowable):
        """ Учитывает в содержании все объекты со стилем Heading1 """
        if flowable.__class__.__name__ == 'Paragraph':
            text = flowable.getPlainText()
            style = flowable.style.name
            if style == 'Heading1':
                self.notify('TOCEntry', (0, text, self.page))


class ReportStyles:
    """ Примененные стили к разному тексту """
    def __init__(self):
        # Регистрация нестандартного шрифта
        pdfmetrics.registerFont(TTFont(
            'Roboto', 'static/Roboto-Regular.ttf', 'UTF-8'
        ))
        self.styles = getSampleStyleSheet()
        # Шрифт для стиля с именем Normal
        self.styles['Normal'].fontName = 'Roboto'
        # Шрифт и отступы для стиля с именем Heading1
        self.styles['Heading1'].fontName = 'Roboto'
        self.styles['Heading1'].spaceBefore = 20
        self.styles['Heading1'].spaceAfter = 20
        # Шрифт и отступы для стиля с именем Heading2
        self.styles['Heading2'].fontName = 'Roboto'
        self.styles['Heading2'].spaceBefore = 20
        self.styles['Heading2'].spaceAfter = 20
        # Базовые стили для таблицы: выравнивание, границы, шрифт, отступы
        self.tbl_styles_base = [
            ('FONT', (0, 0), (-1, 1), 'Roboto', 10),
            ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, 1), 10),
            ('BOX', (0, 0), (-1, -1), 1, colors.black)
        ]
        # Стили для пунктов Содержания
        self.toc_h0 = PS(
            name='Heading0', fontSize=26, leading=16,
            fontName='Roboto', spaceAfter=30
        )
        self.toc_h1 = PS(
            name='Heading1', fontSize=12, leading=16, fontName='Roboto',
            rightIndent=20,
        )
        self.toc_h2 = PS(
            name='Heading2', fontSize=10, leading=14,
            rightIndent=20, leftIndent=10, fontName='Roboto'
        )


def create_pdf(
    user_info: Dict[str, Any],
    filename: str,
    data1: Dict[str, Any],
    data2: List[Dict[str, Any]],
    current_date: str,
    filters: Dict[str, Any]
) -> None:
    """
    Создает документ, наполняет его данными и стилизует их
    :param user_info: Информация о человеке запустившем создание
    :param filename: Имя файла
    :param data1: Статистика по каждому полю
    :param data2: Статистика наихудших катастроф
    :param current_date: Дата создания отчета
    :param filters: Фильтры, примененные при выборе записей в базе
    :return: Файл pdf
    """
    all_tables = []
    styles = ReportStyles()
    toc = TableOfContents()
    toc.levelStyles = [styles.toc_h1, styles.toc_h2]
    # Общая информация
    all_tables.append(Paragraph(
        f"Пользователь запросивший статистику:",
        styles.styles['Heading2']
    ))
    all_tables.append(Paragraph(
        f"{user_info['Фамилия']} {user_info['Имя']} {user_info['Отчество']}",
        styles.toc_h2
    ))
    all_tables.append(Paragraph(
        f"Дата формирования отчета:",
        styles.styles['Heading2']
    ))
    all_tables.append(Paragraph(
        f"{current_date}",
        styles.toc_h2
    ))
    all_tables.append(Paragraph(
        'Данные собраны в соответствии со следующими фильтрами:',
        styles.styles['Heading2']
    ))
    for sort_filter, value in filters.items():
        if value != '' and value != []:
            text = disasters_filters_meta[sort_filter]['title'] + ': '
            if isinstance(value, list):
                text += str(value)[1:-1]
            else:
                text += value
            all_tables.append(Paragraph(
                text,
                styles.toc_h2
            ))
    all_tables.append(PageBreak())
    # добавление содержания
    all_tables.append(
        Paragraph('Содержание:', styles.toc_h0)
    )
    all_tables.append(toc)
    # переход на новую страницу
    all_tables.append(PageBreak())
    # Добавление таблиц со статистикой
    for filed_name, values in data1.items():
        title = pdf_headers['tables_block_1'] + '\'' + filed_name + '\''
        all_tables.append(
            Paragraph(title + ':', styles.styles['Heading1'])
        )
        # Заголовок таблицы
        table = [
            [Paragraph(hd, styles.styles['Normal'])
             for hd in values[0].keys()]
        ]
        tbl_styles = copy.deepcopy(styles.tbl_styles_base)
        # Содержание таблицы
        for i, row in enumerate(values):
            data = []
            color = colors.white
            j = 0
            tbl_styles.append(
                ('LINEBEFORE', (j, 0), (j, -1), 1, colors.black)
            )
            for header, value in row.items():
                data.append(Paragraph(str(value), styles.styles['Normal']))
                tbl_styles.append(
                    ('LINEAFTER', (j, 0), (j, -1), 1, colors.black)
                )
                j += 1
            # Каждая четная строка таблицы имеет окрашенный фон ячеек
            if (i + 1) % 2:
                color = colors.lightgrey
            tbl_styles.append(('BACKGROUND', (0, i + 1), (-1, i + 1), color))
            table.append(data)
        # Когда данные для таблиц сформированы, создается объект
        # и добавляются стили
        table = Table(table, colWidths=75)
        table.setStyle(TableStyle(tbl_styles))
        all_tables.append(table)
        all_tables.append(PageBreak())
    # Заголовок таблицы с наихудшими случаями
    table = [
        [Paragraph(hd, styles.styles['Normal'])
         for hd in data2[0].keys()
         if hd != 'id']
    ]
    all_tables.append(
        Paragraph(pdf_headers['tables_block_2'], styles.styles['Heading1'])
    )
    tbl_styles = copy.deepcopy(styles.tbl_styles_base)
    data2 = data2
    # Строки таблицы
    for i, row in enumerate(data2):
        data = []
        color = colors.white
        j = 0
        tbl_styles.append(
            ('LINEBEFORE', (j, 0), (j, -1), 1, colors.black)
        )
        for header, value in row.items():
            # Номер катастрофы - ссылка, ведущая на полную информацию
            if header == 'Номер полета(ссылка)':
                text = f"<a href={url}/get/disasters/{row['id']}>{str(value)}</a>"
            elif header == 'id':
                continue
            else:
                text = str(value)
            data.append(Paragraph(text, styles.styles['Normal']))
            tbl_styles.append(
                ('LINEAFTER', (j, 0), (j, -1), 1, colors.black)
            )
            j += 1
        if (i + 1) % 2:
            color = colors.lightgrey
        tbl_styles.append(('BACKGROUND', (0, i + 1), (-1, i + 1), color))
        table.append(data)
    table = Table(table, colWidths=75)
    table.setStyle(TableStyle(tbl_styles))
    all_tables.append(table)
    all_tables.append(PageBreak())
    # Создание документа
    pdf = ReportPdfTemplate(
        filename=filename,
        pagesize=A4,
        title='Отчёт о катастрофах',
        author=
        f"{user_info['Фамилия']} {user_info['Имя']} {user_info['Отчество']}"
    )
    # Заполнение всеми описанными ранее объектами
    pdf.multiBuild(all_tables)
