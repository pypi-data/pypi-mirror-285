from unlok_next.rath import UnlokRath, current_unlok_next_rath


def execute(operation, variables, rath: UnlokRath = None):
    rath = rath or current_unlok_next_rath.get()
    return operation(
        **rath.query(
            operation.Meta.document,
            operation.Arguments(**variables).dict(by_alias=True),
        ).data
    )


async def aexecute(operation, variables, rath: UnlokRath = None):
    print(operation, variables)
    rath = rath or current_unlok_next_rath.get()

    x = await rath.aquery(
        operation.Meta.document, operation.Arguments(**variables).dict(by_alias=True)
    )
    print(x)
    return operation(**x.data)


def subscribe(operation, variables, rath: UnlokRath = None):
    rath = rath or current_unlok_next_rath.get()

    for ev in rath.subscribe(
        operation.Meta.document, operation.Arguments(**variables).dict(by_alias=True)
    ):
        yield operation(**ev.data)


async def asubscribe(operation, variables, rath: UnlokRath = None):
    rath = rath or current_unlok_next_rath.get()
    async for event in rath.asubscribe(
        operation.Meta.document, operation.Arguments(**variables).dict(by_alias=True)
    ):
        yield operation(**event.data)
