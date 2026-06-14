from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    api_key: str = Field(min_length=1, description="API key")
    username: str = Field(min_length=3, max_length=50, description="Username")
    email: EmailStr | None = Field(None, description="Email address")


class UserShort(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str = Field(validation_alias="username")


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: int
    name: str = Field(validation_alias="username")

    following: list[UserShort] = Field(default_factory=list)
    followers: list[UserShort] = Field(default_factory=list)


class UserResponse(BaseModel):
    result: bool = True
    model_config = ConfigDict(from_attributes=True)
    user: UserPublic

    @classmethod
    def from_orm_user(cls, user) -> "UserResponse":
        public = UserPublic(
            id=user.id,
            name=user.username,
            following=[UserShort.model_validate(f.following) for f in user.following],
            followers=[UserShort.model_validate(f.follower) for f in user.followers],
        )
        return cls(user=public)
