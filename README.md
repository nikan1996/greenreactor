# gevent_reactor
A reactor which make twisted compatible with gevent 

## Installation
`pip install greenreactor`
## Usage

```python
# Usually we need monkey patch
import gevent.monkey
gevent.monkey.patch_all()

# Install greenreactor
import greenreactor
greenreactor.install()

from twisted.internet import reactor
reactor.run()
```

Then you can use any gevent api such as `spawn`, `spawn_later`, `1etc.
