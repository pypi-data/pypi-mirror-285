

from arkitekt_next.model import Manifest


def init_services(service_builder_registry):
    from .unlok import Unlok
    from .rath import UnlokLinkComposition, UnlokRath
    from rath.links.split import SplitLink
    from rath.contrib.fakts.links.aiohttp import FaktsAIOHttpLink
    from rath.contrib.fakts.links.graphql_ws import FaktsGraphQLWSLink
    from rath.contrib.herre.links.auth import HerreAuthLink
    from graphql import OperationType
    from herre import Herre
    from fakts import Fakts


    from arkitekt_next.service_registry import Params
    from arkitekt_next.model import Requirement


    class ArkitektNextUnlok(Unlok):
        rath: UnlokRath


    def build_arkitekt_unlok(fakts: Fakts, herre: Herre,  params: Params, manifest: Manifest):
        return ArkitektNextUnlok(
            rath=UnlokRath(
                link=UnlokLinkComposition(
                    auth=HerreAuthLink(herre=herre),
                    split=SplitLink(
                        left=FaktsAIOHttpLink(fakts_group="lok", fakts=fakts),
                        right=FaktsGraphQLWSLink(fakts_group="lok", fakts=fakts),
                        split=lambda o: o.node.operation != OperationType.SUBSCRIPTION,
                    ),
                )
            )
        )

    
        
    service_builder_registry.register("unlok", build_arkitekt_unlok, Requirement(
            service="live.arkitekt.lok",
            description="An instance of ArkitektNext Lok to authenticate the user",
        ))