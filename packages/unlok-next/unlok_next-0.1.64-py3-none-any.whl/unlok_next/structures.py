"""Strucutre Registration"""

try:
    from rekuest_next.structures.default import (
        PortScope,
        get_default_structure_registry,
        id_shrink,
    )
    from rekuest_next.widgets import SearchWidget

    from unlok_next.api.schema import RoomFragment, aget_room

    structure_reg = get_default_structure_registry()
    structure_reg.register_as_structure(
        RoomFragment,
        identifier="@lok/room",
        scope=PortScope.GLOBAL,
        aexpand=aget_room,
        ashrink=id_shrink,
    )

except ImportError as e:
    raise e
    print(e)
    structure_reg = None
