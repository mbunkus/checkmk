#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# TODO This module should be freed from base deps.

import os.path
from pathlib import Path
from typing import Final

from cmk.utils.agentdatatype import AgentRawData
from cmk.utils.hostaddress import HostAddress, HostName

from cmk.snmplib import SNMPBackendEnum, SNMPRawData

from cmk.fetchers import Fetcher, NoFetcher, NoFetcherError, SNMPScanConfig, TLSConfig
from cmk.fetchers.filecache import (
    AgentFileCache,
    FileCache,
    FileCacheMode,
    FileCacheOptions,
    MaxAge,
    NoCache,
    SNMPFileCache,
)

from cmk.checkengine.fetcher import FetcherType, SourceInfo, SourceType
from cmk.checkengine.parser import SectionNameCollection

from cmk.base.config import ConfigCache

from ._api import Source

__all__ = [
    "SNMPSource",
    "MgmtSNMPSource",
    "IPMISource",
    "ProgramSource",
    "PushAgentSource",
    "TCPSource",
    "SpecialAgentSource",
    "PiggybackSource",
    "MissingIPSource",
    "MissingSourceSource",
]

# Singleton
_NO_CACHE: Final[FileCache] = NoCache()


class SNMPSource(Source[SNMPRawData]):
    fetcher_type: Final = FetcherType.SNMP
    source_type: Final = SourceType.HOST

    def __init__(
        self,
        config_cache: ConfigCache,
        host_name: HostName,
        ipaddress: HostAddress,
        *,
        scan_config: SNMPScanConfig,
        max_age: MaxAge,
        selected_sections: SectionNameCollection,
        backend_override: SNMPBackendEnum | None,
        stored_walk_path: Path,
        walk_cache_path: Path,
        file_cache_path: Path,
    ) -> None:
        super().__init__()
        self.config_cache: Final = config_cache
        self.host_name: Final = host_name
        self.ipaddress: Final = ipaddress
        self._scan_config: Final = scan_config
        self._max_age: Final = max_age
        self._selected_sections: Final = selected_sections
        self._backend_override: Final = backend_override
        self._stored_walk_path: Final = stored_walk_path
        self._walk_cache_path: Final = walk_cache_path
        self._file_cache_path: Final = file_cache_path

    def source_info(self) -> SourceInfo:
        return SourceInfo(
            self.host_name,
            self.ipaddress,
            "snmp",
            self.fetcher_type,
            self.source_type,
        )

    def fetcher(self) -> Fetcher[SNMPRawData]:
        return self.config_cache.make_snmp_fetcher(
            self.host_name,
            self.ipaddress,
            scan_config=self._scan_config,
            selected_sections=self._selected_sections,
            stored_walk_path=self._stored_walk_path,
            walk_cache_path=self._walk_cache_path,
            source_type=self.source_type,
            backend_override=self._backend_override,
        )

    def file_cache(
        self, *, simulation: bool, file_cache_options: FileCacheOptions
    ) -> FileCache[SNMPRawData]:
        return SNMPFileCache(
            path_template=os.path.join(
                self._file_cache_path, self.source_info().ident, "{mode}", str(self.host_name)
            ),
            max_age=self._max_age,
            simulation=simulation,
            use_only_cache=file_cache_options.use_only_cache,
            file_cache_mode=file_cache_options.file_cache_mode(),
        )


