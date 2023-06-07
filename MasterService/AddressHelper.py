
# Manages secondaries address
class AddressHelper():
    def __init__(self) -> None:
        self.channels = set()

    def GetChannels(self):
        return self.channels
    
    def add(self, channel):
        self.channels.add(channel)

    def remove(self, channel):
        self.channels.remove(channel)