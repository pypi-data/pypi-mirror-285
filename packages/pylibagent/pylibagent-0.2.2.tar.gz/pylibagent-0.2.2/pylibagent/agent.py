import asyncio
import json
import logging
import os
import random
import re
import signal
import socket
import time
from typing import Iterable, Optional
from aiohttp import ClientSession
from setproctitle import setproctitle
from .logger import setup_logger
from .check import CheckBase


class SendDataException(Exception):
    pass


def _convert_verify_ssl(val):
    if val is None or val.lower() in ['true', '1', 'y', 'yes']:
        return None  # None for default SSL check
    return False


def _fqdn():
    fqdn = socket.getaddrinfo(
        socket.gethostname(),
        0,
        flags=socket.AI_CANONNAME)[0][3].strip()
    assert fqdn, 'failed to read fqdn'
    return fqdn


def _join(*parts):
    return '/'.join((part.strip('/') for part in parts))


def _is_valid_version(version):
    check = re.compile(r'^\d+(\.\d+(\.\d+)?)?(\-[a-zA-Z0-9_-]+)?$')
    return isinstance(version, str) and bool(check.match(version))


class Agent:

    def __init__(self, key: str, version: str):
        setproctitle(f'{key}-agent')
        setup_logger()
        logging.warning(f'starting {key} agent v{version}')

        self.key: str = key
        self.version: str = version
        if not _is_valid_version(version):
            logging.error(f'invalid agent version: `{version}`')
            exit(1)

        self.asset_id_file: str = os.getenv('ASSET_ID', None)
        if self.asset_id_file is None:
            logging.error('missing environment variable `ASSET_ID`')
            exit(1)

        token = os.getenv('TOKEN', None)
        if token is None:
            logging.error('missing environment variable `TOKEN`')
            exit(1)

        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._headers = {'Authorization': f'Bearer {token}'}
        self._json_headers = {'Content-Type': 'application/json'}
        self._json_headers.update(self._headers)

        self.asset_id: Optional[int] = None
        self.api_uri: str = os.getenv('API_URI', 'https://api.infrasonar.com')
        self.verify_ssl = _convert_verify_ssl(os.getenv('VERIFY_SSL', '1'))
        if str.isdigit(self.asset_id_file):
            self.asset_id = int(self.asset_id_file)
        else:
            self._read_json()

    async def announce(self, asset_name: Optional[str] = None,
                       asset_kind: Optional[str] = None):
        """Announce the agent.

        Argument `asset_name` is only used if the agent is new (no asset Id
        exists) and if not given, the fqdn is used."""
        try:
            if self.asset_id is None:
                self.asset_id, name =\
                     await self._create_asset(asset_name, asset_kind)
                self._dump_json()
                logging.info(f'created agent {name} (Id: {self.asset_id})')
                return

            url = _join(self.api_uri, f'asset/{self.asset_id}')
            async with ClientSession(headers=self._headers) as session:
                async with session.get(
                        url,
                        params={'fields': 'name', 'collectors': 'key'},
                        ssl=self.verify_ssl) as r:
                    if r.status != 200:
                        msg = await r.text()
                        raise Exception(f'{msg} (error code: {r.status})')

                    resp = await r.json()
                    name = resp["name"]
                    collectors = resp["collectors"]

            for collector in collectors:
                if collector['key'] == self.key:
                    break
            else:
                # The collector is not assigned yet
                url = _join(
                    self.api_uri,
                    f'asset/{self.asset_id}/collector/{self.key}')
                try:
                    async with ClientSession(headers=self._headers) as session:
                        async with session.post(url, ssl=self.verify_ssl) as r:
                            if r.status != 204:
                                msg = await r.text()
                                raise Exception(
                                    f'{msg} (error code: {r.status})')
                except Exception as e:
                    msg = str(e) or type(e).__name__
                    logging.error(f'failed to assign collector: {msg}')

            logging.info(f'announced agent {name} (Id: {self.asset_id})')
            return

        except Exception as e:
            msg = str(e) or type(e).__name__
            logging.error(f'announce failed: {msg}')
            exit(1)

    async def send_data(self, check_key: str, data: dict,
                        timestamp: Optional[int] = None,
                        runtime: Optional[float] = None):
        # The latter strings shouldn't start with a slash. If they start with a
        # slash, then they're considered an "absolute path" and everything
        # before them is discarded.
        # https://stackoverflow.com/questions/1945920/
        # why-doesnt-os-path-join-work-in-this-case
        url = _join(
            self.api_uri,
            f'asset/{self.asset_id}',
            f'collector/{self.key}',
            f'check/{check_key}')

        timestamp = timestamp or int(time.time())
        data = {
            "version": self.version,
            "data": data,
            "timestamp": timestamp,
        }

        if runtime is not None:
            data["runtime"] = runtime

        try:
            async with ClientSession(headers=self._json_headers) as session:
                async with session.post(
                    url,
                    json=data,
                    ssl=self.verify_ssl
                ) as r:
                    if r.status != 204:
                        msg = await r.text()
                        raise Exception(f'{msg} (error code: {r.status})')

        except Exception as e:
            msg = str(e) or type(e).__name__
            raise SendDataException(
                f'failed to send data ({check_key}): {msg} (url: {url})')

    def start(self, checks: Iterable[CheckBase],
              asset_name: Optional[str] = None,
              asset_kind: Optional[str] = None):
        """Start the agent demonized.

        The `asset_name` argument is only used on the accounce when the asset
        is new and must be created. If not given, the fqdn is used.

        The `asset_kind` argument is only used on the accounce when the asset
        is new and must be created. If not given, the asset will be created
        with the default `Asset` kind.

        Argument `checks` must be an iterable containing subclasses of
        CheckBase. (the classes, not instances of the class)
        """
        signal.signal(signal.SIGINT, self._stop)
        signal.signal(signal.SIGTERM, self._stop)

        self._loop = asyncio.get_event_loop()
        try:
            self._loop.run_until_complete(
                self._start(checks, asset_name, asset_kind))
        except Exception:
            self._loop.run_until_complete(self._loop.shutdown_asyncgens())
            self._loop.close()

    def _stop(self, signame, *args):
        logging.warning(
            f'signal \'{signame}\' received, stop {self.key} agent')
        for task in asyncio.all_tasks():
            task.cancel()

    async def _start(self, checks: Iterable[CheckBase],
                     asset_name: Optional[str] = None,
                     asset_kind: Optional[str] = None):
        await self.announce(asset_name, asset_kind)
        checks = [self._check_loop(c) for c in checks]
        try:
            await asyncio.wait(checks)
        except asyncio.exceptions.CancelledError:
            pass

    async def _check_loop(self, check):
        if check.interval == 0:
            logging.error(f'check `{check.key}` is disabled')
            return

        ts = time.time()
        ts_next = int(ts + random.random() * check.interval) + 1
        timeout = check.interval * 0.8

        while True:
            if ts > ts_next:
                # This can happen when a computer clock has been changed
                logging.error('scheduled timestamp in the past; '
                              'maybe the computer clock has been changed?')
                ts_next = ts

            try:
                wait = int(ts_next - ts)
                for _ in range(wait):
                    await asyncio.sleep(1)
            except asyncio.CancelledError:
                logging.info(f'cancelled check: {check.key}')
                break
            ts = ts_next

            try:
                check_data = \
                    await asyncio.wait_for(check.run(), timeout=timeout)
                await self.send_data(check.key, check_data)
            except asyncio.TimeoutError:
                logging.error(f'check error ({check.key}): timed out')
            except SendDataException as e:
                logging.error(str(e))
            except Exception as e:
                msg = str(e) or type(e).__name__
                logging.error(f'check error ({check.key}): {msg}')
            else:
                logging.debug(f'check_loop ({check.key}): ok!')
            finally:
                ts = time.time()
                ts_next += check.interval

    async def _create_asset(self, asset_name: Optional[str] = None,
                            asset_kind: Optional[str] = None) -> int:
        url = _join(self.api_uri, 'container/id')
        async with ClientSession(headers=self._headers) as session:
            async with session.get(url, ssl=self.verify_ssl) as r:
                if r.status != 200:
                    msg = await r.text()
                    raise Exception(f'{msg} (error code: {r.status})')

                resp = await r.json()
                container_id = resp['containerId']

        url = _join(self.api_uri, f'container/{container_id}/asset')
        name = _fqdn() if asset_name is None else asset_name
        data = {"name": name}
        async with ClientSession(headers=self._json_headers) as session:
            async with session.post(url, json=data, ssl=self.verify_ssl) as r:
                if r.status != 201:
                    msg = await r.text()
                    raise Exception(f'{msg} (error code: {r.status})')

                resp = await r.json()
                asset_id = resp['assetId']

        try:
            url = _join(self.api_uri, f'asset/{asset_id}/collector/{self.key}')
            async with ClientSession(headers=self._headers) as session:
                async with session.post(url, ssl=self.verify_ssl) as r:
                    if r.status != 204:
                        msg = await r.text()
                        raise Exception(f'{msg} (error code: {r.status})')
        except Exception as e:
            msg = str(e) or type(e).__name__
            logging.error(f'failed to assign collector: {msg}')

        if asset_kind:
            data = {"kind": asset_kind}
            try:
                url = _join(self.api_uri, f'asset/{asset_id}/kind')
                async with ClientSession(
                        headers=self._json_headers) as session:
                    async with session.patch(url,
                                             json=data,
                                             ssl=self.verify_ssl) as r:
                        if r.status != 204:
                            msg = await r.text()
                            raise Exception(f'{msg} (error code: {r.status})')
            except Exception as e:
                msg = str(e) or type(e).__name__
                logging.error(f'failed to set asset kind: {msg}')

        return asset_id, name

    def _read_json(self):
        if not os.path.exists(self.asset_id_file):
            parent = os.path.dirname(self.asset_id_file)
            if not os.path.exists(parent):
                try:
                    os.mkdir(parent)
                except Exception as e:
                    msg = str(e) or type(e).__name__
                    logging.error(f"failed to create path: {parent} ({msg})")
                    exit(1)
            self._dump_json()
            return
        try:
            with open(self.asset_id_file, 'r') as fp:
                self.asset_id = json.load(fp)
                assert (
                    self.asset_id is None or isinstance(self.asset_id, int)), \
                    'invalid asset Id (must be null of integer)'

        except Exception as e:
            msg = str(e) or type(e).__name__
            logging.error(
                f'failed to read asset Id from file: {self.asset_id_file} '
                f'({msg})')
            exit(1)

    def _dump_json(self):
        try:
            with open(self.asset_id_file, 'w') as fp:
                json.dump(self.asset_id, fp)
        except Exception as e:
            msg = str(e) or type(e).__name__
            logging.error(
                f"failed to write file: {self.asset_id_file} ({msg})")
            exit(1)
