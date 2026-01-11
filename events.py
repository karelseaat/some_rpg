from typing import Dict, List, Callable, Any
from dataclasses import dataclass

@dataclass
class Event:
    """Base class for all events."""
    name: str
    data: Dict[str, Any]

class EventBus:
    """Simple event bus for publishing and subscribing to events."""
    def __init__(self):
        self.subscribers: Dict[str, List[Callable[[Event], None]]] = {}

    def subscribe(self, event_name: str, callback: Callable[[Event], None]):
        """Subscribe to an event."""
        if event_name not in self.subscribers:
            self.subscribers[event_name] = []
        self.subscribers[event_name].append(callback)

    def publish(self, event: Event):
        """Publish an event to all subscribers."""
        if event.name in self.subscribers:
            for callback in self.subscribers[event.name]:
                callback(event)

    def clear(self):
        """Clear all subscribers."""
        self.subscribers = {}

# Global event bus instance
event_bus = EventBus()
