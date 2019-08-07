# Greenreactor
A reactor which make twisted compatc with gevent 


## Motivation

Originally I wrote code for [Scrapy](https://github.com/scrapy/scrapy). I want to combine gevent in Scrapy, so I created this greenreactor.

## Installation
`pip install greenreactor`

## Usage

```python
# Usually we need monkey patch, simply patch all things or patch part of them if you understand what you are doing.
# Guideline: http://www.gevent.org/api/gevent.monkey.html
import gevent.monkey
gevent.monkey.patch_all()

# Install greenreactor
import greenreactor
greenreactor.install()

from twisted.internet import reactor
reactor.run()
```

Thats all! Now you can use any gevent api such as `spawn`, `spawn_later`, etc.
