from __future__ import annotations
import inspect
import json
from collections.abc import Mapping


class DataCollection:
    def __init__(self, path: str):
        self.data: dict[str, dict[str, Record]] = {}
        self.__raw_data = json.load(open(path))
        for collection_name, records in self.__raw_data['Schedule'].items():
            cls_name: str = collection_name.removesuffix('s').capitalize()
            cls = globals().get(cls_name, Record)
            if inspect.isclass(cls) and issubclass(cls, Record):
                factory = cls
            else:
                factory = Record
            for record in records:
                collection = self.data.get(collection_name)
                if not collection:
                    self.data[collection_name] = dict()
                key = f'{cls_name.lower()}.{record["serial"]}'
                obj = factory(record)
                obj.collection = self
                self.data[collection_name][key] = obj

    def __getattr__(self, name):
        try:
            return self.__dict__['data'][name]
        except KeyError:
            raise AttributeError


class Record:
    def __init__(self, data: Mapping):
        self.__dict__.update(data)

    @property
    def collection(self) -> DataCollection:
        return self.__collection

    @collection.setter
    def collection(self, obj: DataCollection):
        self.__collection = obj

    def __repr__(self):
        return f'<{self.__class__.__name__} serial={self.serial!r}>'

    def __hash__(self):
        return hash(self.serial)

    def __eq__(self, other):
        return issubclass(other, self.__class__) and self.serial == other.serial


class Event(Record):
    def __repr__(self):
        try:
            return f'<{self.__class__.__name__}: {self.name}>'
        except AttributeError:
            super().__repr__()

    @property
    def speakers(self):
        speakers = []
        for speaker_id in self.__dict__['speakers']:
            key = f'speaker.{speaker_id}'
            speaker: Speaker = self.collection.speakers.get(key, speaker_id)
            speakers.append(speaker)
        return speakers


class Speaker(Record):
    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.name}>'


if __name__ == '__main__':
    col = DataCollection('text.json')
    event: Event = col.events['event.33597']
    speakers: list[Speaker] = event.speakers
    print(f'Event: {event}, url: {event.website_url}\nSpeakers: {speakers}')
    '''
    Event: <Event: Quantifying your Fitness>, url: http://oscon.com/oscon2014/public/schedule/detail/33597
    Speakers: [<Speaker: Kirsten Hunter>, <Speaker: Kjerstin Williams>]
    '''
    pass
