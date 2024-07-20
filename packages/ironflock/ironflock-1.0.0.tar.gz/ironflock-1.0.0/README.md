# ironflock

## About

With this library you can publishing data to IronFlock fleet storage. When this library is used on a certain device the library automatically uses the private messaging realm (Unified Name Space) of the device's fleet and the data is collected in the respective fleet database.

So if you use the library in your app, the data collection will always be private to the app user's fleet.

## Usage

```python
import asyncio
from ironflock import IronFlock

# create a ironflock instance, which auto connects to the IronFlock Platform
# the ironflock instance handles authentication and reconnects when the connection is lost
rw = IronFlock()

async def main():
    while True:
        # publish an event (if connection is not established the publish is skipped)
        publication = await rw.publish("test.publish.com", {"temperature": 20})
        print(publication)
        await asyncio.sleep(3)


if __name__ == "__main__":
    # run the main coroutine
    asyncio.get_event_loop().create_task(main())
    # run the ironflock component
    rw.run()
```

## Options

The `IronFlock` `__init__` function can be configured with the following options:

```ts
{
    serial_number: string;
}
```

**serial_number**: Used to set the serial_number of the device if the `DEVICE_SERIAL_NUMBER` environment variable does not exist. It can also be used if the user wishes to authenticate as another device.

## Advanced Usage

If you need more control, e.g. acting on lifecycle events (`onJoin`, `onLeave`) take a look at
the [examples](./examples/) folder.


## Development

Install the necessary components if you don't have them already:

```shell
pip install --upgrade setuptools wheel twine
```

Build and publish a new pypi package:

```shell
python setup.py sdist bdist_wheel
twine upload dist/*
```

Check the package at https://pypi.org/project/ironflock/.