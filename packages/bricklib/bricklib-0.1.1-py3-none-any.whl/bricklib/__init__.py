from typing import Generic, TypeVar, Protocol, List, Optional, runtime_checkable

AS = TypeVar('AS', bound='AttachmentSocketMixin')
A = TypeVar('A', bound='AttachmentMixin')

class AttachmentSocketMixin(Generic[A]):
    def __init__(self):
        self.attachments: List[A] = []

    def attach(self: AS, attachment: A):
        if not isinstance(attachment, Attachment):
            raise TypeError("Can only attach objects that implement the Attachment protocol")
        self.attachments.append(attachment)
        attachment.parent = self

class AttachmentMixin(Generic[AS]):
    def __init__(self):
        self.parent: Optional[AS] = None

    def _attach_to(self: A, socket: AS):
        if not isinstance(socket, AttachmentSocket):
            raise TypeError("Can only attach to objects that implement the AttachmentSocket protocol")
        pass

# Create the 'AttachmentSocket' Protocol, which reflects what AttachmentSocketMixin does
@runtime_checkable
class AttachmentSocket(Protocol[A]):
    attachments: List[A]
    def attach(self, attachment: A) -> None:
        ...

# Create the 'Attachment' Protocol, which reflects what AttachmentMixin does
@runtime_checkable
class Attachment(Protocol[AS]):
    parent: Optional[AS]
    def _attach_to(self, socket: AS) -> None:
        ...