class MgmtSNMPSource(Source[SNMPRawData]):
    fetcher_type: Final = FetcherType.SNMP
    source_type: Final = SourceType.MANAGEMENT

    def __init__(
        self,
        config_cache: ConfigCache,
        host_name: HostName,
        ipaddress: HostAddress,
        *,
        scan_config: SNMPScanConfig,
        max_age: MaxAge,
        selected_sections: SectionNameCollection,
        backend_override: SNMPBackendEnum | None,
        stored_walk_path: Path,
        walk_cache_path: Path,
        file_cache_path: Path,
    ) -> None:
        super().__init__()
        self.config_cache: Final = config_cache
        self.host_name: Final = host_name
        self.ipaddress: Final = ipaddress
        self._max_age: Final = max_age
        self._scan_config: Final = scan_config
        self._selected_sections: Final = selected_sections
        self._backend_override: Final = backend_override
        self._stored_walk_path: Final = stored_walk_path
        self._walk_cache_path: Final = walk_cache_path
        self._file_cache_path: Final = file_cache_path

    def source_info(self) -> SourceInfo:
        return SourceInfo(
            self.host_name,
            self.ipaddress,
            "mgmt_snmp",
            self.fetcher_type,
            self.source_type,
        )

    def fetcher(self) -> Fetcher[SNMPRawData]:
        return self.config_cache.make_snmp_fetcher(
            self.host_name,
            self.ipaddress,
            scan_config=self._scan_config,
            selected_sections=self._selected_sections,
            stored_walk_path=self._stored_walk_path,
            walk_cache_path=self._walk_cache_path,
            source_type=self.source_type,
            backend_override=self._backend_override,
        )

    def file_cache(
        self, *, simulation: bool, file_cache_options: FileCacheOptions
    ) -> FileCache[SNMPRawData]:
        return SNMPFileCache(
            path_template=os.path.join(
                self._file_cache_path, self.source_info().ident, "{mode}", str(self.host_name)
            ),
            max_age=self._max_age,
            simulation=simulation,
            use_only_cache=file_cache_options.use_only_cache,
            file_cache_mode=file_cache_options.file_cache_mode(),
        )


class IPMISource(Source[AgentRawData]):
    fetcher_type: Final = FetcherType.IPMI
    source_type: Final = SourceType.MANAGEMENT

    def __init__(
        self,
        config_cache: ConfigCache,
        host_name: HostName,
        ipaddress: HostAddress,
        *,
        max_age: MaxAge,
        file_cache_path: Path,
    ) -> None:
        super().__init__()
        self.config_cache: Final = config_cache
        self.host_name: Final = host_name
        self.ipaddress: Final = ipaddress
        self._max_age: Final = max_age
        self._file_cache_path: Final = file_cache_path

    def source_info(self) -> SourceInfo:
        return SourceInfo(
            self.host_name,
            self.ipaddress,
            "mgmt_ipmi",
            self.fetcher_type,
            self.source_type,
        )

    def fetcher(self) -> Fetcher[AgentRawData]:
        return self.config_cache.make_ipmi_fetcher(self.host_name, self.ipaddress)

    def file_cache(
        self, *, simulation: bool, file_cache_options: FileCacheOptions
    ) -> FileCache[AgentRawData]:
        return AgentFileCache(
            path_template=os.path.join(
                self._file_cache_path, self.source_info().ident, str(self.host_name)
            ),
            max_age=self._max_age,
            simulation=simulation,
            use_only_cache=file_cache_options.use_only_cache,
            file_cache_mode=file_cache_options.file_cache_mode(),
        )


class ProgramSource(Source[AgentRawData]):
    fetcher_type: Final = FetcherType.PROGRAM
    source_type: Final = SourceType.HOST

    def __init__(
        self,
        config_cache: ConfigCache,
        host_name: HostName,
        ipaddress: HostAddress | None,
        *,
        program: str,
        max_age: MaxAge,
        file_cache_path: Path,
    ) -> None:
        super().__init__()
        self.config_cache: Final = config_cache
        self.host_name: Final = host_name
        self.ipaddress: Final = ipaddress
        self.program: Final = program
        self._max_age: Final = max_age
        self._file_cache_path: Final = file_cache_path

    def source_info(self) -> SourceInfo:
        return SourceInfo(
            self.host_name,
            self.ipaddress,
            "agent",
            self.fetcher_type,
            self.source_type,
        )

    def fetcher(self) -> Fetcher[AgentRawData]:
        return self.config_cache.make_program_fetcher(
            self.host_name, self.ipaddress, program=self.program, stdin=None
        )

    def file_cache(
        self, *, simulation: bool, file_cache_options: FileCacheOptions
    ) -> FileCache[AgentRawData]:
        return AgentFileCache(
            path_template=os.path.join(self._file_cache_path, str(self.host_name)),
            max_age=self._max_age,
            simulation=simulation,
            use_only_cache=file_cache_options.use_only_cache,
            file_cache_mode=file_cache_options.file_cache_mode(),
        )


