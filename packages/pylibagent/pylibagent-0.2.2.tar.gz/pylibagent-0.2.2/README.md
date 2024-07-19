[![CI](https://github.com/infrasonar/python-libagent/workflows/CI/badge.svg)](https://github.com/infrasonar/python-libagent/actions)
[![Release Version](https://img.shields.io/github/release/infrasonar/python-libagent)](https://github.com/infrasonar/python-libagent/releases)

# Python library for building InfraSonar Agents

This library is created for building [InfraSonar](https://infrasonar.com) agents.

## Installation

```
pip install pylibagent
```

## Environment variables

Variable                    | Default                       | Description
----------------------------|-------------------------------|-------------------
`TOKEN`                     | _required_                    | Token to connect to.
`ASSET_ID`                  | _required_                    | Asset Id or file location where the Agent asset Id is stored _(e.g `123` or `/var/infrasonar/asset_id.json`)_.
`API_URI`                   | https://api.infrasonar.com    | InfraSonar API.
`VERIFY_SSL`                | `1`                           | Verify SSL certificate, 0 _(=disabled)_ or 1 _(=enabled)_.
`LOG_LEVEL`                 | `warning`                     | Log level _(error, warning, info, debug)_.
`LOG_COLORIZED`             | `0`                           | Log colorized, 0 _(=disabled)_ or 1 _(=enabled)_.
`LOG_FMT`                   | `%y%m...`                     | Default format is `%y%m%d %H:%M:%S`.


## Usage (Demonized agent)

Building an InfraSonar demonized agent.

```python
from pylibagent.agent import Agent
from pylibagent.check import CheckBase

__version__ = "0.1.0"


class SampleCheck(CheckBase):

    key = "sample"
    interval = 300

    @classmethod
    async def run(cls):
        return {
            "type": [
                {
                    "name": "item",
                    "metric": 123
                }
            ]
        }


if __name__ == "__main__":
    collector_key = "sample"
    version = "0.1.0"
    checks = [SampleCheck]

    Agent(collector_key, version).start(checks)
```


## Usage (Non-demonized agent)

Building an InfraSonar agent.

```python
import asyncio
from pylibagent.agent import Agent

__version__ = "0.1.0"


async def main():
    version = "0.1.0"
    collector_key = "sample"
    check_key = "sample"

    agent = Agent(collector_key, version)
    await agent.announce()  # optionally, we can provide an initial asset name
    await agent.send_data(check_key, {
        "type": [
            {
                "name": "item",
                "metric": 123
            }
        ]
    })


if __name__ == "__main__":
    asyncio.run(main())
```
