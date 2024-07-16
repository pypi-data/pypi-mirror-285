from __future__ import annotations

import attrs
import pytest
from aresponses import ResponsesMockServer

from instawow._version_check import is_outdated
from instawow.config import GlobalConfig

from .fixtures.http import Route


@pytest.mark.parametrize(
    '_iw_mock_aiohttp_requests',
    [set()],
    indirect=True,
)
async def test_is_outdated_works_in_variety_of_scenarios(
    monkeypatch: pytest.MonkeyPatch,
    iw_aresponses: ResponsesMockServer,
    iw_global_config_values: dict[str, object],
):
    global_config = GlobalConfig.from_values(iw_global_config_values).write()

    # version == '0+dev', version not cached
    with monkeypatch.context() as patcher:
        patcher.setattr('instawow.__version__', '0+dev')
        assert await is_outdated(global_config) == (False, '')

    # Update check disabled, version not cached
    assert await is_outdated(attrs.evolve(global_config, auto_update_check=False)) == (False, '')

    # Endpoint not responsive, version not cached
    with monkeypatch.context() as patcher:
        patcher.setattr('instawow.__version__', '0.1.0')
        iw_aresponses.add(
            **Route(
                '//pypi.org/simple/instawow',
                iw_aresponses.Response(status=500),
                repeat=1,
            ).to_aresponses_add_args()
        )
        assert await is_outdated(global_config) == (False, '0.1.0')

    # Endpoint responsive, version not cached and version different
    with monkeypatch.context() as patcher:
        patcher.setattr('instawow.__version__', '0.1.0')
        iw_aresponses.add(
            **Route(
                '//pypi.org/simple/instawow',
                {'versions': ['1.0.0']},
                repeat=1,
            ).to_aresponses_add_args()
        )
        assert await is_outdated(global_config) == (True, '1.0.0')

    # version == '0+dev', version cached
    with monkeypatch.context() as patcher:
        patcher.setattr('instawow.__version__', '0+dev')
        assert await is_outdated(global_config) == (False, '')

    # Update check disabled, version cached
    assert await is_outdated(attrs.evolve(global_config, auto_update_check=False)) == (False, '')

    # Endpoint not responsive, version cached
    with monkeypatch.context() as patcher:
        patcher.setattr('instawow.__version__', '0.1.0')
        iw_aresponses.add(
            **Route(
                '//pypi.org/simple/instawow',
                iw_aresponses.Response(status=500),
                repeat=1,
            ).to_aresponses_add_args()
        )
        assert await is_outdated(global_config) == (True, '1.0.0')

    # Endpoint responsive, version cached and version same
    with monkeypatch.context() as patcher:
        patcher.setattr('instawow.__version__', '0.1.0')
        iw_aresponses.add(
            **Route(
                '//pypi.org/simple/instawow',
                {'versions': ['1.0.0']},
                repeat=1,
            ).to_aresponses_add_args()
        )
        assert await is_outdated(global_config) == (True, '1.0.0')

    # Endpoint responsive, version cached and version different
    with monkeypatch.context() as patcher:
        patcher.setattr('instawow.__version__', '1.0.0')
        iw_aresponses.add(
            **Route(
                '//pypi.org/simple/instawow',
                {'versions': ['1.0.0']},
                repeat=1,
            ).to_aresponses_add_args()
        )
        assert await is_outdated(global_config) == (False, '1.0.0')
