import re
from typing import Any, Dict, List, Set, Tuple

from super_scad.scad.Context import Context
from super_scad.scad.ScadWidget import ScadWidget
from super_scad.type.Color import Color
from super_scad.type.Point2 import Point2
from super_scad.type.Point3 import Point3
from super_scad.type.Size2 import Size2
from super_scad.type.Size3 import Size3


class PrivateOpenScadCommand(ScadWidget):
    """
    Widget for creating OpenSCAD commands.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, command: str, args: Dict[str, Any]):
        """
        Object constructor.

        :param command: The name of the OpenSCAD command.
        :param args: The arguments of the OpenSCAD command.
        """
        ScadWidget.__init__(self, args=args)

        self._command: str = command
        """
        The name of the OpenSCAD command.
        """

    # ------------------------------------------------------------------------------------------------------------------
    def build(self, context: Context) -> ScadWidget:
        """
        Builds a SuperSCAD widget.

        :param context: The build context.
        """
        return self

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def command(self) -> str:
        """
        Returns the name of the OpenSCAD command.
        """
        return self._command

    # ------------------------------------------------------------------------------------------------------------------
    def argument_map(self) -> Dict[str, str | None]:
        """
        Returns the map from SuperSCAD arguments to OpenSCAD arguments.
        """
        return {}

    # ------------------------------------------------------------------------------------------------------------------
    def argument_lengths(self) -> Set[str]:
        """
        Returns the set with arguments that are lengths.
        """
        return set()

    # ------------------------------------------------------------------------------------------------------------------
    def generate_args(self, context: Context) -> str:
        """
        Returns the arguments of the OpenSCAD command.
        """
        argument_map = self.argument_map()
        argument_lengths = self.argument_lengths()

        args_as_str = '('
        first = True
        for key, value in self._args.items():
            if not first:
                args_as_str += ', '
            else:
                first = False

            real_name = argument_map.get(key, key)
            real_value = self.uc(value) if real_name in argument_lengths else value

            real_value = self.__format_argument(context, real_value)

            if real_name is None:
                args_as_str += '{}'.format(real_value)
            else:
                args_as_str += '{} = {}'.format(real_name, real_value)
        args_as_str += ')'

        return args_as_str

    # ------------------------------------------------------------------------------------------------------------------
    def __format_argument(self, context: Context, argument: Any) -> str:
        """
        Returns an argument of the OpenSCAD command.

        :param context: The build context.
        :param argument: The argument of OpenSCAD command.
        """
        if isinstance(argument, float):
            # xxx Distinguish between length, scale, and angle.
            argument = context.round_length(argument)
            if argument == '-0.0':
                argument = '0.0'

            return argument

        if isinstance(argument, Point2):
            return "[{}, {}]".format(self.__format_argument(context, float(argument.x)),
                                     self.__format_argument(context, float(argument.y)))

        if isinstance(argument, Point3):
            return "[{}, {}, {}]".format(self.__format_argument(context, float(argument.x)),
                                         self.__format_argument(context, float(argument.y)),
                                         self.__format_argument(context, float(argument.z)))

        if isinstance(argument, Size2):
            return "[{}, {}]".format(self.__format_argument(context, float(argument.width)),
                                     self.__format_argument(context, float(argument.depth)))

        if isinstance(argument, Size3):
            return "[{}, {}, {}]".format(self.__format_argument(context, float(argument.width)),
                                         self.__format_argument(context, float(argument.depth)),
                                         self.__format_argument(context, float(argument.height)))

        if isinstance(argument, bool):
            return str(argument).lower()

        if isinstance(argument, str):
            return '"{}"'.format(re.sub(r'([\\\"])', r'\\\1', argument))

        if isinstance(argument, int):
            return str(argument)

        if isinstance(argument, List):
            parts = []
            for element in argument:
                parts.append(self.__format_argument(context, element))

            return '[{}]'.format(', '.join(parts))

        if isinstance(argument, Tuple):
            parts = []
            for element in argument:
                parts.append(self.__format_argument(context, element))

            return '[{}]'.format(', '.join(parts))

        if isinstance(argument, Color):
            return str(argument)

        raise ValueError(f'Can not format argument of type {argument.__class__}.')

# ----------------------------------------------------------------------------------------------------------------------
