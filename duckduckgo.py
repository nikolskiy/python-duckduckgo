# duckduckgo.py - Library for querying the DuckDuckGo API
#
# The original library was created by https://github.com/mikejs/python-duckduckgo
# Copyright (c) 2010 Michael Stephens <me@mikej.st>
# Copyright (c) 2012-2013 Michael Smith <crazedpsyc@gshellz.org>
# See LICENSE for terms of usage, modification and redistribution.
#
# It was heavily modified with changes not compatible with
# the original source.

from typing import List
from urllib import request, parse
import sys

from dataclasses import dataclass
from marshmallow import Schema, fields, post_load
from pprint import pprint


def query(qstr, safe_search=True, html=False, meanings=True, **kwargs):
    """
    Query DuckDuckGo, returning a Results object.

    Here's a query that's unlikely to change:

    >>> result = query('1 + 1')
    >>> result.type
    'nothing'
    >>> result.answer.text
    '1 + 1 = 2'
    >>> result.answer.type
    'calc'

    Keword arguments:
    safe_search: True for on, False for off. Default: True (bool)
    html: True to allow HTML in output. Default: False (bool)
    meanings: True to include disambiguations in results (bool)
    Any other keyword arguments are passed directly to DuckDuckGo as URL params.
    """

    safe_search = '1' if safe_search else '-1'
    html = '0' if html else '1'
    meanings = '0' if meanings else '1'
    params = {
        'q': qstr,
        'o': 'json',
        'kp': safe_search,
        'no_redirect': '1',
        'no_html': html,
        'd': meanings,
        }
    params.update(kwargs)

    url = 'https://api.duckduckgo.com/?' + parse.urlencode(params)
    response = request.urlopen(url)

    data = response.read()
    #pprint(json.loads(data))

    schema = ResponseSchema()
    obj = schema.loads(data, partial=True)

    return obj


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
class Topic:
    url: str
    result: str
    text: str
    icon: str


@dataclass
class Result:
    topics: List[Topic]
    html: str
    text: str
    url: str
    icon: str


@dataclass
class Response:
    kind: str
    heading: str
    results: List[Result]
    related_topics: List[Topic]
    abstract: Abstract
    redirect: str
    definition: Definition
    answer: Answer
    image: Image


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
    height = SizeInteger(data_key='Height')
    url = fields.Str(data_key='URL')
    width = SizeInteger(data_key='Width')


class TopicSchema(Schema):
    url = fields.Str(data_key='FirstURL')
    text = fields.Str(data_key='Text')
    result = fields.Str(data_key='Result')
    icon = fields.Nested(IconSchema, data_key='Icon')


class ResponseSchema(Schema):
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
    image_height = fields.Int(data_key='ImageHeight')
    image_is_logo = fields.Bool(data_key='ImageIsLogo')
    image_width = fields.Int(data_key='ImageWidth')
    infobox = fields.Dict(data_key='Infobox')
    redirect = fields.Str(data_key='Redirect')
    related_topics = fields.Nested(TopicSchema, data_key='RelatedTopics', many=True)
    results = fields.Nested(TopicSchema, data_key='Results', many=True)
    kind = fields.Str(data_key='Type')
    meta = fields.Dict(data_key='meta')

    @post_load
    def make_response_class(self, data):
        abstract = Abstract(
            html=data['abstract'], text=data['abstract_text'],
            url=data['abstract_url'], source=data['abstract_source']
        )
        answer = Answer(text=data['answer'], kind=data['answer_type'])
        kind = {'A': 'answer', 'D': 'disambiguation', 'C': 'category', 'N': 'name',
                'E': 'exclusive', '': 'nothing'}[data['kind']]
        results = [Result(i[])]



def get_zci(q, web_fallback=True, priority=('answer', 'definition', 'abstract', 'related.0'), urls=True, **kwargs):
    """
    A helper method to get a single (and hopefully the best) ZCI result.
    priority=list can be used to set the order in which fields will be checked for answers.
    Use web_fallback=True to fall back to grabbing the first web result.
    passed to query. This method will fall back to 'Sorry, no results.'
    if it cannot find anything.

    :param q:
    :param web_fallback:
    :param priority:
    :param urls:
    :param kwargs:
    :return:
    """

    ddg = query('\\'+q, **kwargs)
    response = ''

    for p in priority:
        ps = p.split('.')
        type = ps[0]
        index = int(ps[1]) if len(ps) > 1 else None

        result = getattr(ddg, type)
        if index is not None: 
            if not hasattr(result, '__getitem__'):
                raise TypeError('%s field is not indexable' % type)

            result = result[index] if len(result) > index else None
        if not result:
            continue

        if result.text:
            response = result.text
        if result.text and hasattr(result, 'url') and urls:
            if result.url:
                response += ' (%s)' % result.url
        if response:
            break

    # if there still isn't anything, try to get the first web result
    if not response and web_fallback:
        if ddg.redirect.url:
            response = ddg.redirect.url

    # final fallback
    if not response: 
        response = 'Sorry, no results.'

    return response


def show_all(qstr):
    q = query(qstr)
    for key in sorted(q.json.keys()):
        sys.stdout.write(key)
        if type(q.json[key]) in [str, int]:
            print(':', q.json[key])
        else:
            sys.stdout.write('\n')
            for i in q.json[key]:
                print('\t', i)


def answer(qstr):
    response = get_zci(qstr)
    #print(response)


def main():
    if len(sys.argv) > 1:
        answer(' '.join(sys.argv[1:]))
    else:
        print('Usage: %s [query]' % sys.argv[0])


if __name__ == '__main__':
    main()
