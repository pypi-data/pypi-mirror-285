from typer import Context


def parse_context_args(ctx: Context):
    keys = []
    values = []
    for a in ctx.args:
        if a.startswith("--"):
            keys.append(a[2:])
        else:
            values.append(a)
    return dict(zip(keys, values))
