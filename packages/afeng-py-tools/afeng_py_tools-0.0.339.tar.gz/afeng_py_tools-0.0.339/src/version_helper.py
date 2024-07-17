"""
this module is a hack only in place to allow for setuptools
to use the attribute for the versions

it works only if the backend-path of the build-system section
from pyproject.toml is respected
"""
from __future__ import annotations

import logging

from setuptools_scm import Configuration
from setuptools_scm import get_version
from setuptools_scm import git
from setuptools_scm import hg
from setuptools_scm.fallbacks import parse_pkginfo
from setuptools_scm.version import ScmVersion
from setuptools_scm.version import get_local_node_and_date
from setuptools_scm.version import guess_next_dev_version

log = logging.getLogger("setuptools_scm")


def parse_version(root: str, config: Configuration) -> ScmVersion:
    try_parse = [
        git.parse,
        parse_pkginfo,
        hg.parse,
        git.parse_archival,
        hg.parse_archival,
    ]
    for maybe_parse in try_parse:
        try:
            parsed = maybe_parse(root, config)
            if parsed is not None:
                return parsed
        except OSError as e:
            logging.warning("parse with %s failed with: %s", maybe_parse, e)


def get_scm_version() -> str:
    return get_version(
        # root='.',
        parse=parse_version,
        version_scheme=guess_next_dev_version,
        local_scheme=get_local_node_and_date,
    )


version: str


def __getattr__(name: str) -> str:
    if name == "version":
        global version
        version = '.'.join(get_scm_version().split('.')[0:3])
        return version
    raise AttributeError(name)
