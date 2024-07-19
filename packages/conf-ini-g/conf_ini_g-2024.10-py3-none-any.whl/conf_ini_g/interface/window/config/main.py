"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2021
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import inspect as nspt
import typing as h
from pathlib import Path as pl_path_t

from babelwidget.backend.generic.path_chooser import NewSelectedOutputDocument
from babelwidget.main import backend_t
from babelwidget.main import base_h as library_wgt_h
from conf_ini_g.interface.storage.config import INIConfig, SaveConfigToINIDocument
from conf_ini_g.interface.window.config.action import ActionButtonsLayout
from conf_ini_g.interface.window.config.advanced import AdvancedModeLayout
from conf_ini_g.interface.window.config.title import TitleLayout
from conf_ini_g.interface.window.section.collection import SectionsAndCategories
from conf_ini_g.interface.window.section.main import (
    any_section_h,
    controlled_section_t,
    free_section_t,
)
from conf_ini_g.phase.generic.config import AsStr
from conf_ini_g.phase.specification.config.main import config_t as specification_t
from conf_ini_g.phase.specification.parameter.main import (
    parameter_t as parameter_spec_t,
)
from conf_ini_g.phase.specification.section.specific import (
    any_section_h as any_section_spec_h,
)
from conf_ini_g.phase.specification.section.specific import (
    controlled_section_t as controlled_section_spec_t,
)
from conf_ini_g.phase.specification.section.specific import (
    free_section_t as free_section_spec_t,
)
from conf_ini_g.phase.typed.config.main import (
    TypedFromUntyped,
    WithConsumedUnits,
    typed_config_h,
)
from conf_ini_g.phase.untyped.config import ini_config_h


