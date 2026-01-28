from typing import Callable, List

class EventBus:
    """
    Real-time synchronization bus for the Shared Semantic Environment.
    """
    
    def __init__(self):
        self.subscribers = {}
        
    def subscribe(self, topic: str, callback: Callable):
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)
        
    def publish(self, topic: str, payload: dict):
        if topic in self.subscribers:
            for callback in self.subscribers[topic]:
                callback(payload)
