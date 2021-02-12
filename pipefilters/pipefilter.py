import logging

log = logging.getLogger()


class PipeFilter:
    """
    Pipe or Filter superclass

    Sorted according to priority then name. The lower the value, the closer to the beginning of the PipeFilter chain.
    """
    def __init__(self, name='anonymous', applies_to=None, priority=float('inf')):
        self.name = name
        self._applies_to = applies_to
        self.priority = priority

    def applies_to(self, event):
        """
        Expected to return True if Pipe or Filter must apply on received event, False otherwise (event skips this Node)
        """
        return True if self._applies_to is None else self._applies_to(event)

    def __lt__(self, other):
        return (self.priority, self.name) < (other.priority, self.name)

    def __repr__(self):
        return "<{class_name} '{name}'>".format(class_name=type(self).__name__, name=self.name)


class Filter(PipeFilter):
    """
    Apply provided function "accepts" to event, expected to return True to keep event, False otherwise
    """
    def __init__(self, accepts, **kwargs):
        super().__init__(**kwargs)
        self._accepts = accepts

    def accepts(self, component):
        return self._accepts(component)


class Pipe(PipeFilter):
    """
    Apply provided function "transforms" to event, expected to change event in place
    """
    def __init__(self, transforms, **kwargs):
        super().__init__(**kwargs)
        self._transforms = transforms

    def transforms(self, event):
        self._transforms(event)


class SummaryMapPipe(Pipe):
    """
    Rename summary of event according to provided map
    """
    def __init__(self, _map, **kwargs):
        super().__init__(self.transforms, **kwargs)
        self.map = _map

    def applies_to(self, event):
        return event['summary'] in self.map.keys()

    def transforms(self, event):
        summary = event['summary']
        log.debug('%s -> %s', event['summary'], self.map[summary])
        event['summary'] = self.map[summary]
