# types.py

from typing import Generic, TypeVar, Protocol, List, Optional, runtime_checkable

# Type variables bound to their respective protocols
AS = TypeVar('AS', bound='AttachmentSocket')
A = TypeVar('A', bound='Attachment')

@runtime_checkable
class AttachmentSocket(Protocol[A]):
    """
    Protocol for objects that can have attachments.

    Attributes:
        attachments (List[A]): List of attached objects.
    
    Methods:
        attach(attachment: A) -> None: Attach an object to this socket.
    """
    attachments: List[A]
    
    def attach(self, attachment: A) -> None:
        pass

@runtime_checkable
class Attachment(Protocol[AS]):
    """
    Protocol for objects that can be attached to an AttachmentSocket.

    Attributes:
        parent (Optional[AS]): The socket this attachment is attached to.
    
    Methods:
        _attach_to(socket: AS) -> None: Attach this object to a socket.
    """
    parent: Optional[AS]
    
    def _attach_to(self, socket: AS) -> None:
        pass
