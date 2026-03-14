#Codeflix_Botz
#rohit_1888 on Tg

import motor.motor_asyncio
import time
from config import DB_URI, DB_NAME
import logging

logging.basicConfig(level=logging.INFO)

default_verify = {
    'is_verified': False,
    'verified_time': 0,
    'verify_token': "",
    'link': ""
}

def new_user(id):
    return {
        '_id': id,
        'verify_status': default_verify
    }

class Rohit:

    def __init__(self, DB_URI, DB_NAME):
        self.dbclient = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
        self.database = self.dbclient[DB_NAME]

        self.channel_data = self.database['channels']
        self.admins_data = self.database['admins']
        self.user_data = self.database['users']
        self.sex_data = self.database['sex']
        self.banned_user_data = self.database['banned_user']
        self.autho_user_data = self.database['autho_user']
        self.del_timer_data = self.database['del_timer']
        self.fsub_data = self.database['fsub']
        self.rqst_fsub_data = self.database['request_forcesub']
        self.rqst_fsub_Channel_data = self.database['request_forcesub_channel']

        # masked links
        self.masked_links = self.database['masked_links']


    # ---------------- USER DATA ----------------

    async def present_user(self, user_id: int):
        user = await self.user_data.find_one({'_id': user_id})
        return bool(user)

    async def add_user(self, user_id: int):
        await self.user_data.insert_one({'_id': user_id})

    async def full_userbase(self):
        users = await self.user_data.find().to_list(length=None)
        return [user['_id'] for user in users]

    async def del_user(self, user_id: int):
        await self.user_data.delete_one({'_id': user_id})


    # ---------------- ADMIN DATA ----------------

    async def admin_exist(self, admin_id: int):
        admin = await self.admins_data.find_one({'_id': admin_id})
        return bool(admin)

    async def add_admin(self, admin_id: int):
        if not await self.admin_exist(admin_id):
            await self.admins_data.insert_one({'_id': admin_id})

    async def del_admin(self, admin_id: int):
        if await self.admin_exist(admin_id):
            await self.admins_data.delete_one({'_id': admin_id})

    async def get_all_admins(self):
        admins = await self.admins_data.find().to_list(length=None)
        return [admin['_id'] for admin in admins]


    # ---------------- BAN USERS ----------------

    async def ban_user_exist(self, user_id: int):
        user = await self.banned_user_data.find_one({'_id': user_id})
        return bool(user)

    async def add_ban_user(self, user_id: int):
        if not await self.ban_user_exist(user_id):
            await self.banned_user_data.insert_one({'_id': user_id})

    async def del_ban_user(self, user_id: int):
        if await self.ban_user_exist(user_id):
            await self.banned_user_data.delete_one({'_id': user_id})

    async def get_ban_users(self):
        users = await self.banned_user_data.find().to_list(length=None)
        return [user['_id'] for user in users]


    # ---------------- AUTO DELETE TIMER ----------------

    async def set_del_timer(self, value: int):
        existing = await self.del_timer_data.find_one({})
        if existing:
            await self.del_timer_data.update_one({}, {'$set': {'value': value}})
        else:
            await self.del_timer_data.insert_one({'value': value})

    async def get_del_timer(self):
        data = await self.del_timer_data.find_one({})
        return data.get('value', 600) if data else 0


    # ---------------- CHANNEL MANAGEMENT ----------------

    async def channel_exist(self, channel_id: int):
        channel = await self.fsub_data.find_one({'_id': channel_id})
        return bool(channel)

    async def add_channel(self, channel_id: int):
        if not await self.channel_exist(channel_id):
            await self.fsub_data.insert_one({'_id': channel_id})

    async def rem_channel(self, channel_id: int):
        if await self.channel_exist(channel_id):
            await self.fsub_data.delete_one({'_id': channel_id})

    async def show_channels(self):
        channels = await self.fsub_data.find().to_list(length=None)
        return [channel['_id'] for channel in channels]


    # ---------------- REQUEST FORCE SUB ----------------

    async def req_user(self, channel_id: int, user_id: int):
        await self.rqst_fsub_Channel_data.update_one(
            {'_id': int(channel_id)},
            {'$addToSet': {'user_ids': int(user_id)}},
            upsert=True
        )

    async def del_req_user(self, channel_id: int, user_id: int):
        await self.rqst_fsub_Channel_data.update_one(
            {'_id': int(channel_id)},
            {'$pull': {'user_ids': int(user_id)}}
        )

    async def req_user_exist(self, channel_id: int, user_id: int):
        user = await self.rqst_fsub_Channel_data.find_one({
            '_id': int(channel_id),
            'user_ids': int(user_id)
        })
        return bool(user)

    async def reqChannel_exist(self, channel_id: int):
        channel_ids = await self.show_channels()
        return channel_id in channel_ids


    # ---------------- VERIFY SYSTEM ----------------

    async def db_verify_status(self, user_id):
        user = await self.user_data.find_one({'_id': user_id})
        if user:
            return user.get('verify_status', default_verify)
        return default_verify

    async def db_update_verify_status(self, user_id, verify):
        await self.user_data.update_one({'_id': user_id}, {'$set': {'verify_status': verify}})

    async def get_verify_status(self, user_id):
        return await self.db_verify_status(user_id)

    async def update_verify_status(self, user_id, verify_token="", is_verified=False, verified_time=0, link=""):
        current = await self.db_verify_status(user_id)
        current['verify_token'] = verify_token
        current['is_verified'] = is_verified
        current['verified_time'] = verified_time
        current['link'] = link
        await self.db_update_verify_status(user_id, current)


    # ---------------- VERIFY COUNT ----------------

    async def set_verify_count(self, user_id: int, count: int):
        await self.sex_data.update_one({'_id': user_id}, {'$set': {'verify_count': count}}, upsert=True)

    async def get_verify_count(self, user_id: int):
        user = await self.sex_data.find_one({'_id': user_id})
        return user.get('verify_count', 0) if user else 0

    async def reset_all_verify_counts(self):
        await self.sex_data.update_many({}, {'$set': {'verify_count': 0}})

    async def get_total_verify_count(self):
        pipeline = [{"$group": {"_id": None, "total": {"$sum": "$verify_count"}}}]
        result = await self.sex_data.aggregate(pipeline).to_list(length=1)
        return result[0]["total"] if result else 0


    # ---------------- MASKED LINKS ----------------

    async def store_masked_link(self, hash_id: str, target: str, algorithm: str):
        await self.masked_links.insert_one({
            "_id": hash_id,
            "target": target,
            "algorithm": algorithm,
            "created_at": time.time()
        })

    async def get_masked_link(self, hash_id: str):
        return await self.masked_links.find_one({"_id": hash_id})


db = Rohit(DB_URI, DB_NAME)
