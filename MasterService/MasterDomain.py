import asyncio
from threading import Lock, Thread, Condition

import requests

from MasterService.Logging import *
from MasterService.AddressHelper import AddressHelper


def _get_resp_and_approves(x):
    approves_cnt = 0 
    resp_cnt = 0
    for task in x: 
        if not task.done(): 
            continue 
        else: 
            resp_cnt += 1 
        if task.result(): 
            approves_cnt += 1 
    return (resp_cnt, approves_cnt)


class MessageSheduler():
    def __init__(self):
        self.task_list = []
        self.loop = asyncio.new_event_loop()
        runner = Thread(target=self.start)
        runner.start()

    def start(self):
        self.loop.run_until_complete(self.runner())

    async def runner(self):
        while True:
            if len(self.task_list) == 0:
                await asyncio.sleep(1)
            else:
                await self.task_list.pop()

    def create_task(self, func, *args, **kwargs):
        task = self.loop.create_task(func(*args, **kwargs))
        self.task_list.append(task)
        return task


class MasterDomainMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class MasterDomain(metaclass=MasterDomainMeta):
    def __init__(self, addr_helper: AddressHelper, retry_cnt):
        self.addr_helper = addr_helper
        self.number_of_retries = retry_cnt
        self.messages_mtx = Lock()
        self.last_message_id = 0
        self.messages = dict()
        self.sheduler = MessageSheduler()

        self.sheduler.create_task(self.ping)


    async def ping(self):
        delete_list = [] 
        domain_log("checking" + str(self.addr_helper.GetChannels()))
        for ch in self.addr_helper.GetChannels():
            try:
                result = requests.get("http://"+ ch + "/ping")
                if not result.ok:
                    delete_list.append(ch)
            except:
                delete_list.append(ch)
        for ch in delete_list:
            domain_log("Removed secondary" + str(ch))
            self.addr_helper.remove(ch)

        await asyncio.sleep(5)
        self.sheduler.create_task(self.ping)

    # Should send message, do self.number_of_retries retries on fail, 
    # Returns true if message sent, false if all retries failed
    async def send_message(self, channel, id_and_message, notify_cond):

        post_response = requests.post("http://"+channel+ "/add-message", json=id_and_message)
        domain_log("Message Sent!")
        with notify_cond:
            notify_cond.notify()
        return True


    def send_message_to_secondaries(self, id_and_message, write_concern):
        background_tasks = set()
        required_responces = len(self.addr_helper.GetChannels())    
        required_approves = write_concern - 1 # one is only master    
        condition = Condition()
    
        while len(self.addr_helper.GetChannels()) < required_approves:
            time.sleep(5)

        for ch in self.addr_helper.GetChannels():
            task = self.sheduler.create_task(self.send_message, ch, id_and_message, condition)
            background_tasks.add(task)

        resp_cnt = 0
        while resp_cnt < len(background_tasks):
            # Looks like it will check nonstop after first message, but I am lazy 
            with condition:
                condition.wait(timeout=1)
                resp_cnt, approves_cnt = _get_resp_and_approves(background_tasks)
                if approves_cnt >= required_approves:
                    return True

        return False

    def add_message(self, message, write_concern):
        if len(self.addr_helper.GetChannels()) < (write_concern-1):
            return False
        
        domain_log("Adding message")
        with self.messages_mtx:
            id_msg = {"id": self.last_message_id, 
                      "message": message}
            self.messages[self.last_message_id] = message
            self.last_message_id += 1
        
        return self.send_message_to_secondaries(id_msg, write_concern)

    def get_messages(self):
        domain_log("Getting messages")
        with self.messages_mtx:
            return self.messages
    
    def add_client(self, client_address):
        self.addr_helper.add(client_address)
