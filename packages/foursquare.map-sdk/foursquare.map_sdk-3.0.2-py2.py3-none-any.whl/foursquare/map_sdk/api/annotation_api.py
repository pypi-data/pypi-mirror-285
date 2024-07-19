from typing import Any, List, Literal, Optional, Tuple, Union, cast

from pydantic import StrictBool, StrictStr

from foursquare.map_sdk.api.base import Action, CamelCaseBaseModel
from foursquare.map_sdk.api.enums import ActionType
from foursquare.map_sdk.transport.base import (
    BaseInteractiveTransport,
    BaseNonInteractiveTransport,
    BaseTransport,
)


class AnnotationCreationProps(CamelCaseBaseModel):
    id: Optional[StrictStr] = None
    kind: Literal["TEXT", "ARROW", "POINT", "CIRCLE"]
    is_visible: StrictBool
    auto_size: Optional[StrictBool] = None
    auto_size_y: Optional[StrictBool] = None
    anchor_point: Tuple[float, float]
    label: StrictStr
    editor_state: Optional[Any] = None
    map_index: Optional[int] = None
    line_color: StrictStr
    line_width: float
    text_width: float
    text_height: float
    text_vertical_align: Literal["top", "middle", "bottom"]
    arm_length: Optional[float] = None
    angle: Optional[float] = None
    radius_in_meters: Optional[float] = None


class AnnotationUpdateProps(CamelCaseBaseModel):
    is_visible: Optional[StrictBool] = None
    auto_size: Optional[StrictBool] = None
    auto_size_y: Optional[StrictBool] = None
    anchor_point: Optional[Tuple[float, float]] = None
    label: Optional[StrictStr] = None
    editor_state: Optional[Any] = None
    map_index: Optional[int] = None
    line_color: Optional[StrictStr] = None
    line_width: Optional[float] = None
    text_width: Optional[float] = None
    text_height: Optional[float] = None
    text_vertical_align: Optional[Literal["top", "middle", "bottom"]] = None
    arm_length: Optional[float] = None
    angle: Optional[float] = None
    radius_in_meters: Optional[float] = None


class Annotation(CamelCaseBaseModel):
    id: StrictStr
    kind: Literal["TEXT", "ARROW", "POINT", "CIRCLE"]
    is_visible: StrictBool
    auto_size: Optional[StrictBool] = None
    auto_size_y: Optional[StrictBool] = None
    anchor_point: Tuple[float, float]
    label: StrictStr
    editor_state: Optional[Any] = None
    map_index: Optional[int] = None
    line_color: StrictStr
    line_width: float
    text_width: float
    text_height: float
    text_vertical_align: Literal["top", "middle", "bottom"]
    arm_length: Optional[float] = None
    angle: Optional[float] = None
    radius_in_meters: Optional[float] = None


###########
# ACTIONS #
###########


class GetAnnotationsAction(Action):
    type: ActionType = ActionType.GET_ANNOTATIONS


class GetAnnotationByIdAction(Action):
    class Meta(Action.Meta):
        args = ["annotation_id"]

    type: ActionType = ActionType.GET_ANNOTATION_BY_ID
    annotation_id: StrictStr


class AddAnnotationAction(Action):
    class Meta(Action.Meta):
        args = ["annotation"]

    type: ActionType = ActionType.ADD_ANNOTATION
    annotation: AnnotationCreationProps


class UpdateAnnotationAction(Action):
    class Meta(Action.Meta):
        args = ["annotation_id", "values"]

    type: ActionType = ActionType.UPDATE_ANNOTATION
    annotation_id: StrictStr
    values: AnnotationUpdateProps


class RemoveAnnotationAction(Action):
    class Meta(Action.Meta):
        args = ["annotation_id"]

    type: ActionType = ActionType.REMOVE_ANNOTATION
    annotation_id: StrictStr


###########
# METHODS #
###########


class BaseAnnotationApiMethods:
    transport: BaseTransport

    def add_annotation(
        self, annotation: Union[AnnotationCreationProps, dict]
    ) -> Optional[Annotation]:
        """Adds a new annotation to the map.

        Args:
            annotation (Union[AnnotationCreationProps, dict]): The annotation to add.

        Returns (widget map only):
            Annotation: The annotation that was added.
        """

        action = AddAnnotationAction(annotation=annotation)

        return self.transport.send_action_non_null(
            action=action, response_class=Annotation
        )

    def update_annotation(
        self,
        annotation_id: str,
        values: Union[AnnotationUpdateProps, dict],
    ) -> Optional[Annotation]:
        """Updates an existing annotation with given values.

        Args:
            annotation_id (str): The id of the annotation to update.
            values (Union[Annotation, dict]): The values to update.

        Returns (widget map only)
            Annotation: The updated annotation.
        """
        action = UpdateAnnotationAction(annotation_id=annotation_id, values=values)
        return self.transport.send_action_non_null(
            action=action, response_class=Annotation
        )

    def remove_annotation(self, annotation_id: str) -> None:
        """Removes an annotation from the map.

        Args:
            annotation_id (str): The id of the annotation to remove

        Returns:
            None
        """
        action = RemoveAnnotationAction(annotation_id=annotation_id)
        self.transport.send_action(action=action, response_class=None)


class BaseInteractiveAnnotationApiMethods:
    transport: BaseInteractiveTransport

    def get_annotations(self) -> List[Annotation]:
        """Gets all the annotations currently available in the map.

        Returns:
            List[Annotation]: An array of annotations.
        """
        action = GetAnnotationsAction()
        return self.transport.send_action_non_null(
            action=action, response_class=List[Annotation]
        )

    def get_annotation_by_id(self, annotation_id: str) -> Optional[Annotation]:
        """Retrieves an annotation by its identifier if it exists.

        Args:
            annotation_id (str): Identifier of the annotation to get.

        Returns:
            Optional[Annotation]: Annotation with a given identifier, or None if one doesn't exist.
        """
        action = GetAnnotationByIdAction(annotation_id=annotation_id)
        return self.transport.send_action(action=action, response_class=Annotation)


class AnnotationApiNonInteractiveMixin(BaseAnnotationApiMethods):
    """Annotation methods that are supported in non-interactive (i.e. pure HTML) maps"""

    transport: BaseNonInteractiveTransport

    def add_annotation(self, annotation: Union[AnnotationCreationProps, dict]) -> None:
        super().add_annotation(annotation=annotation)
        return

    def update_annotation(
        self,
        annotation_id: str,
        values: Union[AnnotationUpdateProps, dict],
    ) -> None:
        super().update_annotation(annotation_id=annotation_id, values=values)
        return


class AnnotationApiInteractiveMixin(
    BaseAnnotationApiMethods, BaseInteractiveAnnotationApiMethods
):
    """Annotation methods that are supported in interactive (i.e. widget) maps"""

    transport: BaseInteractiveTransport

    def add_annotation(
        self, annotation: Union[AnnotationCreationProps, dict]
    ) -> Annotation:
        return cast(Annotation, super().add_annotation(annotation=annotation))

    def update_annotation(
        self, annotation_id: str, values: Union[AnnotationUpdateProps, dict]
    ) -> Annotation:
        return cast(
            Annotation,
            super().update_annotation(annotation_id=annotation_id, values=values),
        )

    def get_annotations(self) -> List[Annotation]:
        return super().get_annotations()

    def get_annotation_by_id(self, annotation_id: str) -> Optional[Annotation]:
        return super().get_annotation_by_id(annotation_id=annotation_id)
