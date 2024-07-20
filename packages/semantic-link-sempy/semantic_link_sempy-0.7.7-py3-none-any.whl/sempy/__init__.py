from . import _version
from .fabric._environment import (
    _get_artifact_type,
    _get_environment,
    get_notebook_workspace_id,
    get_artifact_id,
    _on_fabric
)
from ._utils._log import _initialize_log


__version__ = _version.get_versions()['version']

_initialize_log(
    on_fabric=_on_fabric(),
    env=_get_environment(),
    notebook_workspace_id=get_notebook_workspace_id(),
    artifact_id=get_artifact_id(),
    artifact_type=_get_artifact_type()
)


def load_ipython_extension(ipython):
    """
    Load the %%dax extension into the IPython shell.

    Parameters
    ----------
    ipython : Any
        The IPython shell.
    """
    from sempy.fabric._daxmagics import DAXMagics

    # register magic
    dax_magics = DAXMagics(ipython)
    ipython.register_magics(dax_magics)

    # not working :(
    # # register auto complete
    # def dax_completers(self, event):
    #     import sempy.fabric as fabric

    #     return ["foobar"]
    #     # fabric.list_datasets()["Dataset Name"].values

    # ipython.set_hook('complete_command', dax_completers, re_key='%%dax')
