from mirage.core import module
from mirage.libs import utils,ble,io
from mirage.core import module,interpreter
import keyboard
import csv

import time

import random

class ble_FUZZ(module.WirelessModule):
    def init(self):

        self.technology = "ble"
        self.type = "FUZZ"
        self.description = "Module to SPOOF a target"
        self.args = {
                "INTERFACE":"hci0",
                "TARGET":"BE:58:97:00:1C:62",
                "SENDasSLAVE":"True",
                "TIMEOUT":"100",
                "CONNECTION_TYPE":"public",
                "HANDLE":"9",
                "NoOfPackets":"100",
                "EXAMPLE_HEX":"0x7e07050300ffff10ef",
                "OUTPUT_FILE":"FUZZING_RESULTS.csv"
            }
    def checkCapabilities(self):
        return self.emitter.hasCapabilities("INITIATING_CONNECTION")
    
    def send_value(self,handle,value):

        utils.wait(seconds=0.07)

        self.emitter.send(ble.BLEWriteRequest(handle=handle,value=bytes.fromhex(value)))

    def onKey(self,key):

        io.info("Key press registered")

        self.key_pressed = True

    def hex_example_to_range(self, EXAMPLE_HEX):

        HEX_VALUE = EXAMPLE_HEX.lower().replace("0x","")

        Highest_DIGIT = 'F'
        Lowest_DIGIT = '1' + '0' * (len(HEX_VALUE) - 1)
 
        byte_length = (len(EXAMPLE_HEX) + 1) // 2  # to help format the output binary

        LOW = Lowest_DIGIT

        LOW = hex(int(LOW,16))

        HIGH = Highest_DIGIT * len(HEX_VALUE)

        HIGH = hex(int(HIGH,16))

        io.info(f"The input HEX {hex(int(EXAMPLE_HEX,16))}, LOW = {LOW}, HIGH = {HIGH}")

        return [int(LOW,16), int(HIGH,16)]

    def run(self):
		
        interface = self.args["INTERFACE"]
        timeout = utils.integerArg(self.args["TIMEOUT"])

        [LOW, HIGH] = self.hex_example_to_range(self.args["EXAMPLE_HEX"])

        self.emitter = self.getEmitter(interface=interface)
        self.receiver = self.getReceiver(interface=interface)

        if self.checkCapabilities():
            io.info("Trying to connect to : " + self.args["TARGET"]+" (type : "+self.args["CONNECTION_TYPE"]+")")
            self.emitter.sendp(ble.BLEConnect(self.args["TARGET"], type=self.args["CONNECTION_TYPE"]))

            while not self.receiver.isConnected() and timeout > 0:
                timeout -= 1
                utils.wait(seconds=1)

            if self.receiver.isConnected():

                io.success("Connected on device : "+ self.args["TARGET"])

                self.key_pressed = False

                keyboard.on_press(self.onKey)

                with open(self.args["OUTPUT_FILE"], 'w', newline='') as file:
                    writer = csv.writer(file)
                    field = ["Handle", "Value", "Event"]
                    writer.writerow(field)

                for i in range(int(self.args["NoOfPackets"])):

                    random_int = str(hex(random.randint(LOW,HIGH))).lower().replace("0x","")

                    self.send_value(int(self.args["HANDLE"]),random_int)

                    with open(self.args["OUTPUT_FILE"], 'a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow([hex(int(self.args['HANDLE'])), random_int, self.key_pressed == True])

                    self.key_pressed = False

                    io.progress(i,int(self.args["NoOfPackets"])-1, suffix=f"Sending {random_int} to {hex(int(self.args['HANDLE']))}")

                return self.ok({"INTERFACE":self.args["INTERFACE"]})

            else:
                io.fail("Error during connection establishment !")
                self.emitter.sendp(ble.BLEConnectionCancel())
                return self.nok()
        else:
            io.fail("Interface provided ("+str(self.args["INTERFACE"])+") is not able to initiate connection.")
            return self.nok()