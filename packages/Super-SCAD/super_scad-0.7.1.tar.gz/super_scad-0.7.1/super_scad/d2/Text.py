from super_scad.private.PrivateOpenScadCommand import PrivateOpenScadCommand


class Text(PrivateOpenScadCommand):
    """
    Widget for creating texts. See https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Text.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self,
                 *,
                 text: str,
                 size: int = 10,
                 font: str | None = None,
                 halign: str = 'left',
                 valign: str = 'baseline',
                 spacing: float = 1.0,
                 direction: str = 'ltr',
                 language: str = 'en',
                 script: str = 'latin',
                 fn: int | None = None):
        """
        Object constructor.

        :param text: The text to generate.
        :param size: The generated text has an ascent (height above the baseline) of approximately the given value.
                     Different fonts can vary somewhat and may not fill the size specified exactly, typically they
                     render slightly smaller. On a metric system a size of 25.4 (1" imperial) will correspond to
                     100pt ⇒ a 12pt font size would be 12×0.254 for metric conversion or 0.12 in imperial.
        :param font: The name of the font that should be used. This is not the name of the font file, but the logical
                     font name (internally handled by the fontconfig library). This can also include a style parameter,
                     see below. A list of installed fonts & styles can be obtained using the font list dialog (Help ->
                     Font List).
        :param halign: The horizontal alignment for the text. Possible values are "left", "center" and "right".
        :param valign: The vertical alignment for the text. Possible values are "top", "center", "baseline" and
                       "bottom".
        :param spacing: Factor to increase/decrease the character spacing. The default value of 1 results in the normal
                        spacing for the font, giving a value greater than 1 causes the letters to be spaced further
                        apart.
        :param direction: Direction of the text flow. Possible values are "ltr" (left-to-right), "rtl" (right-to-left),
                          "ttb" (top-to-bottom) and "btt" (bottom-to-top).
        :param language: The language of the text (e.g., "en", "ar", "ch").
        :param script: The script of the text (e.g., "latin", "arabic", "hani").
        :param fn: Used for subdividing the curved path segments provided by freetype.
        """
        PrivateOpenScadCommand.__init__(self, command='text', args=locals())

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def fn(self) -> int | None:
        """
        Returns used for subdividing the curved path segments provided by freetype.
        """
        return self._args.get('fn')

# ----------------------------------------------------------------------------------------------------------------------
