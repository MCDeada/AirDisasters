import mysql.connector

from interfaces.connection_config import connection_params
from datetime import datetime, timedelta
from random import randrange, random


sql_op = f"""
    select id, country
    from AirDisasters.operators
"""

sql_fl_types = f"""
    select id
    from AirDisasters.flight_types
"""

sql_aircraft_types = f"""
    select id, max_crew, max_passengers
    from AirDisasters.aircraft_types
"""

sql_engine_types = f"""
    select id
    from AirDisasters.engine_types
"""

sql_engine_types_to_aircraft_types = f"""
    select id_engine_type, id_aircraft_type
    from AirDisasters.Engines_types_to_aircraft_types
"""

sql_countries = f"""
    select id
    from AirDisasters.countries
"""

sql_airports = f"""
    select id, country
    from AirDisasters.airports
"""

sql_flight_phases = f"""
    select id
    from AirDisasters.flight_phases
"""

sql_aircraft_conditions = f"""
    select id
    from AirDisasters.aircraft_conditions
"""

sql_weather_conditions = f"""
    select id
    from AirDisasters.weather_conditions
"""

sql_accident_types = f"""
    select id
    from AirDisasters.Aviation_accident_types
"""

with mysql.connector.connect(**connection_params) as conn:
    cur = conn.cursor(dictionary=True)
    cur.execute(sql_op)
    operators = cur.fetchall()

    cur.execute(sql_fl_types)
    flight_types = cur.fetchall()

    cur.execute(sql_aircraft_types)
    aircraft_types = cur.fetchall()
    aircraft_types_dict = {row['id']: (row['max_crew'], row['max_passengers']) for row in aircraft_types}

    cur.execute(sql_engine_types)
    engine_types = cur.fetchall()

    cur.execute(sql_engine_types_to_aircraft_types)
    engine_types_to_aircraft_types = cur.fetchall()

    engine_types_to_aircraft_types_dict = {}
    for pair in engine_types_to_aircraft_types:
        id_engine_type = pair['id_engine_type']
        id_aircraft_type = pair['id_aircraft_type']
        if id_aircraft_type in engine_types_to_aircraft_types_dict:
            engine_types_to_aircraft_types_dict[id_aircraft_type].append(id_engine_type)
        else:
            engine_types_to_aircraft_types_dict[id_aircraft_type] = [id_engine_type]

    cur.execute(sql_countries)
    countries = cur.fetchall()

    cur.execute(sql_airports)
    airports = cur.fetchall()

    op_dict = {country['id']: {} for country in countries}
    for country in countries:
        for operator in operators:
            if operator['country'] == country['id']:
                if op_dict[country['id']] == {}:
                    op_dict[country['id']] = [operator['id']]
                else:
                    op_dict[country['id']].append(operator['id'])

    airports_dict = {country['id']: {} for country in countries}
    for country in countries:
        for airport in airports:
            if airport['country'] == country['id']:
                if airports_dict[country['id']] == {}:
                    airports_dict[country['id']] = [airport['id']]
                else:
                    airports_dict[country['id']].append(airport['id'])

    cur.execute(sql_flight_phases)
    flight_phases = cur.fetchall()

    cur.execute(sql_aircraft_conditions)
    aircraft_conditions = cur.fetchall()

    cur.execute(sql_weather_conditions)
    weather_conditions = cur.fetchall()

    cur.execute(sql_accident_types)
    accident_types = cur.fetchall()
    cur.close()

result = []

