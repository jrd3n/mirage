from mirage.core import module
from mirage.libs import utils,ble,io
from mirage.core import module,interpreter

class ble_BULB(module.WirelessModule):
    def init(self):

        self.technology = "ble"
        self.type = "action"
        self.description = "Connection module for Bluetooth Low Energy devices"
        self.args = {
                "INTERFACE":"hci0",
                "TARGET":"BE:58:97:00:1C:62",
                "TIMEOUT":"10",
                "CONNECTION_TYPE":"public"
            }
    def checkCapabilities(self):
        return self.emitter.hasCapabilities("INITIATING_CONNECTION")

    def send_value(self,handle,value):

        value = bytes.fromhex(value)

        self.emitter.send(ble.BLEWriteCommand(handle=handle,value=value))
		
    def run(self):
        interface = self.args["INTERFACE"]
        timeout = utils.integerArg(self.args["TIMEOUT"])

        self.emitter = self.getEmitter(interface=interface)
        self.receiver = self.getReceiver(interface=interface)

        if self.checkCapabilities():
            io.info("Trying to connect to : "+self.args["TARGET"]+" (type : "+self.args["CONNECTION_TYPE"]+")")
            self.emitter.sendp(ble.BLEConnect(self.args["TARGET"], type=self.args["CONNECTION_TYPE"]))

            while not self.receiver.isConnected() and timeout > 0:
                timeout -= 1
                utils.wait(seconds=1)

            if self.receiver.isConnected():
                io.success("Connected on device : "+self.args["TARGET"])

                io.chart(["Input","Action"],[["r","red"],["g","green"],["b","blue"],["w","white"],["party","party lights"],["on","on"],["off","off"]])

                while True:
					
                    key = io.ask("User input")

                    if key == "r":
                        self.send_value(0x9,'7e070503ff000010ef')
                    # if the key is 'down arrow' ...
                    elif key == "g":
                        # inject a OFF packet
                        self.send_value(0x9,'7e07050300ff0010ef')
                    elif key == "b":
                        # inject a OFF packet
                        self.send_value(0x9,'7e0705030000ff10ef')
                    elif key == "s":
                        # inject a OFF packet
                        self.send_value(0x9,'7e04016401ffff00ef')
                    elif key == "w":
                        # inject a OFF packet
                        self.send_value(0x9,'7e0505014fffff08ef')
                    elif key == "on":
                        self.send_value(0x9,'7e04016401ffff00ef')
                    elif key == "off":
                        self.send_value(0x9,'7e04010001ffff00ef')
                    elif key == "party":
                                                        
                        for i in range(10):

                            self.send_value(0x9,'7e07050300ff0010ef')
                            utils.wait(seconds=0.2)

                            self.send_value(0x9,'7e0705030000ff10ef')
                            utils.wait(seconds=0.2)

                            self.send_value(0x9,'7e070503ff000010ef')
                            utils.wait(seconds=0.2)

                            io.progress(i,10)

                    elif key == 'q':
                        return self.ok({"INTERFACE":self.args["INTERFACE"]})
                    pass

                return self.ok({"INTERFACE":self.args["INTERFACE"]})

            else:
                io.fail("Error during connection establishment !")
                self.emitter.sendp(ble.BLEConnectionCancel())
                return self.nok()
        else:
            io.fail("Interface provided ("+str(self.args["INTERFACE"])+") is not able to initiate connection.")
            return self.nok()