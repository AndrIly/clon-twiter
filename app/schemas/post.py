from pydantic import BaseModel, ConfigDict, Field


class PostCreate(BaseModel):
    text: str = Field(min_length=1, max_length=280, alias="tweet_data")
    tweet_media_ids: list[int] = Field(default_factory=list)
    model_config = ConfigDict(populate_by_name=True)


class AuthorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str = Field(validation_alias="username")


class LikeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    name: str


class TweetOut(BaseModel):
    id: int
    content: str
    stamp: str
    author: AuthorOut
    attachments: list[str] = Field(default_factory=list)
    likes: list[LikeOut] = Field(default_factory=list)

    @classmethod
    def from_orm_post(cls, post) -> "TweetOut":
        return cls(
            id=post.id,
            content=post.content,
            stamp=post.created_at.isoformat(),
            author=AuthorOut.model_validate(post.author),
            attachments=[f"/uploads/{m.file_name}" for m in post.media],
            likes=[
                LikeOut(user_id=like.user_id, name=like.user.username)
                for like in post.likes
            ],
        )


class TweetsResponse(BaseModel):
    result: bool = True
    tweets: list[TweetOut]

    @classmethod
    def from_orm_posts(cls, posts) -> "TweetsResponse":
        return cls(tweets=[TweetOut.from_orm_post(p) for p in posts])


class CreateTweetResponse(BaseModel):
    result: bool = True
    tweet_id: int
