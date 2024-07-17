# geekie-wafer

Converts between object graphs represented by a dictionary and by models

## Migrating from `glibs.wafer`

Most things just work by changing the import from `glibs.wafer` to `wafer`. The only exception is `glibs.wafer.utils` was renamed to `wafer.fields`.

Also the old `glibs.utils.alias` has been moved to `wafer.utils.alias`.

## Usage

Suppose we have a very simple model serialized as follows:

```py
serialized_presentation = {
    "name": "Rockband Matches",
    "author": "Edward Merryweather",
    "type": "ppt",
}
```

We can map that to a model using Wafer as follows:

```py
class Presentation(wafer.Model):
    name = wafer.Field()
    author = wafer.Field()
    type = wafer.Field()
```

Converting the dictionary to a model then becomes very simple

```py
presentation = Presentation(serialized_presentation)
print presentation.name # Outputs Rockband Matches
```

Going the other way around is also very straightforward

```py
presentation = Presentation()
presentation.name = "Rockband Matches"
presentation.author = "Edward Merryweather"
presentation.serialize() # Outputs {
                         #      "name": "Rockband Matches",
                         #      "author": "Edward Merryweather"
                         # }
```

Note that fields whose value is `None` are not written to the dictionary.

### Embedded documents

Frequently models contain themselves other models:

```py
friday_fun_event = {
    "presentation": {
        "name": "Rockband Matches",
    },
}
```

For Wafer to properly serialize and deserialize this kind of object graph, you simply pass the model you want to use to the `wafer.Field` constructor:

```py
class Event(wafer.Model):
    presentation = wafer.Field(Presentation)

event = Event(friday_fun_event)
event.presentation.name # Outputs "Rockband Matches"
```

And the other way around:

```py
event = Event()
event.presentatiob # Outputs None
event.presentation = Presentation()
event.presentation.name = "Rockband Matches"
event.serialize() # Outputs the same as the friday_fun_event object
```

### Embedded collections

In case your model contain a list of embedded models, you use the `wafer.EmbeddedCollection` to declare the field

```py
documents = {
    "presentations": [{
        "name": "Rockband Matches"
    }, {
        "name": "Other"
    }]
}

class DocumentList(wafer.Model):
    presentations = wafer.EmbeddedCollection(Presentation)

list = DocumentList(documents)
list.presentations[1].name # Outputs "Other"
```

Embedded collection fields are never set to `None`, and wafer considers `None` the same as an empty list. Because of that behavior, the following statements are true:

```py
list = DocumentList()
list.presentations # Outputs []
list.serialize()   # Outputs {}, empty list is ignored
```

### Custom serialization/deserialization logic

If you have a field you want to map in some nonstandard way to its serialzed form, override `serialize` and `deserialize` methods

### Customizing getters/setters

If you have a field whose getter/setter logic you want to customize, you'll find that the following doesn't work:

```py
class Person(wafer.Model):
    weight = wafer.Field()

    @property
    def weight(self): # Erases the old definition for 'weight'
        return self.__weight

    @weight.setter
    def weight(self, value):
        if value < 0:
            raise ValueError()
        self.__weight = value
```

In this situation, you can declare the field the following way:

```py
class Person(wafer.Model):
    __weight_field = wafer.Field()
    # Rest of the code unaltered
```

And then everything will work as intended

```py
person = Person({ "weight": -2 }) # raises ValueError
```

### Polymorphism

Your model may have a collection of embedded documents of different types

```py
class Phase(wafer.Model):
    type = wafer.Field()

class VideoPhase(Phase):
    video_url = wafer.Field()

class DrillPhase(Phase):
    exercises = wafer.EmbeddedCollection(Exercise)

class Lecture(wafer.Model):
    phases = wafer.EmbeddedCollection(Phase) # VideoPhase or DrillPhase
```

In such cases, serialization works out of the box but you'll find that deserialization doesn't as it always tries to convert the dictionary to a `Phase` object, and the `Phase` object doesn't know about the different fields each subclass has.

The solution is to use a custom deserialization logic, as follows:

```py
class Phase(wafer.Model):
    @staticmethod
    def deserialize(obj):
        if obj["type"] == "video":
            return VideoPhase(obj)
        else:
            return DrillPhase(obj)

class Lecture(wafer.Model):
    phases = wafer.EmbeddedCollection(Phase, deserializer=Phase.deserialize)
```

You may want to add logic to each subclass to ensure the `type` field is correctly stored. Consider the following possibilities:

````py
class VideoPhase(Phase):
    def serialize(self):
        obj = super(VideoPhase, self).serialize()
        obj["type"] = "video"
        return obj

class VideoPhase(Phase):
    def __init__(self, *args, **kwargs):
        super(VideoPhase, self).__init__(*args, **kwargs)
        self.type = "video"
````
