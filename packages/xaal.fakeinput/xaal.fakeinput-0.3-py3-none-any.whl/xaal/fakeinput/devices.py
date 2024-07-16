from xaal.schemas import devices

class FakeDevice(object):
    def __init__(self,addr,name,engine):
        self.addr = addr
        self.name = name
        self.engine = engine
        self.setup()
        self._fix_description()
        self.engine.add_device(self.dev)

    def _fix_description(self):
        dev = self.dev
        dev.vendor_id = "RAMBo Team"
        dev.product_id = f"Fake:{self.__class__.__name__ }"

class Button(FakeDevice):
    def setup(self):
        self.dev = devices.button(self.addr)

    def click(self,_type=None):
        if _type == 0:
            self.engine.send_notification(self.dev,'click')
        if _type == 1:
            self.engine.send_notification(self.dev,'double_click')

class Switch(FakeDevice):
    def setup(self):
        self.dev = devices.switch(self.addr)

    def set_on(self):
        self.dev.attributes['position'] = True

    def set_off(self):
        self.dev.attributes['position'] = False

    @property
    def state(self):
        return 'checked' if self.dev.attributes['position'] else ''

class Contact(FakeDevice):
    def setup(self):
        self.dev = devices.contact(self.addr)
        
    def set_on(self):
        self.dev.attributes['detected'] = True

    def set_off(self):
        self.dev.attributes['detected'] = False

    @property
    def state(self):
        return 'checked' if self.dev.attributes['detected'] else ''

class Motion(FakeDevice):
    def setup(self):
        self.dev = devices.motion(self.addr)
        
    def set_on(self):
        self.dev.attributes['presence'] = True

    def set_off(self):
        self.dev.attributes['presence'] = False

    @property
    def state(self):
        return 'checked' if self.dev.attributes['presence'] else ''

