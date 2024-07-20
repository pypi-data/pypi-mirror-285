from typing import Any, Optional, Dict

from drf_yasg.openapi import Contact, License


class Swagger:
    title: str
    default_version: str
    description: str
    terms_of_service: str
    contact: Contact
    license: License

    __instance__: Any = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance__ is None:
            cls.__instance__ = object.__new__(cls)
        return cls.__instance__

    def __init__(
            self,
            title: str,
            email: str,
            license: str = "BSD License",
            default_version: str = "v1",
            description: Optional[str] = None,
            terms_of_service: Optional[str] = None
    ):
        self.title = title
        self.default_version = default_version
        self.description = description
        self.terms_of_service = terms_of_service
        self.contact = Contact(email=email)
        self.license = License(name=license)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "default_version": self.default_version,
            "description": self.description,
            "terms_of_service": self.terms_of_service,
            "contact": self.contact,
            "license": self.license
        }
