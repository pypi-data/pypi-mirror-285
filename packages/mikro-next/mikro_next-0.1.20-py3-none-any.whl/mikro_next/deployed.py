from dokker import  mirror, Deployment
import os
from koil.composition import Composition
from .mikro_next import MikroNext
from rath.links.auth import ComposedAuthLink
from rath.links.aiohttp import AIOHttpLink
from rath.links.graphql_ws import GraphQLWSLink
from mikro_next.mikro_next import MikroNext
from mikro_next.rath import (
    MikroNextRath,
    UploadLink,
    SplitLink,
    MikroNextLinkComposition,
)
from mikro_next.datalayer import DataLayer
from graphql import OperationType

test_path = os.path.join(os.path.dirname(__file__), "deployments", "test")


def build_deployment() -> Deployment:
    setup = mirror(test_path)
    setup.add_health_check(
        url="http://localhost:7788/ht", service="mikro", timeout=5, max_retries=10
    )
    return setup


async def token_loader():
    return "johannes"


def build_deployed_mikro_next():
    datalayer = DataLayer(
        endpoint_url="http://localhost:7799",
    )

    y = MikroNextRath(
        link=MikroNextLinkComposition(
            auth=ComposedAuthLink(
                token_loader=token_loader,
                token_refresher=token_loader,
            ),
            upload=UploadLink(datalayer=datalayer),
            split=SplitLink(
                left=AIOHttpLink(endpoint_url="http://localhost:7788/graphql"),
                right=GraphQLWSLink(ws_endpoint_url="ws://localhost:7788/graphql"),
                split=lambda o: o.node.operation != OperationType.SUBSCRIPTION,
            ),
        ),
    )

    mikro = MikroNext(
        datalayer=datalayer,
        rath=y,
    )
    return mikro


class DeployedMikroNext(Composition):
    deployment: Deployment
    mikro: MikroNext


def deployed() -> DeployedMikroNext:
    return DeployedMikroNext(
        deployment=build_deployment(),
        mikro=build_deployed_mikro_next(),
    )
