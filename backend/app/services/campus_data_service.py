from typing import List, Dict, Any
from app.database import db_manager, COLLECTIONS
from app.seed.campus_seed import (
    SEED_VENUES,
    SEED_RESOURCES,
    SEED_BLOCKS,
    SEED_LEADERSHIP,
    SEED_EVENT_CATEGORIES
)

class CampusDataService:
    @staticmethod
    async def get_venues() -> List[Dict[str, Any]]:
        """Fetch all venues from MongoDB or fallback seed data."""
        if db_manager.is_connected and db_manager.db is not None:
            try:
                coll = db_manager.db[COLLECTIONS["venues"]]
                count = await coll.count_documents({})
                if count > 0:
                    cursor = coll.find({}, {"_id": 0})
                    return await cursor.to_list(length=100)
            except Exception:
                pass
        return [dict(v) for v in SEED_VENUES]

    @staticmethod
    async def get_resources() -> List[Dict[str, Any]]:
        """Fetch all campus resources from MongoDB or fallback seed data."""
        if db_manager.is_connected and db_manager.db is not None:
            try:
                coll = db_manager.db[COLLECTIONS["resources"]]
                count = await coll.count_documents({})
                if count > 0:
                    cursor = coll.find({}, {"_id": 0})
                    return await cursor.to_list(length=100)
            except Exception:
                pass
        return [dict(r) for v in [SEED_RESOURCES] for r in v]

    @staticmethod
    async def get_blocks() -> List[Dict[str, Any]]:
        """Fetch campus blocks and floor patterns."""
        return [dict(b) for b in SEED_BLOCKS]

    @staticmethod
    async def get_leadership() -> List[Dict[str, Any]]:
        """Fetch leadership directory."""
        if db_manager.is_connected and db_manager.db is not None:
            try:
                coll = db_manager.db[COLLECTIONS["leadership"]]
                count = await coll.count_documents({})
                if count > 0:
                    cursor = coll.find({}, {"_id": 0})
                    return await cursor.to_list(length=100)
            except Exception:
                pass
        return [dict(l) for l in SEED_LEADERSHIP]

    @staticmethod
    async def get_existing_bookings() -> List[Dict[str, Any]]:
        """Fetch existing event bookings for overlap check."""
        if db_manager.is_connected and db_manager.db is not None:
            try:
                coll = db_manager.db[COLLECTIONS["events"]]
                count = await coll.count_documents({})
                if count > 0:
                    cursor = coll.find({"status": {"$in": ["Approved", "Confirmed"]}}, {"_id": 0})
                    return await cursor.to_list(length=100)
            except Exception:
                pass
        # Return realistic seed bookings for schedule conflict testing
        return [
            {
                "event_id": "bk-01",
                "title": "Annual Alumni Conclave",
                "venue_id": "convocation-hall",
                "dates": "Next Month 15-16",
                "status": "Confirmed"
            },
            {
                "event_id": "bk-02",
                "title": "ECE National Faculty Development Program",
                "venue_id": "spoorthy-sh",
                "dates": "Next Friday",
                "status": "Confirmed"
            }
        ]
