


def init_services(service_builder_registry):
    from .fluss import Fluss
    from .rath import FlussLinkComposition, FlussRath
    from rath.links.split import SplitLink
    from rath.contrib.fakts.links.aiohttp import FaktsAIOHttpLink
    from rath.contrib.fakts.links.graphql_ws import FaktsGraphQLWSLink
    from rath.contrib.herre.links.auth import HerreAuthLink
    from graphql import OperationType
    from herre import Herre
    from fakts import Fakts

    from arkitekt_next.model import Manifest

    from arkitekt_next.service_registry import (
        Params,
    )
    from arkitekt_next.model import Requirement

    class ArkitektNextFluss(Fluss):
        rath: FlussRath

    def build_arkitekt_next_fluss(fakts: Fakts, herre: Herre, params: Params, manifest: Manifest):
        return ArkitektNextFluss(
            rath=FlussRath(
                link=FlussLinkComposition(
                    auth=HerreAuthLink(herre=herre),
                    split=SplitLink(
                        left=FaktsAIOHttpLink(fakts_group="fluss", fakts=fakts),
                        right=FaktsGraphQLWSLink(fakts_group="fluss", fakts=fakts),
                        split=lambda o: o.node.operation != OperationType.SUBSCRIPTION,
                    ),
                )
            )
        )

    service_builder_registry.register(
        "fluss",
        build_arkitekt_next_fluss,
        Requirement(
            service="live.arkitekt.fluss",
            description="An instance of ArkitektNext fluss to retrieve graphs from",
        ),
    )
    