"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2017
SEE COPYRIGHT NOTICE BELOW
"""

import numpy
from csbdeep.utils import normalize
from logger_36.instance.loggers import LOGGERS
from pyvispr.constant.flow.value import VALUE_NOT_SET, value_not_set_t
from stardist.models import StarDist2D
from str_to_obj.api.catalog import path_purpose_e, path_t, path_type_e


def pyVisprAnnSegmenter(
    image: numpy.ndarray,
    /,
    *,
    model: (
        path_t.NewAnnotatedType(path_type_e.document, path_purpose_e.input) | None
    ) = None,
    threshold: float = 0.5,
    should_return_transformed: bool = False,
    pyvispr_name: str | None = None,
) -> tuple[numpy.ndarray, numpy.ndarray | value_not_set_t]:
    """
    _interactive: model, threshold, should_return_transformed
    _outputs: segmented, transformed
    Compute the segmentation of an image by thresholding the output of an ANN model. If
    should_return_transformed is true, the transformed output receives the output of the
    model.
    """
    model = StarDist2D.from_pretrained("2D_demo")
    normalized = normalize(image, 1.0, 99.8, axis=(0, 1))
    labels, _ = model.predict_instances(normalized)

    return labels > 0, labels

    # if image.ndim == 2:
    #     image = numpy.dstack(3 * (image,))
    # elif image.ndim == 3:
    #     if image.shape[2] == 3:
    #         pass
    #     elif image.shape[2] == 4:
    #         image = image[..., :3]
    #     else:
    #         raise NotImplementedError
    # else:
    #     raise NotImplementedError


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