for _ in range(10000):
    flight_phase = flight_phases[randrange(len(flight_phases))]['id']
    aircraft_condition = aircraft_conditions[randrange(len(aircraft_conditions))]['id']
    weather_condition = weather_conditions[randrange(len(weather_conditions))]['id']
    accident_type = accident_types[randrange(len(accident_types))]['id']
    flight_type = flight_types[randrange(len(flight_types))]['id']
    aircraft_type = aircraft_types[randrange(len(aircraft_types))]['id']
    lst = engine_types_to_aircraft_types_dict[aircraft_type]
    engine_type = lst[randrange(len(lst))]
    op_countries = []
    for country in op_dict:
        if op_dict[country] != {}:
            op_countries.append(country)
    country_dep = op_countries[randrange(len(op_countries))]
    operators_lst = op_dict[country_dep]
    operator = operators_lst[randrange(len(operators_lst))]
    airports_lst = airports_dict[country_dep]
    airport_dep = airports_lst[randrange(len(airports_lst))]
    country_des = op_countries[randrange(len(op_countries))]
    while country_des == country_dep:
        country_des = op_countries[randrange(len(op_countries))]
    airports_lst = airports_dict[country_des]
    airport_des = airports_lst[randrange(len(airports_lst))]
    country_dis = countries[randrange(len(countries))]['id']
    disaster_datetime = datetime(
        year=randrange(2000, 2011),
        month=randrange(1, 13),
        day=randrange(1, 28),
        hour=randrange(0, 24),
        minute=randrange(0, 60),
        second=randrange(0, 60),
    )
    dep_datetime = disaster_datetime - timedelta(seconds=randrange(0, 14400))
    des_datetime = disaster_datetime + timedelta(seconds=randrange(0, 14400))
    flight_number = 'ADV-' + str(randrange(0, 1000))
    registration_code = 'ZA-' + str(randrange(0, 1000))
    crew_fatal = randrange(0, aircraft_types_dict[aircraft_type][0])
    crew_survived = aircraft_types_dict[aircraft_type][0] - crew_fatal
    passengers_fatal = randrange(0, aircraft_types_dict[aircraft_type][1])
    passengers_survived = aircraft_types_dict[aircraft_type][1] - passengers_fatal
    temperature = randrange(-100, 100) * random()
    pressure = randrange(0, 850) * random()
    """
    disaster_datetime, flight_type, flight_number, operator, aircraft_model_type,
    engine_model_type, registration_code, departure_place, departure_date,
    destination_place, destination_date, crew_survived, crew_fatalities,
    passengers_survived, passengers_fatalities, temperature, country,
    flight_phase, aircraft_condition, weather_condition, disaster_accident"""
    s = (f"('{disaster_datetime}', {flight_type}, '{flight_number}', {operator}, "
         f"{aircraft_type}, {engine_type}, '{registration_code}', "
         f"{airport_dep}, '{dep_datetime}', {airport_des}, '{des_datetime}', "
         f"{crew_survived}, {crew_fatal}, {passengers_survived}, {passengers_fatal}, "
         f"{temperature}, {pressure}, {country_dis}, {flight_phase}, {aircraft_condition}, "
         f"{weather_condition}, {accident_type})")
    result.append(s)
res_res = ', \n'.join(result)
print()
#
# dat = datetime.strptime(str(res), '%a, %d %b %Y %H:%M:%S %Z').date()
# print()


# from reportlab.lib.styles import ParagraphStyle as PS
# from reportlab.platypus import PageBreak
# from reportlab.platypus.paragraph import Paragraph
# from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
# from reportlab.platypus.tableofcontents import TableOfContents
# from reportlab.platypus.frames import Frame
# from reportlab.lib.units import cm
#
#
# class MyDocTemplate(BaseDocTemplate):
#
#     def __init__(self, filename, **kw):
#         self.allowSplitting = 0
#         BaseDocTemplate.__init__(self, filename, **kw)
#         template = PageTemplate('normal', [Frame(2.5*cm, 2.5*cm, 15*cm, 25*cm, id='F1')])
#         self.addPageTemplates(template)
#
#     def afterFlowable(self, flowable):
#         "Registers TOC entries."
#         if flowable.__class__.__name__ == 'Paragraph':
#             text = flowable.getPlainText()
#             style = flowable.style.name
#             if style == 'Heading1':
#                 self.notify('TOCEntry', (0, text, self.page))
#             if style == 'Heading2':
#                 self.notify('TOCEntry', (1, text, self.page))
#
# h1 = PS(name = 'Heading1',
#        fontSize = 14,
#        leading = 16)
#
# h2 = PS(name = 'Heading2',
#        fontSize = 12,
#        leading = 14,
#        leftIndent = 10)
#
# # Build story.
# story = []
# toc = TableOfContents()
# # For conciseness we use the same styles for headings and TOC entries
# toc.levelStyles = [h1, h2]
# story.append(toc)
# story.append(PageBreak())
# story.append(Paragraph('First heading', h1))
# story.append(Paragraph('Text in first heading', PS('body')))
# story.append(Paragraph('First sub heading', h2))
# story.append(Paragraph('Text in first sub heading', PS('body')))
# story.append(PageBreak())
# story.append(Paragraph('Second sub heading', h2))
# story.append(Paragraph('Text in second sub heading', PS('body')))
# story.append(Paragraph('Last heading', h1))
#
# doc = MyDocTemplate('mintoc.pdf')
# doc.multiBuild(story)
