from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class RemoteFile(BaseModel):
    id: int
    uuid: str
    display_name: str
    filename: str
    url: str
    size: int
    locked: bool
    hidden: bool
    hidden_for_user: bool
    locked_for_user: bool


class LegacyPage(BaseModel):
    published: bool
    hide_from_students: bool
    locked_for_user: bool
    body: Optional[str]


class DiscussionTopicHeader(BaseModel):
    id: int
    title: str
    created_at: datetime
    private_delayed_post_at: Optional[datetime] = Field(alias="delayed_post_at")
    private_posted_at: Optional[datetime] = Field(alias="posted_at")
    position: int
    user_name: str
    user_can_see_posts: bool
    read_state: str
    unread_count: int
    subscribed: bool
    # I'm not sure if I've ever seen anything in this field
    attachments: List[RemoteFile]
    published: bool
    locked: bool
    html_url: str
    url: str
    pinned: bool
    message: str
    is_announcement: bool
    # This is added manually, not returned from canvas API
    course_id: str

    @property
    def posted_at(self) -> datetime:
        return self.private_posted_at or self.private_delayed_post_at


class MediaSource(BaseModel):
    is_original: str = Field(..., alias="isOriginal")
    bitrate: str
    url: str
    file_ext: str = Field(..., alias="fileExt")
    size: str


class MediaObject(BaseModel):
    title: str
    media_sources: list[MediaSource]
