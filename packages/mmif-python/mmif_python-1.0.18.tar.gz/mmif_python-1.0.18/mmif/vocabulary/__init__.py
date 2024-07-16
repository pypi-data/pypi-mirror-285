from .base_types import ThingTypesBase
from .base_types import ThingType
from .base_types import ClamsTypesBase
from .base_types import AnnotationTypesBase
from .base_types import DocumentTypesBase
from .annotation_types import AnnotationTypes
from .document_types import DocumentTypes

_typevers = {**ThingType._typevers, **AnnotationTypes._typevers, **DocumentTypes._typevers}
