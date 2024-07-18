


def register_structures(structure_reg):

    from rekuest_next.structures.default import (
        PortScope,
        id_shrink,
    )
    from rekuest_next.widgets import SearchWidget
    from mikro_next.api.schema import (
        Image,
        aget_image,
        SearchImagesQuery,
        Dataset,
        Stage,
        aget_stage,
        File,
        aget_file,
        SearchStagesQuery,
        SearchFilesQuery,
        aget_rgb_context,
        RGBContext,
        aget_dataset,
    )
    from mikro_next.api.schema import (
        Snapshot,
        aget_snapshot,
        SearchSnapshotsQuery,
    )

    structure_reg.register_as_structure(
        Image,
        identifier="@mikro/image",
        aexpand=aget_image,
        ashrink=id_shrink,
        scope=PortScope.GLOBAL,
        default_widget=SearchWidget(
            query=SearchImagesQuery.Meta.document, ward="mikro"
        ),
    )
    structure_reg.register_as_structure(
        Snapshot,
        identifier="@mikro/snapshot",
        aexpand=aget_snapshot,
        ashrink=id_shrink,
        scope=PortScope.GLOBAL,
        default_widget=SearchWidget(
            query=SearchSnapshotsQuery.Meta.document, ward="mikro"
        ),
    )
    structure_reg.register_as_structure(
        Stage,
        identifier="@mikro/stage",
        aexpand=aget_stage,
        ashrink=id_shrink,
        scope=PortScope.GLOBAL,
        default_widget=SearchWidget(
            query=SearchStagesQuery.Meta.document, ward="mikro"
        ),
    )
    structure_reg.register_as_structure(
        Dataset,
        identifier="@mikro/dataset",
        aexpand=aget_dataset,
        ashrink=id_shrink,
        scope=PortScope.GLOBAL,
        default_widget=SearchWidget(
            query=SearchImagesQuery.Meta.document, ward="mikro"
        ),
    )
    structure_reg.register_as_structure(
        File,
        identifier="@mikro/file",
        aexpand=aget_file,
        ashrink=id_shrink,
        scope=PortScope.GLOBAL,
        default_widget=SearchWidget(
            query=SearchFilesQuery.Meta.document, ward="mikro"
        ),
    )
    structure_reg.register_as_structure(
        RGBContext,
        identifier="@mikro/rbgcontext",
        aexpand=aget_rgb_context,
        ashrink=id_shrink,
        scope=PortScope.GLOBAL,
    )
