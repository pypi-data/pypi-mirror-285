# Nueue

An easier way to create the queue.

```py
$ pip install Nueue
```

## Example

```py
from Nueue.queue import Queue

queue = Queue()

queue.add("Nya! Ichi Ni San Nyaa Arigato!")
queue.add("พี่ชอบหนูที่สุดเลย")

previous = queue.previous()
# None
now_playing = queue.current_item()
# Nya! Ichi Ni San Nyaa Arigato!
next_ = queue.next()
# พี่ชอบหนูที่สุดเลย
```

That's it, have fun! (?
