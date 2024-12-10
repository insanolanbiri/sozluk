from enum import Flag, auto


class HumanCapability(Flag):
    SIMPLE_RW = auto()
    """Allow the human to read topics & entries, write entries."""
    MOVE_TOPIC = auto()
    """Allow the human to bulk move entries in one topic to another."""
    DELETE_ENTRY = auto()
    """Permit the human to delete everybody's entries for moderation purposes."""
    VERIFY_HUMAN = auto()
    """Allow the human to verify new humans (By adding SIMPLE_RW capability to them)."""
    DEVERIFY_HUMAN = auto()
    """Allow the human to deverify verified humans (By removing all capabilities of them)."""
    VIEW_REAL_NAME = auto()
    """Allow the human to view the real names of others."""
    CHANGE_PRIMARY_IDENTIFIER = auto()
    """Allow the human to change the primary identities of others with their permission."""
    EXTEND_CAPABILITIES = auto()
    """Allow the human to inherit some or all capabilies (Excluding this capability and EXTEND_CAPABILITY_LOOP) to other humans."""
    EXTEND_CAPABILITES_LOOP = auto()
    """Allow the human to inherit even the EXTEND_CAPABILITIES capability."""
    PERSISTENT_CAPABILITES = auto()
    """Make the human's capabilities non-removable, except by the administrator."""
    ADMINISTRATOR = auto()
    """Allow the human to override certain restrictions."""
