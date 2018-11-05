# gevent_reactor
A reactor which make twisted compatible with gevent 

## Installation

## Usage

```python
import gevent.monkey
gevent.monkey.patch_all()
from green_reactor.greenreactor import GreenReactor

```

Then you can use any gevent api such as `spawn`, `spawn_later`, etc.
