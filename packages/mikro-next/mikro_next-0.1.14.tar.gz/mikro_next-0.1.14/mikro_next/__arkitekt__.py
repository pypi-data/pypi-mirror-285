from pydantic import Field
from rath.links.file import FileExtraction
from rath.links.dictinglink import DictingLink
from rath.links.auth import AuthTokenLink



def init_services(service_builder_registry):
    from rath.contrib.fakts.links.aiohttp import FaktsAIOHttpLink
    from rath.links.split import SplitLink
    from rath.contrib.fakts.links.graphql_ws import FaktsGraphQLWSLink
    from rath.contrib.herre.links.auth import HerreAuthLink
    from fakts import Fakts
    from herre import Herre
    from arkitekt_next.service_registry import Params
    from arkitekt_next.model import Requirement


    from mikro_next.mikro_next import MikroNext
    from mikro_next.rath import MikroNextLinkComposition, MikroNextRath
    from rath.links.split import SplitLink
    from rath.contrib.fakts.links.aiohttp import FaktsAIOHttpLink
    from rath.contrib.fakts.links.graphql_ws import FaktsGraphQLWSLink
    from rath.contrib.herre.links.auth import HerreAuthLink
    from mikro_next.contrib.fakts.datalayer import FaktsDataLayer
    from mikro_next.links.upload import UploadLink
    from mikro_next.datalayer import DataLayer
    from graphql import OperationType
    from herre import Herre
    from fakts import Fakts

    from arkitekt_next.model import Manifest

    try:
        from rekuest_next.links.context import ContextLink
        from rath.links.compose import TypedComposedLink
        class ArkitektMikroNextLinkComposition(TypedComposedLink):
            fileextraction: FileExtraction = Field(default_factory=FileExtraction)
            """ A link that extracts files from the request and follows the graphql multipart request spec"""
            dicting: DictingLink = Field(default_factory=DictingLink)
            """ A link that converts basemodels to dicts"""
            upload: UploadLink
            """ A link that uploads supported data types like numpy arrays and parquet files to the datalayer"""
            auth: AuthTokenLink
            """ A link that adds the auth token to the request"""
            """ A link that splits the request into a http and a websocket request"""
            assignation: ContextLink = Field(default_factory=ContextLink)
            split: SplitLink
    except ImportError: 
    
        ArkitektMikroNextLinkComposition = MikroNextLinkComposition


    class ArkitektMikroNextRath(MikroNextRath):
        link: ArkitektMikroNextLinkComposition


    class ArkitektNextMikroNext(MikroNext):
        rath: ArkitektMikroNextRath
        datalayer: DataLayer


    def builder_mikro(fakts: Fakts, herre: Herre,  params: Params, manifest: Manifest):
        datalayer = FaktsDataLayer(fakts_group="datalayer", fakts=fakts)

        return ArkitektNextMikroNext(
            rath=ArkitektMikroNextRath(
                link=ArkitektMikroNextLinkComposition(
                    auth=HerreAuthLink(herre=herre),
                    upload=UploadLink(
                        datalayer=datalayer,
                    ),
                    split=SplitLink(
                        left=FaktsAIOHttpLink(fakts_group="mikro", fakts=fakts),
                        right=FaktsGraphQLWSLink(fakts_group="mikro", fakts=fakts),
                        split=lambda o: o.node.operation != OperationType.SUBSCRIPTION,
                    ),
                )
            ),
            datalayer=datalayer
        )
    
    def fake_builder(fakts,herre, params, manifest):
        return  FaktsDataLayer(fakts_group="datalayer", fakts=fakts)
        
    service_builder_registry.register("mikro", builder_mikro,Requirement(
            service="live.arkitekt.mikro",
            description="An instance of ArkitektNext Mikro to make requests to the user's data",
            optional=True,
        ),)
    service_builder_registry.register("datalayer", fake_builder, Requirement(
            service="live.arkitekt.datalayer",
            description="An instance of ArkitektNext Datalayer to make requests to the user's data",
            optional=True,
        ),)
    

    try:

        from rekuest_next.structures.default import (
            get_default_structure_registry,
            PortScope,
            id_shrink,
        )
        from rekuest_next.widgets import SearchWidget
        from mikro_next.api.schema import (
            ImageFragment,
            aget_image,
            SearchImagesQuery,
            DatasetFragment,
            aget_dataset,
        )
        from mikro_next.api.schema import (
            SnapshotFragment,
            aget_snapshot,
            SearchSnapshotsQuery,
        )

        structure_reg = get_default_structure_registry()
        structure_reg.register_as_structure(
            ImageFragment,
            identifier="@mikro/image",
            aexpand=aget_image,
            ashrink=id_shrink,
            scope=PortScope.GLOBAL,
            default_widget=SearchWidget(
                query=SearchImagesQuery.Meta.document, ward="mikro"
            ),
        )
        structure_reg.register_as_structure(
            SnapshotFragment,
            identifier="@mikro/snapshot",
            aexpand=aget_snapshot,
            ashrink=id_shrink,
            scope=PortScope.GLOBAL,
            default_widget=SearchWidget(
                query=SearchSnapshotsQuery.Meta.document, ward="mikro"
            ),
        )
        structure_reg.register_as_structure(
            DatasetFragment,
            identifier="@mikro/dataset",
            aexpand=aget_dataset,
            ashrink=id_shrink,
            scope=PortScope.GLOBAL,
            default_widget=SearchWidget(
                query=SearchImagesQuery.Meta.document, ward="mikro"
            ),
        )

    except ImportError:
        raise ImportError("Default structures not found")

    imported = True




