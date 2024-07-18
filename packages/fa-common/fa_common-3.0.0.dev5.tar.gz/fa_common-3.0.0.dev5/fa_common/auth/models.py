from datetime import datetime
from typing import List, Optional

from pydantic import AnyUrl, EmailStr, Field, model_validator

from fa_common.models import CamelModel


class AuthUser(CamelModel):
    sub: str
    name: str = "Unknown User"
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    country: Optional[str] = None
    email: Optional[EmailStr] = None
    nickname: Optional[str] = None
    emails: Optional[List[EmailStr]] = None
    email_verified: bool = Field(False, title="Email Verified")
    picture: Optional[AnyUrl] = None
    updated_at: Optional[datetime] = Field(None, title="Updated At")
    scopes: List[str] = []
    roles: List[str] = []

    @model_validator(mode="after")
    def set_name_to_given_family(self):
        if (self.name is None or self.name == "Unknown User") and (self.given_name or self.family_name):
            self.name = f"{self.given_name} {self.family_name}"

        if self.email is None and self.emails is not None and len(self.emails) > 0:
            self.email = self.emails[0]

        return self