class PushAgentSource(Source[AgentRawData]):
    fetcher_type: Final = FetcherType.PUSH_AGENT
    source_type: Final = SourceType.HOST

    def __init__(
        self,
        host_name: HostName,
        ipaddress: HostAddress | None,
        *,
        max_age: MaxAge,
        file_cache_path: Path,
    ) -> None:
        super().__init__()
        self.host_name: Final = host_name
        self.ipaddress: Final = ipaddress
        self._max_age: Final = max_age
        self._file_cache_path: Final = file_cache_path

    def source_info(self) -> SourceInfo:
        return SourceInfo(
            self.host_name,
            self.ipaddress,
            "push-agent",
            self.fetcher_type,
            self.source_type,
        )

    def fetcher(self) -> Fetcher[AgentRawData]:
        return NoFetcher(NoFetcherError.NO_FETCHER)

    def file_cache(
        self, *, simulation: bool, file_cache_options: FileCacheOptions
    ) -> FileCache[AgentRawData]:
        return AgentFileCache(
            path_template=os.path.join(
                self._file_cache_path, self.source_info().ident, str(self.host_name), "agent_output"
            ),
            max_age=(
                MaxAge.unlimited()
                if simulation or file_cache_options.use_outdated
                else self._max_age
            ),
            simulation=simulation,
            use_only_cache=True,
            file_cache_mode=(
                # Careful: at most read-only!
                FileCacheMode.DISABLED
                if file_cache_options.disabled
                else FileCacheMode.READ
            ),
        )


class TCPSource(Source[AgentRawData]):
    fetcher_type: Final = FetcherType.TCP
    source_type: Final = SourceType.HOST

    def __init__(
        self,
        config_cache: ConfigCache,
        host_name: HostName,
        ipaddress: HostAddress,
        *,
        max_age: MaxAge,
        file_cache_path: Path,
        tls_config: TLSConfig,
    ) -> None:
        super().__init__()
        self.config_cache: Final = config_cache
        self.host_name: Final = host_name
        self.ipaddress: Final = ipaddress
        self._max_age: Final = max_age
        self._file_cache_path: Final = file_cache_path
        self._tls_config: Final = tls_config

    def source_info(self) -> SourceInfo:
        return SourceInfo(
            self.host_name,
            self.ipaddress,
            "agent",
            self.fetcher_type,
            self.source_type,
        )

    def fetcher(self) -> Fetcher[AgentRawData]:
        return self.config_cache.make_tcp_fetcher(
            self.host_name,
            self.ipaddress,
            tls_config=self._tls_config,
        )

    def file_cache(
        self, *, simulation: bool, file_cache_options: FileCacheOptions
    ) -> FileCache[AgentRawData]:
        return AgentFileCache(
            path_template=os.path.join(self._file_cache_path, str(self.host_name)),
            max_age=self._max_age,
            simulation=simulation,
            use_only_cache=(
                file_cache_options.tcp_use_only_cache or file_cache_options.use_only_cache
            ),
            file_cache_mode=file_cache_options.file_cache_mode(),
        )


