import os
from pathlib import Path

from super_scad.private.PrivateMultiChildOpenScadCommand import PrivateMultiChildOpenScadCommand
from super_scad.private.PrivateOpenScadCommand import PrivateOpenScadCommand
from super_scad.private.PrivateSingleChildOpenScadCommand import PrivateSingleChildOpenScadCommand
from super_scad.scad.Context import Context
from super_scad.scad.ScadWidget import ScadWidget
from super_scad.scad.Unit import Unit


class Scad:
    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, unit_length_final: Unit):
        """
        Object constructor.

        :param unit_length_final: The unit of length used in the generated OpenSCAD code.
        """

        self.__project_home: Path = Path(os.getcwd()).resolve()
        """
        The current project's home directory.
        """

        self.__context = Context(project_home=self.__project_home, unit_length_final=unit_length_final)

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def project_home(self) -> Path:
        """
        Returns the current project's home directory.
        """
        return self.__project_home

    # ------------------------------------------------------------------------------------------------------------------
    @project_home.setter
    def project_home(self, project_home: Path) -> None:
        """
        Sets the current project's home directory.

        :param Path project_home: The current project's home directory.
        """
        self.__project_home = project_home

    # ------------------------------------------------------------------------------------------------------------------
    def run_super_scad(self, root_widget: ScadWidget, openscad_path: Path | str) -> None:
        """
        Runs SuperSCAD on a SuperSCAD widget and stores the generated OpenSCAD code.

        :param root_widget: The root SuperSCAD widget to build.
        :param openscad_path: The path to the file were to store the generated OpenSCAD code.
        """
        self.__run_super_scad_prepare(openscad_path)
        self.__run_super_scad_walk_build_tree(root_widget)
        self.__run_super_scad_finalize()

    # ------------------------------------------------------------------------------------------------------------------
    def __run_super_scad_prepare(self, openscad_path: Path | str) -> None:
        """
        Executes the required steps before running SuperSCAD.

        :param openscad_path: The path to the file were to store the generated OpenSCAD code.
        """
        self.__context.target_path = Path(openscad_path)
        self.__context.set_unit_length_current(self.__context.get_unit_length_final())
        self.__context.code_store.clear()
        self.__context.code_store.add_line('// Unit of length: {}'.format(Context.get_unit_length_final()))

    # ------------------------------------------------------------------------------------------------------------------
    def __run_super_scad_finalize(self) -> None:
        """
        Executes the required step after running SuperSCAD.
        """
        self.__context.code_store.add_line('')

        with open(self.__context.target_path, 'wt') as handle:
            handle.write(self.__context.code_store.get_code())

    # ------------------------------------------------------------------------------------------------------------------
    def __run_super_scad_walk_build_tree(self, parent_widget: ScadWidget) -> None:
        """
        Helper method for __run_super_scad. Runs recursively on the SubSCAD widget and its children until it finds a
        widget for an OpenSCAD command. This OpenSCAD command is used to generate the OpenSCAD code.

        :param parent_widget: The parent widget to build.
        """
        old_unit = Context.get_unit_length_current()
        child_widget = parent_widget.build(self.__context)
        Context.set_unit_length_current(old_unit)

        if isinstance(child_widget, PrivateOpenScadCommand):
            self.__context.code_store.add_line('{}{}'.format(child_widget.command,
                                                             child_widget.generate_args(self.__context)))

            if isinstance(child_widget, PrivateSingleChildOpenScadCommand):
                self.__context.code_store.add_line('{')
                self.__run_super_scad_walk_build_tree(child_widget.child)
                self.__context.code_store.add_line('}')

            elif isinstance(child_widget, PrivateMultiChildOpenScadCommand):
                self.__context.code_store.add_line('{')
                for child in child_widget.children:
                    self.__run_super_scad_walk_build_tree(child)
                self.__context.code_store.add_line('}')

            else:
                self.__context.code_store.append_to_last_line(';')

        else:
            if child_widget == parent_widget:
                # Only OpenSCAD commands are allowed to build themselves.
                ValueError(f'Widget {parent_widget.__class__} build itself.')

            self.__run_super_scad_walk_build_tree(child_widget)

# ----------------------------------------------------------------------------------------------------------------------
