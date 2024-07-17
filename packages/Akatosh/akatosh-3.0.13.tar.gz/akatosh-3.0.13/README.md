# Akatosh

`Akatosh` is a light-weighted disceret event simulation library. Unlike popular library `Simpy` which is progress-oriented and you have to write generator function for simulated events or events interaction, `Akatosh` is fully object-oriented that events are encapsulated as `InstantEvent`/`ContinousEvent` with states, priority and a life-cycle. The actual impact of events are simply regular python functions. You could create events all at once, or create event within event. In addition, `Akatosh` is async which means event that are happening at the same simulated time will be executed simultaneously for real, unless they have different priority.

`Akatosh` also support `Resource`, provide all functionalities as it is in `Simpy` with extra utilities for telemetries collection and interaction with `Entity`. The `Entity` is unique to `Akatosh` which represents a abstract entity with a life-cycle, for example a follower. The `Entity` supports utility functions to interact with `Resource` and automatically releases all its occupied resources upon termination.

You probably already noticed that `Akatosh` is the name of "Dragon God of Time" in elder scroll serie, therefore the singleton class `Mundus` is the core of the simulation. The `Mundus` will schedule the events, move forward time and engage async execution.

To use `Akatosh`:

```bash
pip install -U Akatosh
```

A basic example is showing below, for more information please look at *Examples* and *API Reference*, full documentation is available at https://ulfaric.github.io/Akatosh/.

```py
from Akatosh.universe import universe
from Akatosh.resource import Resource
from Akatosh.entity import Entity
from Akatosh.event import Event

# create a resource with capacity of 100 and current level 50
res = Resource(100.0, 50.0)

# create a instance event happens at 0.9s
lock = Event(0.9,0.9, lambda: print("Unlocked!"))

# indicate a user entity should be created after lock event ended, wait till 1.1s.
user = Entity(lock, 1.1, "User")

# indicate user entity engage a event at 1.2s
@user.event(1.2,1.2, "Use Resource")
def user_event():
    if res.distribute(user, 1):
        print(res.level)
    else:
        print("Not enough resource")


# run simulation for 1.2s
universe.simulate(1.2)
```
