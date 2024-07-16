from typing import Generic, Optional

from instructor.dsl.maybe import T
from pydantic import BaseModel, Field, create_model


class MaybeBase(BaseModel, Generic[T]):
    """
    Extract a result from a model, if any, otherwise set the error and message fields.
    Mostly copies from instructor.maybe.MaybeBase.
    These fields do get overridden by the fields in the Maybe function, but specified here for typing.
    """

    result: T
    extraction_clarifying_message: Optional[str] = Field(
        default=None, description="Ask the user for clarification if for any fields that "
    )

    def __bool__(self) -> bool:
        return self.result is not None

    @property
    def error(self) -> bool:
        return self.result is None


def Maybe(
    model: type[T], result_description: Optional[str] = None, ecm_description: Optional[str] = None
) -> type[MaybeBase[T]]:
    ## Get required fields
    fields = list(model.model_fields.keys())
    required_fields = [field for field in fields if model.model_fields[field].is_required()]
    ## Descriptions
    result_description = (
        result_description or "Correctly extracted result from the model, if any, otherwise None"
    )
    ecm_description = ecm_description or (
        f"A message asking the user to provide more information when any of "
        f"these fields are missing or unclear, [{','.join(required_fields)}]. "
        f"This message should guide the user to specify the necessary "
        f"details."
    )
    ## capitalize the first letter of the model name
    name = model.__name__[0].upper() + model.__name__[1:]

    ## Field names here (result, extraction_clarifying_message) override the ones in MaybeBase
    return create_model(
        f"Maybe{name}",
        __base__=MaybeBase, # type: ignore
        result=(Optional[model], Field(default=None, description=result_description)),
        extraction_clarifying_message=(str, Field(default=None, description=ecm_description)),
    )
