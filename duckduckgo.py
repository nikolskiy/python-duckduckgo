# duckduckgo.py - Library for querying the DuckDuckGo API
#
# The original library was created by https://github.com/mikejs/python-duckduckgo
# Copyright (c) 2010 Michael Stephens <me@mikej.st>
# Copyright (c) 2012-2013 Michael Smith <crazedpsyc@gshellz.org>
# See LICENSE for terms of usage, modification and redistribution.
#
# It was heavily modified with changes not compatible with
# the original source.

from typing import List, Dict
from urllib import request, parse
import sys

from dataclasses import dataclass
from marshmallow import Schema, fields, post_load, pre_load, EXCLUDE


@dataclass
class Answer:
    text: str
    kind: str


@dataclass
class Definition:
    text: str
    url: str
    source: str


@dataclass
class Abstract:
    html: str
    text: str
    url: str
    source: str


@dataclass
class Image:
    url: str
    height: int
    width: int


@dataclass
class Icon:
    url: str
    height: int
    width: int


@dataclass
class Topic:
    html: str
    text: str
    icon: Icon
    url: str


@dataclass
class Redirect:
    text: str


@dataclass
class Response:
    kind: str
    heading: str
    results: List[Topic]
    related_topics: List[Topic]
    abstract: Abstract
    redirect: Redirect
    definition: Definition
    answer: Answer
    image: Image
    data_dict: Dict
    priority = ['answer', 'definition', 'abstract', 'related_topics', 'redirect']

    @property
    def zci(self):
        for field in self.priority:
            result = getattr(self, field, None)
            # pick first item if the result is a list
            if isinstance(result, list):
                if not result:
                    continue
                result = result[0]
            result = result.text
            if result:
                return result

        return 'Sorry, I have nothing to report here.'


class SizeInteger(fields.Integer):
    """
    Modification of Int field that accepts empty strings
    and sets them to default value.
    """
    def __init__(self, *, empty_default=0, **kwargs):
        self.empty_default = empty_default
        super().__init__(**kwargs)

    def _format_num(self, value):
        if not value:
            value = self.empty_default
        return super()._format_num(value)


class IconSchema(Schema):
    url = fields.Str(data_key='URL')
    height = SizeInteger(data_key='Height')
    width = SizeInteger(data_key='Width')


class TopicSchema(Schema):
    html = fields.Str(data_key='Result')
    text = fields.Str(data_key='Text')
    icon = fields.Nested(IconSchema, data_key='Icon')
    url = fields.Str(data_key='FirstURL')


class ResponseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    abstract = fields.Str(data_key='Abstract')
    abstract_source = fields.Str(data_key='AbstractSource')
    abstract_text = fields.Str(data_key='AbstractText')
    abstract_url = fields.Str(data_key='AbstractURL')
    answer = fields.Str(data_key='Answer')
    answer_type = fields.Str(data_key='AnswerType')
    definition = fields.Str(data_key='Definition')
    definition_source = fields.Str(data_key='DefinitionSource')
    definition_url = fields.Str(data_key='DefinitionURL')
    entity = fields.Str(data_key='Entity')
    heading = fields.Str(data_key='Heading')
    image = fields.Str(data_key='Image')
    image_height = SizeInteger(data_key='ImageHeight')
    image_width = SizeInteger(data_key='ImageWidth')
    redirect = fields.Str(data_key='Redirect')
    related_topics = fields.Nested(TopicSchema, data_key='RelatedTopics', many=True)
    results = fields.Nested(TopicSchema, data_key='Results', many=True)
    kind = fields.Str(data_key='Type')

    @post_load
    def make_response_class(self, data, **kwargs):
        abstract = Abstract(
            html=data['abstract'], text=data['abstract_text'],
            url=data['abstract_url'], source=data['abstract_source']
        )
        kind = {'A': 'answer', 'D': 'disambiguation', 'C': 'category', 'N': 'name',
                'E': 'exclusive', '': 'nothing'}[data['kind']]
        if data['answer_type']:
            kind = data['answer_type']
        definition = Definition(
            text=data['definition'], url=data['definition_url'], source=data['definition_source']
        )
        image = Image(
            url=data['image'], width=data['image_width'],
            height=data['image_height']
        )
        results = [
            Topic(html=i['html'], text=i['text'], icon=Icon(**i['icon']), url=i['url'])
            for i in data['results']
        ]
        related_topics = [
            Topic(html=i['html'], text=i['text'], icon=Icon(**i['icon']), url=i['url'])
            for i in data['related_topics']
        ]
        return Response(
            kind=kind, heading=data['heading'], results=results, related_topics=related_topics,
            abstract=abstract, redirect=Redirect(text=data['redirect']), definition=definition,
            answer=Answer(text=data['answer'], kind=data['answer_type']),
            image=image, data_dict=data
        )

    @pre_load
    def pre_process(self, data, **kwargs):
        return self.fix_schema(data, 'RelatedTopics')

    def fix_schema(self, data, key):
        """
        Some responses are wrapped into topics in the following form
        'name': 'Places',
        'Topics': [{}, {}, ...]
        Topics here are in the standard form 'Result', 'Text', etc.
        This function will make the structure flat and throw away
        topic name since it doesn't show up for all results.
        """
        new_topics = []
        for item in data[key]:
            if 'Topics' in item:
                new_topics += item['Topics']
            else:
                new_topics.append(item)

        data[key] = new_topics
        return data


def query(qstr, safe_search=True, html=False, meanings=True, **kwargs):
    """
    Query DuckDuckGo, returning a Results object.

    Keword arguments:
    safe_search: True for on, False for off. Default: True (bool)
    html: True to allow HTML in output. Default: False (bool)
    meanings: True to include disambiguations in results (bool)
    Any other keyword arguments are passed directly to DuckDuckGo as URL params.
    """
    params = {
        'q': qstr,
        'o': 'json',
        'kp': '1' if safe_search else '-1',
        'no_redirect': '1',
        'no_html': '0' if html else '1',
        'd': '0' if meanings else '1',
    }
    params.update(kwargs)

    url = 'https://api.duckduckgo.com/?' + parse.urlencode(params)
    with request.urlopen(url) as response:
        obj = ResponseSchema().loads(response.read())

    return obj


def main():
    if len(sys.argv) > 1:
        res = query(' '.join(sys.argv[1:]))
        print()
        print(res.zci)
        print()
    else:
        res = 'Usage: %s [query]' % sys.argv[0]
        print(res)


if __name__ == '__main__':
    main()

