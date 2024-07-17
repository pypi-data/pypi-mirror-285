from xaal.lib import Device

class OutputChannel(object):

    def __init__(self,ipx,channel,addr,state_name,group):
        dev = Device("changeme.basic",addr)
        dev.vendor_id  = "IHSEV"
        dev.version    = 0.1
        dev.hw_id = channel
        dev.group_id = group
        dev.info = 'IPX-800 output %s' % channel
        
        # attribute
        self.state = dev.new_attribute(state_name)
        
        # method 
        dev.add_method('turn_on',self.turn_on)
        dev.add_method('turn_off',self.turn_off)
        dev.add_method('toggle',self.toggle)

        self.chan = channel
        self.ipx = ipx 
        self.dev = dev

    def turn_on(self):
        self.ipx.relay_on(self.chan)
    
    def turn_off(self):
        self.ipx.relay_off(self.chan)

    def toggle(self):
        if self.state.value == True:
            self.turn_off()
        else:
            self.turn_on()

def new_lamp(ipx,channel,addr,group):
    lamp = OutputChannel(ipx,channel,addr,'light',group)
    lamp.dev.dev_type = 'lamp.toggle'
    lamp.dev.product_id = 'IPX-800 Lamp'
    return lamp


def new_relay(ipx,channel,addr,group):
    relay = OutputChannel(ipx,channel,addr,'power',group)
    relay.dev.dev_type = 'powerrelay.toggle'
    relay.dev.product_id = 'IPX-800 Power Relay'
    return relay
