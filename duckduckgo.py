# duckduckgo.py - Library for querying the DuckDuckGo API
#
# The original library was created by https://github.com/mikejs/python-duckduckgo
# Copyright (c) 2010 Michael Stephens <me@mikej.st>
# Copyright (c) 2012-2013 Michael Smith <crazedpsyc@gshellz.org>
# See LICENSE for terms of usage, modification and redistribution.
#
# It was heavily modified with changes not compatible with
# the original source.

from urllib import request, parse
import json
import sys

from marshmallow import Schema, fields


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
    useragent: UserAgent to use while querying. Default: "python-duckduckgo %d" (str)
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

    schema = Results()
    data = response.read()
    print(json.loads(data))
    obj = schema.loads(data)
    print(obj)

    return obj


class Abstract(Schema):
    html = fields.Str(attribute='Abstract')
    text = fields.Str(attribute='AbstractText')
    url = fields.Url(attribute='AbstractURL')
    source = fields.Str(attribute='AbstractSource')


class Redirect(Schema):
    url = fields.Url(attribute='Redirect')


class Image(Schema):
    url = fields.Url(attribute='Result')
    height = fields.Int(attribute='Height')
    width = fields.Int(attribute='Width')


class Result(Schema):
    topics = fields.List(fields.Str(), attribute='Topics')
    html = fields.Str(attribute='Result')
    text = fields.Str(attribute='Text')
    url = fields.Url(attribute='FirstURL')
    icon = fields.Nested(Image, attribute='Image')


class Answer(Schema):
    text = fields.Str(attribute='Answer')
    kind = fields.Str(attribute='AnswerType')


class Definition(object):
    text = fields.Str(attribute='Definition')
    url = fields.Url(attribute='DefinitionURL')
    source = fields.Str(attribute='DefinitionSource')


class Results(Schema):
    # {'A': 'answer', 'D': 'disambiguation',
    #  'C': 'category', 'N': 'name',
    #  'E': 'exclusive', '': 'nothing'}
    kind = fields.Str(attribute='Type')
    heading = fields.Str(attribute='Heading')
    results = fields.Nested(Result, attribute='Results', many=True)
    related = fields.Nested(Result, attribute='RelatedTopics', many=True)
    abstract = fields.Nested(Abstract)
    definition = fields.Nested(Definition)
    answer = fields.Nested(Answer)
    image = fields.Nested(Image)


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
    print(response)


def main():
    if len(sys.argv) > 1:
        answer(' '.join(sys.argv[1:]))
    else:
        print('Usage: %s [query]' % sys.argv[0])


if __name__ == '__main__':
    main()
