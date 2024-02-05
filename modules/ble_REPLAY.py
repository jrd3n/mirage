from mirage.core import module
from mirage.libs import utils,ble,io
from mirage.core import module,interpreter

import pyshark

class ble_REPLAY(module.WirelessModule):
    def init(self):

        self.technology = "ble"
        self.type = "REPLAY"
        self.description = "Module to REPLAY a PCAP file to the target"
        self.args = {
                "INTERFACE":"hci0",
                "TARGET":"BE:58:97:00:1C:62",
                "SENDasSLAVE":"True",
                "TIMEOUT":"100",
                "CONNECTION_TYPE":"public",
                "PCAP_FILE":"",
            }
    def checkCapabilities(self):
        return self.emitter.hasCapabilities("INITIATING_CONNECTION")

    def send_value(self,handle,value):

        value = value.lower().replace(":","")

        io.info(f"Sending value {value}")

        value = bytes.fromhex(value)

        self.emitter.send(ble.BLEWriteCommand(handle=handle,value=value))
		
    def run(self):

        self.pcap = self.args["PCAP_FILE"]

        if (self.pcap) == "":
            io.fail("PCAP_FILE=None")
            return self.nok()

        packets = list(pyshark.FileCapture(self.pcap))
		
        interface = self.args["INTERFACE"]
        timeout = utils.integerArg(self.args["TIMEOUT"])

        # self.pcap_receiver = self.getReceiver(interface=self.pcap)

        self.emitter = self.getEmitter(interface=interface)
        self.receiver = self.getReceiver(interface=interface)

        if self.checkCapabilities():

            io.info("Trying to connect to : " + self.args["TARGET"]+" (type : "+self.args["CONNECTION_TYPE"]+")")
            self.emitter.sendp(ble.BLEConnect(self.args["TARGET"], type=self.args["CONNECTION_TYPE"]))

            while not self.receiver.isConnected() and timeout > 0:

                timeout -= 1
                utils.wait(seconds=1)

            if self.receiver.isConnected():

                io.success("Connected on device : "+self.args["TARGET"])

                io.success("Sending BLE packets from PCAP file")

                for packet in packets:

                    if 'btle' in packet:

                        btle = packet['btle']

                        if btle.get('slave_bd_addr','none').upper() == self.args["TARGET"].upper():

                            # print(dir(packet))
                    
                            # if 'btatt' in packet:
                            #     print(packet['btatt']) 
                            # if 'btl2cap' in packet:
                            #     print(packet['btl2cap']) 
                            # # if 'btle' in packet:
                            # #     print(packet['btle']) 
                            # if 'captured_length' in packet:
                            #     print(packet['captured_length']) 
                            # if 'frame_info' in packet:
                            #     print(packet['frame_info']) 
                            # if 'get_multiple_layers' in packet:
                            #     print(packet['get_multiple_layers']) 
                            # if 'get_raw_packet' in packet:
                            #     print(packet['get_raw_packet']) 
                            # if 'highest_layer' in packet:
                            #     print(packet['highest_layer']) 
                            # if 'interface_captured' in packet:
                            #     print(packet['interface_captured']) 
                            # if 'layers' in packet:
                            #     print(packet['layers']) 
                            # if 'length' in packet:
                            #     print(packet['length']) 
                            # # if 'nordic_ble' in packet:
                            # #     print(packet['nordic_ble']) 
                            # if 'number' in packet:
                            #     print(packet['number']) 
                            # if 'pretty_print' in packet:
                            #     print(packet['pretty_print']) 
                            # if 'show' in packet:
                            #     print(packet['show']) 
                            # if 'sniff_time' in packet:
                            #     print(packet['sniff_time']) 
                            # if 'sniff_timestamp' in packet:
                            #     print(packet['sniff_timestamp']) 
                            # if 'transport_layer' in packet:
                            #     print(packet['transport_layer'])



        
                            if "BTATT" in packet:

                                # print(packet['btatt']) 

                                btatt_layer = packet["BTATT"]

                                handle = btatt_layer.get('handle')

                                opcode_command = btatt_layer.get('opcode_command') # this is bool, whether the operatiohn is a command or not
                                opcode_method = btatt_layer.get('opcode_method') # this is whether a request is expected
                                value = btatt_layer.get('value')

                                if opcode_command == '1':

                                    # print(packet['btatt'])

                                    self.send_value(handle,value)

                                    utils.wait(seconds=0.07)


                    #     UUID = btatt_layer.get('uuid128')


                    #     field_names = btatt_layer.get('field_names') 
                    #     get = btatt_layer.get('get') 
                    #     get_field = btatt_layer.get('get_field') 
                    #     get_field_by_showname = btatt_layer.get('get_field_by_showname') 
                    #     get_field_value = btatt_layer.get('get_field_value') 
                    #     handle = btatt_layer.get('handle') 
                    #     has_field = btatt_layer.get('has_field') 
                    #     layer_name = btatt_layer.get('layer_name') 
                    #     opcode = btatt_layer.get('opcode') 
                    #     opcode_authentication_signature = btatt_layer.get('opcode_authentication_signature') 


                    #     pretty_print = btatt_layer.get('pretty_print') 
                    #     raw_mode = btatt_layer.get('raw_mode') 
                    #     service_uuid16 = btatt_layer.get('service_uuid16') 
                    #     uuid16 = btatt_layer.get('uuid16') 


                    #     io.info(f"handle = {handle}\tValue = {value}\tUUID = {UUID}")

                    #     if opcode_command == '1':
                        
                    #         formatted_value = value.replace(':', '')

                    #         formatted_data = UUID.replace(':', '')
                    #         uuid_format = f"{formatted_data[:8]}-{formatted_data[8:12]}-{formatted_data[12:16]}-{formatted_data[16:20]}-{formatted_data[20:]}"

                    #         print(f"handle  = {handle}, value = {formatted_value}, UUID = {uuid_format}, OPMETHOD = {opcode_method}")

                    #         send_value(handle,formatted_value)
         
                return self.ok({"INTERFACE":self.args["INTERFACE"]})

            else:
                io.fail("Error during connection establishment !")
                self.emitter.sendp(ble.BLEConnectionCancel())
                return self.nok()
        else:
            io.fail("Interface provided ("+str(self.args["INTERFACE"])+") is not able to initiate connection.")
            return self.nok()