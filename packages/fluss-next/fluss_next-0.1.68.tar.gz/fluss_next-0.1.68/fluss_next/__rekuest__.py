


def register_structures(structure_reg):
    from rekuest_next.structures.default import (
        get_default_structure_registry,
        PortScope,
        id_shrink,
    )
    from rekuest_next.widgets import SearchWidget

    from fluss_next.api.schema import (
        FlowFragment,
        SearchFlowsQuery,
        aget_flow,
        RunFragment,
        arun,
        SearchRunsQuery,
    )

    structure_reg = get_default_structure_registry()
    structure_reg.register_as_structure(
        FlowFragment,
        identifier="@fluss/flow",
        scope=PortScope.GLOBAL,
        aexpand=aget_flow,
        ashrink=id_shrink,
        default_widget=SearchWidget(query=SearchFlowsQuery.Meta.document, ward="fluss"),
    )
    structure_reg.register_as_structure(
        RunFragment,
        identifier="@fluss/run",
        scope=PortScope.GLOBAL,
        aexpand=arun,
        ashrink=id_shrink,
        default_widget=SearchWidget(query=SearchRunsQuery.Meta.document, ward="fluss"),
    )