class SpecialAgentSource(Source[AgentRawData]):
    fetcher_type: Final = FetcherType.SPECIAL_AGENT
    source_type: Final = SourceType.HOST

    def __init__(
        self,
        config_cache: ConfigCache,
        host_name: HostName,
        ipaddress: HostAddress | None,
        *,
        max_age: MaxAge,
        agent_name: str,
        stdin: str | None,
        cmdline: str,
        file_cache_path: Path,
    ) -> None:
        super().__init__()
        self.config_cache: Final = config_cache
        self.host_name: Final = host_name
        self.ipaddress: Final = ipaddress
        self._max_age: Final = max_age
        self._agent_name: Final = agent_name
        self._stdin: Final = stdin
        self._cmdline: Final = cmdline
        self._file_cache_path: Final = file_cache_path

    def source_info(self) -> SourceInfo:
        return SourceInfo(
            self.host_name,
            self.ipaddress,
            f"special_{self._agent_name}",
            self.fetcher_type,
            self.source_type,
        )

    def fetcher(self) -> Fetcher[AgentRawData]:
        return self.config_cache.make_special_agent_fetcher(
            cmdline=self._cmdline,
            stdin=self._stdin,
        )

    def file_cache(
        self, *, simulation: bool, file_cache_options: FileCacheOptions
    ) -> FileCache[AgentRawData]:
        return AgentFileCache(
            path_template=os.path.join(
                self._file_cache_path, self.source_info().ident, str(self.host_name)
            ),
            max_age=self._max_age,
            simulation=simulation,
            use_only_cache=file_cache_options.use_only_cache,
            file_cache_mode=file_cache_options.file_cache_mode(),
        )


class PiggybackSource(Source[AgentRawData]):
    fetcher_type: Final = FetcherType.PIGGYBACK
    source_type: Final = SourceType.HOST

    def __init__(
        self,
        config_cache: ConfigCache,
        host_name: HostName,
        ipaddress: HostAddress | None,
    ) -> None:
        super().__init__()
        self.config_cache: Final = config_cache
        self.host_name: Final = host_name
        self.ipaddress: Final = ipaddress

    def source_info(self) -> SourceInfo:
        return SourceInfo(
            self.host_name,
            self.ipaddress,
            "piggyback",
            self.fetcher_type,
            self.source_type,
        )

    def fetcher(self) -> Fetcher[AgentRawData]:
        return self.config_cache.make_piggyback_fetcher(self.host_name, self.ipaddress)

    def file_cache(
        self, *, simulation: bool, file_cache_options: FileCacheOptions
    ) -> FileCache[AgentRawData]:
        return _NO_CACHE


class MissingIPSource(Source):
    fetcher_type: Final = FetcherType.NONE
    source_type: Final = SourceType.HOST

    def __init__(self, host_name: HostName, ipaddress: None, ident: str) -> None:
        super().__init__()
        self.host_name: Final = host_name
        self.ipaddress: Final = ipaddress
        self.ident: Final = ident

    def source_info(self) -> SourceInfo:
        return SourceInfo(
            self.host_name,
            self.ipaddress,
            self.ident,
            self.fetcher_type,
            self.source_type,
        )

    def fetcher(self) -> Fetcher:
        return NoFetcher(NoFetcherError.MISSING_IP)

    def file_cache(self, *, simulation: bool, file_cache_options: FileCacheOptions) -> FileCache:
        return _NO_CACHE


class MissingSourceSource(Source):
    fetcher_type: Final = FetcherType.NONE
    source_type: Final = SourceType.HOST

    def __init__(self, host_name: HostName, ipaddress: HostAddress | None, ident: str) -> None:
        super().__init__()
        self.host_name: Final = host_name
        self.ipaddress: Final = ipaddress
        self.ident: Final = ident

    def source_info(self) -> SourceInfo:
        return SourceInfo(
            self.host_name,
            self.ipaddress,
            self.ident,
            self.fetcher_type,
            self.source_type,
        )

    def fetcher(self) -> Fetcher:
        return NoFetcher(NoFetcherError.NO_FETCHER)

    def file_cache(self, *, simulation: bool, file_cache_options: FileCacheOptions) -> FileCache:
        return _NO_CACHE
