#!/usr/bin/env python3
import argparse
import logging
from importlib import import_module
from pathlib import Path

from icalendar import Calendar

from pipefilters.pipefilter import PipeFilter, Filter, Pipe

log = logging.getLogger()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('ade_path', help='The path to the <filename>.ics')
    p.add_argument('plugin', help='Name of the module containing pipe and filters')
    args = p.parse_args()

    ical_str = open(args.ade_path, 'r').read()
    old_cal = Calendar.from_ical(ical_str)
    new_cal = Calendar()

    pipes_and_filters_module = import_module(args.plugin)
    pipes_and_filters_attrs = [attr for attr in dir(pipes_and_filters_module)
                               if isinstance(getattr(pipes_and_filters_module, attr), PipeFilter)]
    pipes_and_filters = []
    for pipe_filter_attr in pipes_and_filters_attrs:
        pipe_filter = getattr(pipes_and_filters_module, pipe_filter_attr)
        if pipe_filter.name == 'anonymous':
            pipe_filter.name = pipe_filter_attr
        pipes_and_filters.append(pipe_filter)
    pipes_and_filters.sort()

    log.debug('Found pipe and filters  : %s', pipes_and_filters)

    for component in old_cal.walk():
        if component.name == 'VEVENT':
            event = component
            for pipe_filter in pipes_and_filters:
                log.debug('considering %s', pipe_filter)
                if pipe_filter.applies_to(component):
                    log.debug('applying %s', pipe_filter)
                    if isinstance(pipe_filter, Filter):
                        _filter = pipe_filter

                        if _filter.accepts(event):
                            log.debug('accepting event "%s"', component['summary'])
                            continue
                        else:
                            log.info('removing event "%s"', event['summary'])
                            break
                    elif isinstance(pipe_filter, Pipe):
                        pipe = pipe_filter
                        pipe.transforms(event)
            else:
                log.info('adding event "%s"', component['summary'])
                new_cal.add_component(component)

    log.info('done')

    Path('out.ics').write_bytes(new_cal.to_ical())


if __name__ == '__main__':
    log.setLevel(logging.DEBUG)
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)8s : %(message)s'))
    log.addHandler(console)
    main()
