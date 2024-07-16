# mixins.py

from typing import Generic, List, Optional, TypeVar
from .types import AttachmentSocket, Attachment

# Type variables bound to their respective protocols
AS = TypeVar('AS', bound='AttachmentSocket')
A = TypeVar('A', bound='Attachment')

class AttachmentSocketMixin(Generic[A]):
    """
    Mixin for objects that can have attachments.

    Implements the AttachmentSocket protocol.

    Attributes:
        attachments (List[A]): List of attached objects.
    
    Methods:
        attach(attachment: A) -> None: Attach an object to this socket.
    """
    def __init__(self):
        self.attachments: List[A] = []

    def attach(self: AS, attachment: A):
        """
        Attach an object to this socket.

        Args:
            attachment (A): The object to attach.
        
        Raises:
            TypeError: If the attachment does not implement the Attachment protocol.
        """
        if not isinstance(attachment, Attachment):
            raise TypeError("Can only attach objects that implement the Attachment protocol")
        self.attachments.append(attachment)
        attachment.parent = self
        attachment._attach_to(self)

class AttachmentMixin(Generic[AS]):
    """
    Mixin for objects that can be attached to an AttachmentSocket.

    Implements the Attachment protocol.

    Attributes:
        parent (Optional[AS]): The socket this attachment is attached to.
    
    Methods:
        _attach_to(socket: AS) -> None: Attach this object to a socket.
    """
    def __init__(self):
        self.parent: Optional[AS] = None

    def _attach_to(self: A, socket: AS):
        """
        Attach this object to a socket.

        Args:
            socket (AS): The socket to attach to.
        
        Raises:
            TypeError: If the socket does not implement the AttachmentSocket protocol.
        """
        if not isinstance(socket, AttachmentSocket):
            raise TypeError("Can only attach to objects that implement the AttachmentSocket protocol")
        pass
