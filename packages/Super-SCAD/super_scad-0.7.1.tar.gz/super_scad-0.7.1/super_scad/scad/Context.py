import inspect
import os
from pathlib import Path

from super_scad.scad.ScadCodeStore import ScadCodeStore
from super_scad.scad.Unit import Unit


class Context:
    """
    The context for generating OpenSCAD from SuperSCAD.
    """

    # ------------------------------------------------------------------------------------------------------------------
    __unit_length_current: Unit = Unit.FREE
    """
    The current unit of length.
    """

    __unit_length_final: Unit = Unit.FREE
    """
    The unit of length used in the generated OpenSCAD code.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, project_home: Path, unit_length_final: Unit):
        """
        Object constructor.

        :param Path project_home: The home folder of the current project.
        :param unit_length_final: The unit of length used in the generated OpenSCAD code.
        """

        self.__project_home: Path = project_home
        """
        The home folder of the current project. 
        """

        self.__target_path: Path | None = None
        """
        The path to the OpenSCAD script that currently been generated.
        """

        self.__code_store: ScadCodeStore = ScadCodeStore()
        """
        The place were we store the generated OpenSCAD code.
        """

        self.__eps: float = 1E-2
        """
        Epsilon value for clear overlap.
        """

        self.__fa: float = 1.0
        """
        The minimum angle (in degrees) of each fragment. 
        Known in OpenSCAD as $fa, see https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Other_Language_Features#$fa.
        """

        self.__fs: float = 0.1
        """
        The minimum circumferential length of each fragment.
        Known in OpenSCAD as $fs, see https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Other_Language_Features#$fs.
        """

        self.__fn: int = 0
        """
        The number of fragments in 360 degrees. Values of 3 or more override $fa and $fs.
        Known in OpenSCAD as $fn, see https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Other_Language_Features#$fn.
        """

        self.__unit_length_final: Unit = unit_length_final
        """
        The unit of length.
        """

        self.__length_digits = 4
        """
        The number of decimal places of a length in the generated OpenSCAD code.
        """

        Context.set_unit_length_current(unit_length_final)
        Context.__set_unit_length_final(unit_length_final)

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def project_home(self) -> Path:
        """
        Returns the current project's home directory.
        """
        return self.__project_home

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def target_path(self) -> Path | None:
        """
        Returns the path to the OpenSCAD script that currently been generated.
        """
        return self.__target_path

    # ------------------------------------------------------------------------------------------------------------------
    @target_path.setter
    def target_path(self, target_path: str) -> None:
        """
        Set the path to the OpenSCAD script that currently been generated.
        """
        self.__target_path = Path(os.path.realpath(target_path))

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def length_digits(self) -> int:
        """
        Returns the number of decimal places of a length in the generated OpenSCAD code.
        """
        return self.__length_digits

    # ------------------------------------------------------------------------------------------------------------------
    def resolve_path(self, path: Path | str) -> Path:
        """
        Resolve a path relative from the caller script to a path relative to the project home.

        :param Path path: The path to resolve.
        """
        caller = Path(inspect.stack()[1].filename)
        absolute_path = Path(caller.parent.joinpath(path).resolve())

        if os.path.commonprefix([absolute_path, self.__project_home]) == str(self.__project_home):
            # works with python >=3.12 return absolute_path.relative_to(self.target_path.parent, walk_up=True)
            return Path(os.path.relpath(absolute_path, self.target_path.parent))

        return absolute_path

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def code_store(self) -> ScadCodeStore:
        """
        Returns code store.
        """
        return self.__code_store

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def eps(self) -> float:
        """
        Returns the epsilon value for clear overlap.
        """
        return self.__eps

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def resolution(self) -> float:
        """
        Returns the resolution of lengths in generated OpenSCAD code.
        """
        return 10 ** -self.__length_digits

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def fa(self) -> float:
        """
        Returns the minimum angle (in degrees) of each fragment.
        Known in OpenSCAD as $fa, see https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Other_Language_Features#$fa.
        """
        return self.__fa

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def fs(self) -> float:
        """
        Returns the minimum circumferential length of each fragment.
        Known in OpenSCAD as $fs, see https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Other_Language_Features#$fs.
        """
        return self.__fs

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def fn(self) -> int:
        """
        Returns the number of fragments in 360 degrees. Values of 3 or more override $fa and $fs.
        Known in OpenSCAD as $fn, see https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Other_Language_Features#$fn.
        """
        return self.__fn

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def __set_unit_length_final(__unit_length_final: Unit) -> None:
        """
        Sets the unit of length used in the generated OpenSCAD code.
        """
        Context.__unit_length_final = __unit_length_final

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def get_unit_length_final() -> Unit:
        """
        Returns the unit of length used in the generated OpenSCAD code.
        """
        return Context.__unit_length_final

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def set_unit_length_current(unit_length_current: Unit) -> None:
        """
        Sets the current unit of length.

        :param unit_length_current: The new current unit of length.
        """
        Context.__unit_length_current = unit_length_current

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def get_unit_length_current() -> Unit:
        """
        Returns the current unit of length.
        """
        return Context.__unit_length_current

    # ------------------------------------------------------------------------------------------------------------------
    def round_length(self, length: float) -> str:
        """
        Returns a length rounded to the desired number of digits.

        :param length: The length.
        """
        return str(round(float(length), self.__length_digits))

# ----------------------------------------------------------------------------------------------------------------------
