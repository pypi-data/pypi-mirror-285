from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="ChatMessageRequest")


@attr.s(auto_attribs=True)
class ChatMessageRequest:
    """
    Attributes:
        message (str):
        system_context_override (Union[Unset, str]):
    """

    message: str
    system_context_override: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        message = self.message
        system_context_override = self.system_context_override

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "message": message,
            }
        )
        if system_context_override is not UNSET:
            field_dict["systemContextOverride"] = system_context_override

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        message = d.pop("message")

        system_context_override = d.pop("systemContextOverride", UNSET)

        chat_message_request = cls(
            message=message,
            system_context_override=system_context_override,
        )

        chat_message_request.additional_properties = d
        return chat_message_request

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
