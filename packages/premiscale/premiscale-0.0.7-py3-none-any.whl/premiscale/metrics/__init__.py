"""
A portion of this module is dedicated to the MetricsCollector class, which oversees visiting every host and collecting
metrics and storing them in the appropriate backend database.

The other portion is dedicated to factory methods for building connections to the time-series and state databases.
"""


from __future__ import annotations

import logging

from typing import TYPE_CHECKING
from concurrent.futures import ThreadPoolExecutor
from setproctitle import setproctitle
from cattrs import unstructure
from time import sleep
from datetime import datetime, timedelta
from premiscale.hypervisor import build_hypervisor_connection


if TYPE_CHECKING:
    from typing import Iterator, List, Tuple
    # TODO: Update this to 'from premiscale.config._config import ConfigVersion as Config' once an ABC for Host is implemented.
    from premiscale.config.v1alpha1 import Config, Host
    from premiscale.metrics.state._base import State
    from premiscale.metrics.timeseries._base import TimeSeries


log = logging.getLogger(__name__)


def build_timeseries_connection(config: Config) -> TimeSeries:
    """
    Build a metrics collection class instance for storing metrics  hosts. Only one of
    these loops is created; metrics are published to influxdb for retrieval and query
    by the ASG loop, which evaluates on a per-ASG basis whether Actions need to be taken.

    Args:
        config (Config): The configuration object.

    Returns:
        TimeSeries: A time-series database interface.

    Raises:
        ValueError: If the time-series database type is unknown.
    """
    match config.controller.databases.timeseries.type:
        case 'memory':
            log.debug(f'Using local memory for time series database')
            from premiscale.metrics.timeseries.local import Local

            return Local(
                retention=timedelta(seconds=config.controller.databases.timeseries.retention),
                file=config.controller.databases.timeseries.dbfile
            )
        case 'influxdb':
            log.debug(f'Using InfluxDB for time series database')
            from premiscale.metrics.timeseries.influxdb import InfluxDB

            return InfluxDB(
                config.controller.databases.timeseries
            )
        case _:
            raise ValueError(f'Unknown timeseries database type: {config.controller.databases.timeseries.type}')


def build_state_connection(config: Config) -> State:
    """
    Build a state collection class.

    Args:
        config (Config): The configuration object.

    Returns:
        State: A state database interface.

    Raises:
        ValueError: If the state database type is unknown.
    """
    match config.controller.databases.state.type:
        case 'memory':
            # SQLite
            from premiscale.metrics.state.local import Local

            return Local(
                dbfile=config.controller.databases.state.dbfile
            )
        case 'mysql':
            from premiscale.metrics.state.mysql import MySQL

            connection = unstructure(config.controller.databases.state)
            del(connection['type'])

            return MySQL(**connection)
        case _:
            raise ValueError(f'Unknown state database type: {config.controller.databases.state.type}')


