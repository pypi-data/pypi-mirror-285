import logging

from setuptools_scm import get_version, git, hg, Configuration
from setuptools_scm.fallbacks import parse_pkginfo
from setuptools_scm.version import guess_next_dev_version, get_local_node_and_date, ScmVersion


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
        root='..',
        parse=parse_version,
        version_scheme=guess_next_dev_version,
        local_scheme=get_local_node_and_date,
    )


def run_demo():
    print(get_scm_version())
    pass


if __name__ == '__main__':
    run_demo()
    pass
