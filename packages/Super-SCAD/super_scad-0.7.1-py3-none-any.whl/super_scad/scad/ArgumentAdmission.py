from typing import Any, List, Set


class ArgumentAdmission:
    """
    Class for validation arguments of a SupeSCAD widget constructor.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, arguments: dict[str, Any]):
        """
        Object constructor.

        :param arguments: The arguments passed to the constructor of the SuperSCAD widget.
        """
        self.__arguments_set: Set[str] = set(arguments.keys())
        """
        A set with all the none empty arguments passed to the constructor of a ScadWidget.
        """

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _to_string(sets: List[Set[str]]) -> str:
        """

        """
        if len(sets) == 0:
            return ''

        if len(sets) == 1:
            return str(sets[0])

        if len(sets) == 2:
            return str(sets[0]) + ' and ' + str(sets[1])

        ret = ''
        for i in range(len(sets) - 1):
            ret += str(sets[i]) + ', '
        ret += ', and ' + str(sets[-1])

        return ret

    # ------------------------------------------------------------------------------------------------------------------
    def validate_exclusive(self, *args: Set[str]) -> None:
        """
        Validates that only arguments belonging to one of the given sets are passed to the constructor of the SuperScad
        widget.
        """
        supplied_sets = []
        for arg in args:
            supplied = set.intersection(self.__arguments_set, arg)
            if supplied:
                supplied_sets.append(supplied)

        if len(supplied_sets) > 1:
            sets = self._to_string(supplied_sets)
            raise ValueError('The following set of arguments are not exclusive: {}'.format(sets))

    # ------------------------------------------------------------------------------------------------------------------
    def validate_required(self, *args: Set[str]) -> None:
        """
        Validates that at least one argument belonging to each of the given sets are passed to the constructor of the
        SuperSCAD widget.
        """
        for arg in args:
            supplied = set.intersection(self.__arguments_set, arg)
            if not supplied:
                raise ValueError('At least one of these arguments {} must be supplied'.format(str(arg)))

# ----------------------------------------------------------------------------------------------------------------------