class MetricsCollector:
    """
    Oversee visiting every host and collecting metrics and storing them in the appropriate backend database.

    Args:
        config (Config): The configuration object.
        timeseries_enabled (bool): Whether to enable time-series data collection. Defaults to False.
    """
    def __init__(self, config: Config, timeseries_enabled: bool = False) -> None:
        self.timeseries_enabled = timeseries_enabled
        self.config = config

    def __call__(self) -> None:
        """
        Start the metrics collection subprocess.
        """
        setproctitle('metrics-collector')
        log.debug('Starting metrics collection subprocess')

        self._initialize_host()
        self._collectMetrics()

    def _initialize_host(self, host: Host | None = None) -> None:
        """
        Ensure hosts are tracked in the database as they're discovered, or, run through all hosts in the configuration file
        by not specifying any host.

        Args:
            host (Host | None): The host to initialize in the database (for forward compatibility). Defaults to None.
                If None, all hosts in the configuration file are initialized.
        """

        _start_time = datetime.now()

        stateConnection = build_state_connection(self.config)
        stateConnection.open()
        stateConnection.initialize()

        if host is not None:
            _host_dict = host.state()

            if not stateConnection.host_exists(host.name, host.address):
                stateConnection.host_create(**_host_dict)

            _end_time = datetime.now()

            log.debug(f'Host {host.name} initialized in {_end_time - _start_time}')

            return None

        for _h in self:
            if not stateConnection.host_exists(_h.name, _h.address):
                stateConnection.host_create(
                    **_h.state()
                )

        _end_time = datetime.now()
        _total_time = round((_end_time - _start_time).total_seconds(), 2)

        log.debug(f'All hosts initialized in state database in {_total_time}s')

    def __iter__(self) -> Iterator:
        """
        Create an iterator that visits every host specified in the configuration file.

        Returns:
            Iterator: An iterator that visits every host.
        """
        return iter(self.config.controller.autoscale.hosts)

    def __len__(self) -> int:
        """
        Return the number of hosts specified in the configuration file.

        Returns:
            int: The number of hosts.
        """
        return len(self.config.controller.autoscale.hosts)

    def __getitem__(self, subscript: int | slice) -> List[Host]:
        """
        Get a host by index or slice.

        Args:
            subscript (int | slice): The index or slice of the hosts to retrieve.

        Returns:
            List[Host]: List of hosts at the specified index or within the range of the slice.
        """
        if isinstance(subscript, slice):
            return self.config.controller.autoscale.hosts[subscript.start:subscript.stop:subscript.step]
        else:
            return [self.config.controller.autoscale.hosts[subscript]]

    def _collectMetrics(self) -> None:
        """
        Collect metrics from all hosts and store them in the appropriate backend database.
        """
        # Paginate through hosts to avoid queuing up a large number of jobs to visit hosts.
        maxpages = max(
            1,
            len(self) // self.config.controller.databases.maxHostConnectionThreads + (
                1 if len(self) % self.config.controller.databases.maxHostConnectionThreads > 0 else 0
            ),
            len(self) // (1 if (self.config.controller.databases.hostConnectionQueueSize is None) else self.config.controller.databases.hostConnectionQueueSize) + (
                1 if len(self) % (len(self) if (self.config.controller.databases.hostConnectionQueueSize is None) else self.config.controller.databases.hostConnectionQueueSize) > 0 else 0
            )
        )

        while True:
            collection_run_start = datetime.now()

            for page in range(0, maxpages):

                # Set a lower and upper bound for a slice of hosts to visit from the whole config.
                lower_bound = page * self.config.controller.databases.maxHostConnectionThreads
                _potential_upper_bound = (1 + page) * self.config.controller.databases.maxHostConnectionThreads
                upper_bound = _potential_upper_bound if _potential_upper_bound < len(self) else len(self)

                if lower_bound == upper_bound:
                    log.debug(f'No hosts to visit. Ensure you list managed hosts in the config file')
                    break

                log.debug(f'Collecting metrics for hosts {lower_bound + 1} to {upper_bound} of total {len(self)}')

                # Reset our collection of threads every paginated iteration over hosts.
                threads = []

                with ThreadPoolExecutor(max_workers=self.config.controller.databases.maxHostConnectionThreads) as executor:
                    for host in self[lower_bound:upper_bound]:
                        threads.append(
                            executor.submit(
                                self._collectHostMetrics,
                                host
                            )
                        )

                    for thread in threads:
                        if thread is not None:
                            thread.result()

            # Wait for the next collection interval, or start right away if collection took longer than that interval.

            collection_run_end = datetime.now()
            collection_run_duration = round((collection_run_end - collection_run_start).total_seconds(), 2)

            log.debug(f'Collection run took {collection_run_duration} seconds')

            if collection_run_duration < timedelta(seconds=self.config.controller.databases.collectionInterval).total_seconds():
                actual_sleep = round(self.config.controller.databases.collectionInterval - (collection_run_end - collection_run_start).total_seconds(), 2)
                log.debug(f'Waiting for {actual_sleep} seconds before revisiting every host')
                sleep(actual_sleep)
            else:
                log.warning(f'Collection took longer than the collection interval of {self.config.controller.databases.collectionInterval} seconds. Starting collection immediately')

    def _collectHostMetrics(self, host: Host) -> None:
        """
        Collect metrics for a single host over a readonly Libvirt connection and store them in the appropriate backend database.

        This method is intended to be called with a host argument from a ThreadPoolExecutor-based thread.

        Args:
            host (Host): The host object to collect metrics from.
        """
        timeseriesConnection: TimeSeries | None = None

        # Set up database interfaces.
        if self.timeseries_enabled:
            timeseriesConnection = build_timeseries_connection(self.config)
            timeseriesConnection.open()

        domain_timeseries: List[Tuple] = []

        with build_hypervisor_connection(host, readonly=True) as host_connection:

            # Exit early; instantiating the connection to the host failed and has already been logged.
            # We'll try again on the next iteration.
            if host_connection is None:
                return None

            log.debug(f'Connection to host {host.name} succeeded, collecting metrics')

            stateConnection = build_state_connection(self.config)
            stateConnection.open()

            # Diff current state and recorded state and update the state database. We
            # split reads and writes here to avoid locking the database for too long.
            if stateConnection.get_host(host.name, host.address) != (host_state := host.state()):
                log.debug(f'Host {host.name} has changed. Updating state database entry')
                stateConnection.host_update(
                    **host_state,
                )

            if timeseriesConnection is not None:
                # If time series data collection is enabled, collect and store both host and virtual machine time-series data about their performance.
                domain_timeseries = host_connection.timeseries()
            else:
                log.debug(f'Time series data collection is disabled. Skipping collection for host {host.name}')
                return None

        for domain in domain_timeseries:
            # vm :: Tuple[Dict, Dict, Dict, Dict]
            # each Dict is a different measurement by which we can scale on.
            log.debug(f'Inserting time series metrics for VM: {domain}')
            timeseriesConnection.insert_batch(domain)

        log.debug(f'Time series metrics currently stored: "{timeseriesConnection.get_all()}"')