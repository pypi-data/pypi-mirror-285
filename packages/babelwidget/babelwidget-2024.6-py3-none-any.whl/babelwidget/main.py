"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2023
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import importlib.util as mprt
import sys as sstm
import types as t
import typing as h
from os import sep as PATH_SEPARATOR
from pathlib import Path as path_t

base_h = h.TypeVar("base_h")
button_h = h.TypeVar("button_h")
color_h = h.TypeVar("color_h")
config_constant_h = h.TypeVar("config_constant_h")
dropdown_choice_h = h.TypeVar("dropdown_choice_h")
grid_lyt_h = h.TypeVar("grid_lyt_h")
group_h = h.TypeVar("group_h")
hbox_lyt_h = h.TypeVar("hbox_lyt_h")
image_h = h.TypeVar("image_h")
label_h = h.TypeVar("label_h")
menu_h = h.TypeVar("menu_h")
radio_choice_h = h.TypeVar("radio_choice_h")
scroll_container_h = h.TypeVar("scroll_container_h")
stack_h = h.TypeVar("stack_h")
tabs_h = h.TypeVar("tabs_h")
text_box_h = h.TypeVar("text_box_h")
text_line_h = h.TypeVar("text_line_h")
vbox_lyt_h = h.TypeVar("vbox_lyt_h")


class backend_p(h.Protocol):
    ALIGNED_CENTER: config_constant_h
    ALIGNED_HCENTER: config_constant_h
    ALIGNED_LEFT: config_constant_h
    ALIGNED_RIGHT: config_constant_h
    ALIGNED_TOP: config_constant_h
    BASE_PALETTE: config_constant_h
    DIALOG_ACCEPTATION: config_constant_h
    DIALOG_ACCEPT_OPEN: config_constant_h
    DIALOG_ACCEPT_SAVE: config_constant_h
    DIALOG_AUTO_OVERWRITE: config_constant_h
    DIALOG_MODE_ANY: config_constant_h
    DIALOG_MODE_EXISTING_FILE: config_constant_h
    DIALOG_MODE_FOLDER: config_constant_h
    FORMAT_RICH: config_constant_h
    LINE_NO_WRAP: config_constant_h
    SELECTABLE_TEXT: config_constant_h
    SIZE_EXPANDING: config_constant_h
    SIZE_FIXED: config_constant_h
    SIZE_MINIMUM: config_constant_h
    TAB_POSITION_EAST: config_constant_h
    WIDGET_TYPE: config_constant_h
    WORD_NO_WRAP: config_constant_h

    Color: h.Callable[[str], color_h]
    NewMessage: h.Callable
    AddMessageCanal: h.Callable[[h.Any, str, h.Callable], None]
    RemoveMessageCanal : h.Callable[[h.Any, str], None]

    qt_core_app_t: h.Any
    event_loop_t: h.Any

    base_t: base_h

    button_t: button_h
    dropdown_choice_t: dropdown_choice_h
    group_t: group_h
    image_t: image_h
    label_t: label_h
    menu_t: menu_h
    path_chooser_t: base_h
    radio_choice_t: radio_choice_h
    scroll_container_t: scroll_container_h
    stack_t: stack_h
    tabs_t: tabs_h
    text_box_t: text_box_h
    text_line_t: text_line_h

    grid_lyt_t: grid_lyt_h
    hbox_lyt_t: hbox_lyt_h
    vbox_lyt_t: vbox_lyt_h

    ShowErrorMessage: h.Callable[..., None]
    ShowMessage: h.Callable[..., None]


@d.dataclass(repr=False, eq=False)
class backend_t(backend_p):
    name: str

    def __post_init__(self) -> None:
        """"""
        base_path = path_t(__file__).parent
        package_path = base_path.parent
        path = base_path / "backend" / self.name
        if not path.is_dir():
            raise ValueError(f"Invalid backend folder: {path}.")

        standard_modules = set(sstm.stdlib_module_names).union(
            sstm.builtin_module_names
        )
        for node in path.rglob("*.py"):
            if node.is_file():
                relative = node.relative_to(package_path)
                name = str(relative.parent / relative.stem).replace(PATH_SEPARATOR, ".")
                spec = mprt.spec_from_file_location(name, node)
                module = mprt.module_from_spec(spec)
                sstm.modules[name] = module
                spec.loader.exec_module(module)

                for name in dir(module):
                    if name[0] == "_":
                        continue

                    element = getattr(module, name)
                    if not (
                        isinstance(element, t.ModuleType)
                        or (not hasattr(element, "__module__"))
                        or (element.__module__[0] == "_")
                        or (element.__module__ in standard_modules)
                    ):
                        setattr(self, name, element)


"""
COPYRIGHT NOTICE

This software is governed by the CeCILL  license under French law and
abiding by the rules of distribution of free software.  You can  use,
modify and/ or redistribute the software under the terms of the CeCILL
license as circulated by CEA, CNRS and INRIA at the following URL
"http://www.cecill.info".

As a counterpart to the access to the source code and  rights to copy,
modify and redistribute granted by the license, users are provided only
with a limited warranty  and the software's author,  the holder of the
economic rights,  and the successive licensors  have only  limited
liability.

In this respect, the user's attention is drawn to the risks associated
with loading,  using,  modifying and/or developing or reproducing the
software by the user in light of its specific status of free software,
that may mean  that it is complicated to manipulate,  and  that  also
therefore means  that it is reserved for developers  and  experienced
professionals having in-depth computer knowledge. Users are therefore
encouraged to load and test the software's suitability as regards their
requirements in conditions enabling the security of their systems and/or
data to be ensured and,  more generally, to use and operate it in the
same conditions as regards security.

The fact that you are presently reading this means that you have had
knowledge of the CeCILL license and that you accept its terms.

SEE LICENCE NOTICE: file README-LICENCE-utf8.txt at project source root.

This software is being developed by Eric Debreuve, a CNRS employee and
member of team Morpheme.
Team Morpheme is a joint team between Inria, CNRS, and UniCA.
It is hosted by the Centre Inria d'Université Côte d'Azur, Laboratory
I3S, and Laboratory iBV.

CNRS: https://www.cnrs.fr/index.php/en
Inria: https://www.inria.fr/en/
UniCA: https://univ-cotedazur.eu/
Centre Inria d'Université Côte d'Azur: https://www.inria.fr/en/centre/sophia/
I3S: https://www.i3s.unice.fr/en/
iBV: http://ibv.unice.fr/
Team Morpheme: https://team.inria.fr/morpheme/
"""
