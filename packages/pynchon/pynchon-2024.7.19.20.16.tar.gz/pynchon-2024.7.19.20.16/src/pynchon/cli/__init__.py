""" pynchon.cli
"""

from fleks.cli import arguments  # noqa
from fleks.cli import click  # noqa

from . import options  # noqa


def yad(decorators):
    def decorator(f):
        for d in reversed(decorators):
            f = d(f)
        return f

    return decorator


def get_from_super(kls, name):
    def fxn(self, *args, **kwargs):
        return getattr(super(kls, self), name)(*args, **kwargs)

    fxn.__name__ = name
    return fxn


def extends_super(kls, name, extra_options=[]):
    """
    example usage:
        apply = cli.extends_super(Planner, 'apply', extra_options=[cli.options...])
    """
    fxn = get_from_super(kls, name)
    fxn = options_from(getattr(kls, name))(fxn)
    for o in extra_options:
        fxn = o(fxn)
    return fxn


def options_from(class_method):
    """ """
    assert callable(class_method) and hasattr(class_method, "__click_params__")
    from click import Option, option

    return yad(
        [
            option(
                *o.opts,
                default=o.default,
                is_flag=o.is_flag,
                envvar=o.envvar,
                flag_value=o.flag_value,
                multiple=o.multiple,
                help=o.help,
            )
            for o in class_method.__click_params__
            if isinstance(o, (Option,))
        ]
    )