@d.dataclass(repr=False, eq=False)
class config_t(list[any_section_h]):
    """
    The class cannot use slots because it disables weak referencing, which is required.
    See error message below when using slots:
    TypeError: cannot create weak reference to 'config_t' object
    [...]
    File "[...]conf_ini_g/catalog/interface/window/backend/pyqt5/widget/choices.py", line 41, in SetFunction
        self.clicked.connect(function)
        │                    └ <bound method config_t.ToggleAdvancedMode of <conf_ini_g.interface.window.config.config_t object at [...]>>
        └ <conf_ini_g.catalog.interface.window.backend.pyqt5.widget.choices.radio_choice_wgt_h object at [...]>

    Widget might not cooperate well with list, in which case Python raises the
    following exception: TypeError: multiple bases have instance lay-out conflict
    To be safe, "sections" is a field instead of being part of the class definition.

    _widget: Both an access for interacting with widgets, and a reference keeper to
    prevent autonomous widgets from loosing their "liveness".
    """

    specification: specification_t
    ini_path: pl_path_t | None
    UpdateHistory: h.Callable[[pl_path_t | str], None] | None
    #
    backend: backend_t
    library_wgt: library_wgt_h
    #
    Action: h.Callable[[typed_config_h], None] = None
    #
    _widget: dict[str, library_wgt_h] = d.field(init=False, default_factory=dict)

    @classmethod
    def NewForSpecification(
        cls,
        title: str | None,
        specification: specification_t,
        ini_path: pl_path_t | None,
        backend: backend_t,
        /,
        *,
        history: h.Sequence[str] | None = None,
        UpdateHistory: h.Callable[[pl_path_t | str], None] | None = None,
        action: tuple[str, h.Callable[[typed_config_h], None]] = None,
        advanced_mode: bool = False,
    ) -> h.Self:
        """"""
        if ini_path is not None:
            if UpdateHistory is not None:
                UpdateHistory(ini_path)
            as_str = str(ini_path)
            if history is None:
                history = (as_str,)
            elif as_str not in history:
                history = list(history)
                history.append(as_str)

        if action is None:
            kwargs = {}
        else:
            kwargs = {"Action": action[1]}

        output = cls(
            specification=specification,
            ini_path=ini_path,
            backend=backend,
            library_wgt=backend.base_t(),
            UpdateHistory=UpdateHistory,
            **kwargs,
        )

        # --- Top-level widgets
        (
            title_lyt,
            ini_path_wgt,
            history_button,
            history_menu,
            close_button,
        ) = TitleLayout(
            title,
            specification,
            history,
            backend,
            ini_path,
            output.UpdateWithNewINI,
            output.library_wgt.close,
        )
        advanced_mode_lyt, adv_mode_wgt = AdvancedModeLayout(
            advanced_mode, backend, output.ToggleAdvancedMode
        )
        button_lyt, action_button, action_wgts = ActionButtonsLayout(
            action,
            ini_path is not None,
            backend,
            output.ShowInINIFormat,
            output.SaveConfig,
            output.LaunchAction,
            output.library_wgt.close,
        )
        output._widget["ini_path"] = ini_path_wgt
        output._widget["history_button"] = history_button
        output._widget["history_menu"] = history_menu
        output._widget["adv_mode"] = adv_mode_wgt
        output._widget["action"] = action_button
        output._widget["action_buttons"] = action_wgts
        output._widget["close"] = close_button

        # --- Sections
        sections, controlled_sections, category_selector = SectionsAndCategories(
            specification, None, backend
        )
        output.extend(sections)
        output._AssociateSectionsAndControllers(controlled_sections)
        output._widget["category_selector"] = category_selector

        # --- Layout...
        layout = backend.grid_lyt_t()
        if title_lyt is None:
            first_available_row = 0
        else:
            layout.addLayout(title_lyt, 0, 0, 1, 1)
            first_available_row = 1
        layout.addWidget(category_selector, first_available_row, 0, 1, 1)
        layout.addLayout(advanced_mode_lyt, first_available_row + 1, 0, 1, 1)
        layout.addLayout(button_lyt, first_available_row + 2, 0, 1, 1)

        output.library_wgt.setLayout(layout)
        # --- ...Layout

        return output

    def _AssociateSectionsAndControllers(
        self,
        controlled_sections: h.Sequence[
            tuple[controlled_section_t, controlled_section_spec_t]
        ],
        /,
    ) -> None:
        """"""
        for section, section_spec in controlled_sections:
            controller = section_spec.controller
            # Controller section cannot be controlled, so active parameters are in fact
            # all the parameters.
            parameter = self[controller.section].active_parameters[controller.parameter]
            value_wgt = parameter.value
            if hasattr(value_wgt, "SetFunction"):
                value_wgt.SetFunction(section.page_stack.setCurrentIndex)
            else:
                self.backend.ShowErrorMessage(
                    f"{controller.section}.{controller.parameter}: "
                    f'Controller has no "SetFunction" method; Disabling control.'
                )

    def ReassignCloseButtonTarget(self) -> None:
        """"""
        current = self.library_wgt
        main_window = None
        while current is not None:
            main_window = current
            current = current.parent()

        self._widget["close"].SetFunction(main_window.close)

    def SetValues(
        self, config: typed_config_h, units: dict[tuple[str, str], tuple[str, float]], /
    ) -> None:
        """"""
        for section in self:
            sct_name = section.spec_name
            if isinstance(section, free_section_t):
                for parameter in section:
                    prm_name = parameter.spec_name
                    parameter_spec = self.specification[sct_name][prm_name]
                    typed_section = config[sct_name]
                    if prm_name in typed_section:
                        parameter.value.Assign(
                            typed_section[prm_name], parameter_spec.type
                        )
                        unit = units.get((sct_name, prm_name), None)
                        if unit is not None:
                            parameter.unit.setText(unit[0])
                    elif parameter_spec.optional:
                        parameter.value.Assign(
                            parameter_spec.default, parameter_spec.type
                        )
            else:
                for controlling_value, parameters in section.items():
                    for parameter in parameters:
                        prm_name = parameter.spec_name
                        parameter_spec = self.specification[sct_name][
                            controlling_value
                        ][prm_name]
                        typed_section = config[sct_name]
                        if prm_name in typed_section:
                            parameter.value.Assign(
                                typed_section[prm_name], parameter_spec.type
                            )
                            unit = units.get((sct_name, prm_name), None)
                            if unit is not None:
                                parameter.unit.setText(unit[0])
                        elif parameter_spec.optional:
                            parameter.value.Assign(
                                parameter_spec.default, parameter_spec.type
                            )

    def ToggleAdvancedMode(self, advanced_mode: bool, /) -> None:
        """"""
        for section in self:
            section_spec = self.specification[section.spec_name]
            if section_spec.basic:
                should_check_parameters = True
            elif advanced_mode:
                section.library_wgt.setVisible(True)
                should_check_parameters = True
            else:
                section.library_wgt.setVisible(False)
                should_check_parameters = False

            if should_check_parameters:
                parameters = section.active_parameters
                parameter_specs = self._ActiveParameterSpcOfSection(section_spec)
                for parameter, parameter_spec in zip(parameters, parameter_specs):
                    if not parameter_spec.basic:
                        if advanced_mode:
                            parameter.SetVisible(True)
                        else:
                            parameter.SetVisible(False)

    def UpdateWithNewINI(self, ini_path: pl_path_t | str, /) -> None:
        """"""
        if isinstance(ini_path, str):
            ini_path = pl_path_t(ini_path)

        config_ini = INIConfig(ini_path)
        config_typed, config_units, config_comments, issues = TypedFromUntyped(
            config_ini, None, self.specification
        )
        if issues.__len__() > 0:
            self.backend.ShowErrorMessage("\n".join(issues), parent=self.library_wgt)
            return

        category_selector = self._widget["category_selector"]
        if isinstance(category_selector, self.backend.tabs_t):
            # Note: idx^th layout: category_selector.widget(t_idx).widget().layout().
            while category_selector.count() > 0:
                category_selector.removeTab(0)
        else:
            layout = category_selector.widget().layout()
            while layout.count() > 0:
                layout.itemAt(0).widget().setParent(None)

        self.clear()
        sections, controlled_sections, _ = SectionsAndCategories(
            self.specification, category_selector, self.backend
        )
        self.extend(sections)
        self._AssociateSectionsAndControllers(controlled_sections)
        self.SetValues(config_typed, config_units)
        self.ToggleAdvancedMode(self._widget["adv_mode"].true_btn.isChecked())

        self._widget["ini_path"].Assign(ini_path, None)
        self._widget["history_button"].setEnabled(True)
        if str(ini_path) not in (
            _elm.text() for _elm in self._widget["history_menu"].actions()
        ):
            self._widget["history_menu"].addAction(str(ini_path))

        if self.UpdateHistory is not None:
            self.UpdateHistory(ini_path)

    def _ActiveParameterSpcOfSection(
        self, section_spec: any_section_spec_h, /
    ) -> h.Sequence[parameter_spec_t]:
        """"""
        if isinstance(section_spec, free_section_spec_t):
            output = section_spec
        else:
            controller = section_spec.controller
            controller = self[controller.section].active_parameters[
                controller.parameter
            ]
            output = section_spec.ActiveParameters(controller.Text())

        return output

    def AsINI(self) -> ini_config_h:
        """"""
        return {_elm.spec_name: _elm.AsINI() for _elm in self}

    def LaunchAction(self) -> None:
        """"""
        config_full, units_full, _, issues = TypedFromUntyped(
            self.AsINI(), None, self.specification
        )
        if issues.__len__() > 0:
            self.backend.ShowErrorMessage("\n".join(issues), parent=self.library_wgt)
            return

        typed_config, issues = WithConsumedUnits(config_full, units_full)
        if issues.__len__() > 0:
            self.backend.ShowErrorMessage("\n".join(issues), parent=self.library_wgt)
            return

        self.setEnabled(False)
        self.backend.qt_core_app_t.processEvents()
        try:
            self.Action(typed_config)
        except Exception as exception:
            trace = nspt.trace()[-1]
            context = "\n".join(trace.code_context)
            self.backend.ShowErrorMessage(
                f"{trace.filename}@{trace.lineno}:{trace.function}\n"
                f"{context}\n"
                f"{exception}",
                parent=self.library_wgt,
            )
        self.setEnabled(True)

    def ShowInINIFormat(self) -> None:
        """"""
        config = AsStr(self.AsINI(), color="html")
        self.backend.ShowMessage("INI Config", "<tt>" + config + "<tt/>")

    def SaveConfig(self, new_ini: bool, /) -> None:
        """"""
        if new_ini:
            path = NewSelectedOutputDocument(
                "Save Config As",
                "Save Config As",
                self.backend,
                mode="document",
                valid_types={"Config files": ("ini", "INI")},
            )
        else:
            path = self.ini_path  # Will overwrite current INI document

        if path is not None:
            config = self.AsINI()
            issues = SaveConfigToINIDocument(config, path)
            if issues.__len__() > 0:
                self.backend.ShowErrorMessage("\n".join(issues), parent=self)
            else:
                self.ini_path = path

    def __getattr__(self, attribute: str, /) -> h.Any:
        """
        E.g., used for "show".
        """
        try:
            output = super().__getattribute__(attribute)
        except AttributeError:
            output = getattr(self.library_wgt, attribute)

        return output

    def __contains__(self, key: str, /) -> bool:
        """"""
        return any(_elm.spec_name == key for _elm in self)

    def __getitem__(self, key: str, /) -> any_section_h:
        """"""
        for section in self:
            if section.spec_name == key:
                return section

        raise KeyError(f"{key}: Not a section of config.")


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
