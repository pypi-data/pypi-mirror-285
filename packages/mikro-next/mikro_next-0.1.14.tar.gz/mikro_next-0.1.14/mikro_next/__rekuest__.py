


def register_structures(structure_reg):

    from rekuest_next.structures.default import (
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
