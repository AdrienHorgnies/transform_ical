from pipefilters.pipefilter import Filter, Pipe, SummaryMapPipe
from datetime import timedelta


def trim_a_distance_fun(event):
    event['summary'] = event['summary'].replace('A DISTANCE - ', '')


def fix_timezone_fun(event):
    event['dtstart'].dt = event['dtstart'].dt + timedelta(hours=2)
    event['dtend'].dt = event['dtend'].dt + timedelta(hours=2)


trim_a_distance = Pipe(trim_a_distance_fun, priority=0)
shortens = SummaryMapPipe({
    'Théorie des graphes et réseaux de Petri': 'Graphes',
    'Ingénierie du logiciel': 'Ingénierie'
}, priority=1)
followed_courses = Filter(lambda event: event['summary'] in ['Laboratoire', 'Ingénierie', 'Graphes'])
fix_timezone = Pipe(fix_timezone_fun)
