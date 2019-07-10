==================
python-duckduckgo
==================

A Python library for querying the `DuckDuckGo Instant Answer API <https://duckduckgo.com/api>`_.

This version has been forked from the original to work with Python 3.7 or later.
It uses dataclasses and Marshmallow library to parse DuckDuckGo responses.

Note that this is a wrapper around DuckDuckGo API and they might change how they provide
answers or stop providing answers all together. For example you used to be able to ask
the API to calculate '2 + 2' but now they just tell you it's a calculation but don't
provide the answer.

Installation
============

If you already downloaded the source you can run:

    ``python3.7 setup.py install``

Here is how you can install it using pip from the git repo:
    ``pip install git+git://github.com/nikolskiy/python-duckduckgo.git``

Command Line Usage
==================
Print your IP address according to DuckDuckGo:
    ``ddg ip``

Ask DuckDuckGo to check your spelling:
    ``ddg how to spell missisipy``

``ddg`` command is a wrapper around ``query('command line args')`` and ``response.zci`` calls so
all the queries described in the section below should still work

Query Usage
===========

    >>> from duckduckgo import query
    >>> r = query('DuckDuckGo')
    >>> r.kind
    'answer'
    >>> r.results[0].text
    'Official site'
    >>> r.results[0].url
    'http://duckduckgo.com/'
    >>> r.abstract.url
    'http://en.wikipedia.org/wiki/Duck_Duck_Go'
    >>> r.abstract.source
    'Wikipedia'
    
    >>> r = query('Python')
    >>> r.kind
    'disambiguation'
    >>> r.related_topics[0].text
    'Python (programming language) An interpreted high-level programming language for general-purpose programming.'
    >>> r.related[0].url
    'https://duckduckgo.com/Python_(programming_language)?kp=1'

    >>> r = query('1 + 1')
    >>> r.kind
    'calc'
    >>> r.answer.text
    '' # This is sad but DuckDuckGo API stopped providing answers for calculations
    >>> r.answer.kind
    'calc'

    >>> query('how to spell test', html=True).answer.text
    <b>Test</b> appears to be spelled correctly!<br/><i>Suggestions:</i> <a href='/?q=define+test'>test</a>
    <a href='/?q=define+testy'>testy</a> <a href='/?q=define+teat'>teat</a>
    <a href='/?q=define+tests'>tests</a> <a href='/?q=define+rest'>rest</a> <a href='/?q=define+yest'>yest</a> .


    >>> query('foo').zci
    'Foobar The terms foobar, or foo and others are used as placeholder names in computer programming or...'

Special keyword args for query():
 - safesearch  - boolean, enable or disable safesearch.
 - html        - boolean, Allow HTML in responses?

Credits
=======

| Copyright (c) 2010 Michael Stephens <me@mikej.st>
| Copyright (c) 2012-2013 Michael Smith <crazedpsyc@gshellz.org>
| Copyright (c) 2019 Denis Nikolskiy

Released under a 3-clause BSD license, see LICENSE for details.

| Latest: https://github.com/nikolskiy/python-duckduckgo
| Previous: http://github.com/crazedpsyc/python-duckduckgo
| Original: http://github.com/mikejs/python-duckduckgo (outdated)

