# services/chat_store.py

from uuid import uuid4
from datetime import datetime


class ChatStore:
    def __init__(self):
        self.conversations = {} 

    def new_chat(self):
        cid = str(uuid4())
        now = datetime.utcnow()
        self.conversations[cid] = {
            "id": cid,
            "title": "New Chat",
            "messages": [],
            "created_at": now,
            "updated_at": now,
        }
        return self.conversations[cid]

    def get(self, cid):
        return self.conversations.get(cid)

    def all(self):
        return sorted(
            self.conversations.values(),
            key=lambda c: c["updated_at"],
            reverse=True,
        )

    def delete(self, cid):
        return self.conversations.pop(cid, None)

    def add_message(self, cid, role, content):
        conv = self.conversations[cid]
        msg = {
            "id": str(uuid4()),
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow(),
        }
        conv["messages"].append(msg)
        conv["updated_at"] = datetime.utcnow()
        return msg


store = ChatStore()
