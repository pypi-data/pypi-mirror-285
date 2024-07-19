"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2023
SEE COPYRIGHT NOTICE BELOW
"""

import typing as h


def __init__Function(size_policy, /) -> h.Callable:
    """"""

    def __init__(self, *args, **kwargs) -> None:
        """"""
        super(self.__class__, self).__init__(*args, **kwargs)
        self.setSizePolicy(size_policy, size_policy)
        self.setScaledContents(True)
        # Must be kept alive in instance.
        self.q_image = None

    return __init__


def SetImageFunction(module, n_array_t, img_format, /):
    """"""

    def SetImage(self, rgb_image: n_array_t, /) -> None:
        """
        QImage call taken from:
        https://github.com/baoboa/pyqt5/blob/master/examples/widgets/imageviewer.py
        """
        self.q_image = module.QImage(
            rgb_image.data,
            rgb_image.shape[1],
            rgb_image.shape[0],
            3 * rgb_image.shape[1],
            img_format,
        )
        self.setPixmap(module.QPixmap.fromImage(self.q_image))

    return SetImage


def DrawPointsFunction(module, n_array_t, point_t, /):
    """"""

    def DrawPoints(
        self,
        points: tuple[n_array_t, n_array_t],
        color: tuple[int, int, int],
        /,
        *,
        bbox_width: int = 1,
        bbox_height: int = 1,
    ) -> None:
        """"""
        contour_qpoints = tuple(point_t(point[1], point[0]) for point in zip(*points))
        pixmap = module.QPixmap(self.pixmap())

        painter = module.QPainter()
        painter.begin(pixmap)
        painter.setPen(
            module.QPen(module.QColor(*color))
        )  # Must be after call to begin
        for point in contour_qpoints:
            # TODO: Check why -1's are necessary.
            painter.drawPoint(point.x() + bbox_width - 1, point.y() + bbox_height - 1)
        painter.end()

        self.setPixmap(pixmap)

    return DrawPoints


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
