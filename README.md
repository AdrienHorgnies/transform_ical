# Transform ical files

This script lets you modify ical files using a convenient interface.

You only have to define some objects in a Python module,
and the script does the rest (parsing, processing and exporting)


## Install
This script is not packaged, you must call the python (>=3.6) interpreter on it.


## Usage

```
python transform_ical ADECal.ics plugin.ade
```

`ADECal.ics` is the file you want to process.

`plugin.ade` is the dot path of the module you must provide and corresponds to the path `./plugin/ade.py`.

This will create a file `out.ics` which contains the result of the transformation.

## How to
Create a python module and define top level attributes using the `Pipe` and `Filter` classes.
Any top level property referencing an instance of these classes will be used to transform the provided ics file.

All events are instance of the Component class from the [icalendar](https://icalendar.readthedocs.io/en/latest/api.html) package.

### Pipe

A `Pipe` node expects a function the modifies the event in place.
```python
def trim_a_distance_fun(event):
    event['summary'] = event['summary'].replace('A DISTANCE - ', '')

# I don't need that in the title, there's already the location for that...
trim_a_distance = Pipe(trim_a_distance_fun)
```

### Filter
A `Filter` node expects a function that returns a boolean value.

```python
# I'm not interested in other courses
followed_courses = Filter(lambda event: event['summary'] in ['Laboratoire', 'Ingénierie', 'Graphes'])
```

### Select which events to apply to
Both `Pipe` and `Filter` can be restricted to apply only on certain events.

To do that, you must provide an `applies_to` function. 
The function must expect an argument event and return a boolean value.
`True` means the node will process the event, `False` means it will not.


```python
# I won't attend this teacher Saturday's courses
no_saturday = Filter(lambda event: event['dtstart'].dt.weekday() != 5,
                     applies_to=lambda event: event['description'].contains('Greenbelt'))
```

### Ordering nodes

In case a node depends on the result of another node, they can be ordered by assigning a priority.
The priority can be any sortable value.
A node with a lower value will run before a node with a higher value.

Nodes are sorted according to their priority then their name.
If no name is provided, the variable name is used.

```python
# trim_a_distance must run before shortens
trim_a_distance = Pipe(trim_a_distance_fun, priority=0)
shortens = SummaryMapPipe({
    'Théorie des graphes et réseaux de Petri': 'Graphes',
    'Ingénierie du logiciel': 'Ingénierie'
}, priority=1)
```

### SummaryMapPipe

An additionnal class is provided to easily change the summary of events.
It expects a dictionary as an argument.
Keys of the dictionary are the old values to change and values are the new values to change to.

```python
shortens = SummaryMapPipe({
    'Théorie des graphes et réseaux de Petri': 'Graphes',
    'Ingénierie du logiciel': 'Ingénierie'
})
```

### Example

An example plugin (`plugin/ade.py`) is provided, it :
* removes 'A DISTANCE - ' prefixes
* changes the summary of some events
* add 2 hours to the start and end of all events
* filter out events that are not part of a given list
