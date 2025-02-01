###############################################################################
#
#   Interface module for APC SMART-UPS over serial interface
#
###############################################################################
#
#   2024 - August - Henk-Johan
#           - first version of interface module
#
#
###############################################################################
#   to-be-do-list
#
#
###############################################################################
import time                         # for sleeping
import serial                       # for RS232 connection


###############################################################################
class APC:

    def __init__(self, serialport):
        '''Init of the UPS. We need to parse the serialport location that we are going to use.'''
        self.serialport = serialport

    def serial_open(self):
        '''Open the serialport that we parsed at the init.'''
        self.ser = serial.Serial(
            port        = self.serialport,
            baudrate    = 2400,
            parity      = serial.PARITY_NONE,
            stopbits    = serial.STOPBITS_ONE,
            bytesize    = serial.EIGHTBITS,
            timeout     = 2
            )
        return self.ser.is_open

    def serial_close(self):
        '''Close the serialport that we parsed at the init.'''
        self.ser.close()
        return self.ser.is_open

    def process_command(self, data, debug = False, sleep=0.5):
        """Handle commands . This method will only do a basic inspection of the data that comes back."""
        # transform the list into a byte array so we can push it out of the RS232 port
        transmit = bytearray(data)
        # write to the RS232 port
        if debug:
            print('Transmitting:', list(transmit))
        trbytes = self.ser.write(transmit)
        if trbytes != len(transmit):
            return [-1]
        # small delay to give the APC time to respond. keep in mind, it is slow.
        time.sleep(sleep)
        # check how many bytes are in the buffer    
        exp =  int(self.ser.in_waiting )
        if exp == 0:
            return [-2]
        if debug:
            print('received bytes: ', exp)
        # prepare a receive array with length of exp, the amount of bytes in the buffer
        receive = bytearray( exp )
        # read the bytes into the buffer and return
        self.ser.readinto(receive)
        return list(receive)

    def set_ups_to_smart_mode(self,debug=False):
        """ Set UPS to Smart Mode
            In order to use the UPS-Link control language to communicate with the UPS, 
            the ASCII character uppercase "Y" must be sent to the UPS when the UPS is 
            turned on. The UPS will respond with the characters "SM". Once put into 
            the smart signaling mode, the UPS's standard signaling outputs are disabled. 
            However, no signaling functionality is lost as UPS-Link duplicates all 
            standard signaling information such as Line Fail and Low Battery.
        """
        receive = self.process_command([ord('Y')], debug)
        if debug == True:
            print('set_ups_to_smart_mode', receive)
        if len(receive) < 4:
            return -1
        else:
            if receive[0] != 83:      # S
                return -1
            if receive[1] != 77:      # M
                return -1
            if receive[2] != 13:      # CR
                return -1
            if receive[3] != 10:      # LR
                return -1
            return 0

    def return_to_simple_mode(self,debug=False):
        """ 
            Sending the ASCII character "R" forces the UPS out of Smart mode. The response is 
            always "BYE" (assuming the UPS is in Smart Mode when the “R” is sent). To get back 
            into Smart mode, you must send a "Y". The R command is valid on 3G (third generation) 
            Smart-UPS models. It is also valid on Smart-UPS v/s and Back-UPS Pro models, except 
            for early models that do not have the necessary firmware version. 
            The R command is not valid on Matrix-UPS.        
        """
        receive = self.process_command([ord('R')], debug)
        if debug == True:
            print('return_to_simple_mode', receive)
        if len(receive) < 5:
            return -1
        else:
            if receive[0] != 66:      # B
                return -1
            if receive[1] != 89:      # Y
                return -1
            if receive[2] != 69:      # E
                return -1
            if receive[3] != 13:      # CR
                return -1
            if receive[4] != 10:      # LR
                return -1
            return 0

    def test_lights_and_beeper(self,debug=False):
        """ Test Lights and Beeper
            
            Sending the ASCII character uppercase "A" causes the 
            UPS to illuminate all front panel indicator LEDs 
            (where applicable) and sound the beeper for 2 seconds. 
            The UPS responds to this command by sending the characters "OK".
        """
        receive = self.process_command([ord('A')], debug)
        if debug == True:
            print('test_lights_and_beeper', receive)
        if len(receive) < 4:
            return -1
        else:
            if receive[0] != 79:      # O
                return -1
            if receive[1] != 75:      # K
                return -1
            if receive[2] != 13:      # CR
                return -1
            if receive[3] != 10:      # LR
                return -1
            return 0

    # def turn_off_after_delay(self,debug=False):
    #     """
    #         Sending an ASCII character sequence uppercase "K" uppercase "K", with a 
    #         greater than 1.5 second delay between characters, causes the UPS to turn 
    #         off based on the Shutdown Delay (the "p" command in section 3.4, “UPS 
    #         Customizing Commands”). The KK character sequence, with the greater than 
    #         1.5 second delay between the K characters, is shown in this document as 
    #         “K (>1.5 sec)K.” If the delay between characters is less than 1.5 seconds, 
    #         or if another command is sent to the UPS between the "K" characters, the
    #         UPS will not recognize the "K" command. When processing a command that 
    #         conflicts with the Turn Off after Delay function, the UPS returns the message 
    #         "NA" immediately after the "K (>1.5 sec)K" command is sent. Older UPSs return 
    #         an "*" (asterisk) to the terminal to signal that it is about to turn off. Newer 
    #         models respond with a "OK" to indicate that the UPS received the command. No 
    #         other commands will be processed following the "*" or "OK" response. If 
    #         turned off while operating on-battery, the UPS does not restart when the utility is restored.

    #         This command is not supported on the Smart-UPS 250, 400, and 370ci. 
    #         The Matrix-UPS's battery charger is disabled when shut off. 
    #         Do not operate the Matrix-UPS in this mode for extended periods because 
    #         the batteries may become discharged.
    #     """
    #     receive = self.process_command([ord('Y')], debug)
    #     if debug == True:
    #         print('turn_off_after_delay', receive)
    #     if len(receive) == 0:
    #         return -1
    #     if receive[0] != 83:      # S
    #         return -1
    #     if receive[1] != 77:      # M
    #         return -1
    #     if receive[-2] != 13:      # CR
    #         return -1
    #     if receive[-1] != 10:      # LR
    #         return -1
    #     return 0

    # def shut_down_ups_on_battery(self,debug=False):
    #     """
    #         Sending the ASCII character uppercase "S" to the UPS while operating on-battery 
    #         causes the UPS to shut down following a shutdown delay programmed by the Shutdown 
    #         Delay command (the "p" command documented in Section 3.4, “UPS Customizing Commands”). 
    #         The UPS's output returns when the utility power is restored. If the utility power is 
    #         restored within the UPS shutdown delay interval, the UPS still shuts down at the end 
    #         of the interval (and then immediately restarts). The UPS responds to this command with 
    #         the characters "OK". The commands "K(>1.5 sec)K", "U", "W", "Z(>1.5 sec) Z", "@ddd" 
    #         and "-" will not be processed following the "OK" response. If these commands are sent, 
    #         the UPS returns the characters "NA". During the time the UPS's output is unpowered, 
    #         the UPS's internal electronics remain in a "sleep" mode as indicated by the marquee 
    #         sequence of the UPS LEDs or message given on the UPS's display.
            
    #         The UPS responds to this command only when running on battery, and the UPS stays on battery after the command is sent.
            
    #         The automatic turn on feature on APC models Smart-UPS 400 and UPS 370ci must be disabled 
    #         via the option switch in order for the command to take effect.
    #     """
    #     receive = self.process_command([ord('Y')], debug)
    #     if debug == True:
    #         print('shut_down_ups_on_battery', receive)
    #     if len(receive) == 0:
    #         return -1
    #     if receive[0] != 83:      # S
    #         return -1
    #     if receive[1] != 77:      # M
    #         return -1
    #     if receive[-2] != 13:      # CR
    #         return -1
    #     if receive[-1] != 10:      # LR
    #         return -1
    #     return 0


    def simulate_power_failure(self,debug=False):
        """
            Sending the ASCII character uppercase "U" forces the UPS to switch briefly to 
            battery operation. The UPS responds to this command by sending the characters 
            "OK". When processing a command that conflicts with the simulated power failure 
            function, the UPS returns the message "NA" immediately after the "U" command is sent.
        """
        receive = self.process_command([ord('U')], debug)
        if debug == True:
            print('simulate_power_failure', receive)
        if len(receive) < 4:
            return -1
        else:
            if receive[0] != 79:      # O
                return -1
            if receive[1] != 75:      # K
                return -1
            if receive[2] != 13:      # CR
                return -1
            if receive[3] != 10:      # LR
                return -1
            return 0

    def battery_test(self,debug=False):
        """
            Sending the ASCII character uppercase "W" causes the UPS to run its battery 
            test procedure. The test lasts about 8 seconds. The result of the battery 
            test is saved for five minutes for retrieval via the "X" UPS Status Inquiry 
            Command. Automatic battery testing can be scheduled using the "E" command, 
            documented in Section 3.4, “UPS Customizing Commands.” When processing a 
            command that conflicts with the battery test function, the UPS returns the 
            message "NA" immediately after the "W" command is sent.

            The Matrix-UPS and newer Smart-UPS responds to this command with the characters "OK".
        """
        receive = self.process_command([ord('W')], debug)
        if debug == True:
            print('battery_test', receive)
        if len(receive) < 4:
            return -1
        else:
            if receive[0] != 79:      # O
                return -1
            if receive[1] != 75:      # K
                return -1
            if receive[2] != 13:      # CR
                return -1
            if receive[3] != 10:      # LR
                return -1
            return 0

    def turn_off_ups(self,debug=False):
        """
            Sending an ASCII character sequence uppercase "Z" uppercase "Z", with a 
            greater than 1.5 second delay between characters, causes the UPS to turn off 
            immediately. The ZZ character sequence, with the greater than 1.5 second 
            delay between the Z characters, is shown in this document as “Z(>1.5 sec)Z.” 
            If the delay between characters is less than 1.5 seconds, or if another 
            command is sent to the UPS between the "Z" characters, the UPS does not 
            recognize the "Z" command. When processing a command that conflicts with 
            the turn off function, the UPS returns the message "NA” immediately after 
            the Z(>1.5 sec)Z" command is sent. Older Smart-UPSs return an "*" (asterisk) 
            to the terminal to signal that it is about to turn off.

            This command is not supported on APC models Smart-UPS 250, 400 and UPS 370ci. 
            The Matrix-UPS's battery charger is disabled when shut off. Do not operate the 
            Matrix-UPS in this mode for extended periods because the batteries may become discharged.
        """
        receive = self.process_command([ord('Z')], debug)
        if debug == True:
            print('turn_off_ups', receive)
        time.sleep(2)
        receive = self.process_command([ord('Z')], debug)
        if debug == True:
            print('turn_off_ups', receive)
        if len(receive) != 0:
            return -1
        return 0

    # def shut_down_with_delayed_wake_up(self,debug=False):
    #     """
    #         Sending the ASCII characters "@ddd" causes the UPS to turn off based on the Shutdown Delay (the "p" command, 
    #         documented in Section 3.4, "UPS Customizing Commands"), then restore power to the load after "ddd" tenths of 
    #         an hour have expired. After "ddd" tenths of an hour have expired, the UPS waits an additional delay interval 
    #         specified by the UPS Turn On Delay (the "r" command, documented in Section 3.4, "UPS Customizing Commands").
            
    #         For example, if "@126" is sent to the UPS, the UPS turns off following a 20 second delay (the default value 
    #         of the "p" command) and restarts after 12.6 hours. The UPS ignores invalid characters such as alphabetic 
    #         characters (letters) sent after the "@", and the command must be retried. When processing a command that conflicts 
    #         with the Shut Down with Delayed Wake Up command, the UPS returns the message "NA" immediately after the "@ddd" command is sent.
            
    #         Older UPSs return an "*" (asterisk) to the terminal to signal that they are about to turn off. Matrix-UPSs and 
    #         newer Smart-UPSs return an "OK" to acknowledge receipt of the command. No other commands will be processed 
    #         following the "*" or "OK" response. During the time the UPS's output is unpowered, the UPS's internal electronics 
    #         remain in a "sleep" mode as indicated by the marquee sequence or message given on the UPS's display. A delay in 
    #         addition to that programmed with the "@ddd" command is provided via the "r" command, documented in Section 3.4.

    #         Note that the “automatic turn on” feature on APC models Smart-UPS 400 and UPS 370ci must be disabled via the 
    #         option switch in order for the command to take effect.
    #     """
    #     receive = self.process_command([ord('Y')], debug)
    #     if debug == True:
    #         print('xxxxx', receive)
    #     if len(receive) == 0:
    #         return -1
    #     if receive[0] != 79:      # O
    #         return -1
    #     if receive[1] != 75:      # K
    #         return -1
    #     if receive[-2] != 13:      # CR
    #         return -1
    #     if receive[-1] != 10:      # LR
    #         return -1
    #     return 0

    # def abort_shutdown(self,debug=False):
    #     """
    #         Sending the ASCII character equivalent to the "DEL" key (delete) immediately causes the UPS to 
    #         abort the following shutdown commands: "@ddd" (Shut Down with Delayed Wake Up), "S" (Shut Down 
    #         UPS on Battery) or "K(>1.5 sec)K" (Turn Off after Delay). However, the "K" command, "K(>1.5 sec)K,
    #         " can be aborted only during the delay; once the UPS is shut off, the “DEL” command responds 
    #         "NO" to the "K" command and does not turn back on. When the UPS aborts a shutdown command, the 
    #         UPS turns back on regardless of whether line voltage is good or not. If a newer Smart-UPS is in 
    #         "sleep" mode due to the "@ddd" command, "DEL" brings it out of sleep mode. The response from the 
    #         UPS to the "DEL" command is "OK".

    #         The "DEL" command is valid for APC Matrix-UPS models and newer Smart-UPS models. 
    #         Other APC UPS models do not respond to the command.
    #     """
    #     receive = self.process_command([ord('Y')], debug)
    #     if debug == True:
    #         print('xxxxx', receive)
    #     if len(receive) == 0:
    #         return -1
    #     if receive[0] != 79:      # O
    #         return -1
    #     if receive[1] != 75:      # K
    #         return -1
    #     if receive[-2] != 13:      # CR
    #         return -1
    #     if receive[-1] != 10:      # LR
    #         return -1
    #     return 0

    def run_time_calibration(self,debug=False):
        """
            Sending the ASCII character uppercase "D" immediately causes the UPS to start a run time calibration until 
            less than 25% of full battery capacity is reached. The APC model Matrix-UPS operates on-battery until less 
            than 35% of full battery capacity is reached. This command calibrates the returned run time value. The test 
            begins only if battery capacity is 100%. If battery capacity is less than 100%, the UPS returns the characters 
            "NO". The UPS responds to the "D" command with the characters "OK". The commands "K(>1.5 sec)K", "U", "W", 
            "Z(>1.5 sec)Z", "@ddd" and the "-" will not be processed following the "OK" response. If these commands are 
            sent, the UPS returns the characters "NA". You can abort the run time calibration by sending the "D" command 
            a second time. The "D" command is not available on the Smart-UPS v/s or the Back-UPS Pro.
        """
        receive = self.process_command([ord('D')], debug)
        if debug == True:
            print('run_time_calibration', receive)
        if len(receive) < 4:
            return -1
        if receive[2] != 13:      # CR
            return -2
        if receive[3] != 10:      # LR
            return -2
        #---------------------------------------------        
        if receive[0] == 79 and receive[1] == 75: # OK
            return 0
        if receive[0] == 78 and receive[1] == 79: # NO
            return 1
        if receive[0] == 78 and receive[1] == 65: # NA
            return 2
        #---------------------------------------------
        return -2

    def ups_to_bypass(self,debug=False):
        """
            Sending the ASCII character "^" while the UPS is operating on-line causes the UPS to respond with 
            the characters "BYP" and transfer to bypass mode. Sending the "^" character while the UPS is 
            operating in bypass mode causes the UPS to respond with the characters "INV" and revert to normal 
            on-line operation (note that the UPS may first briefly operate on-battery). The UPS returns the 
            characters "ERR" when the UPS is unable to transfer to or from bypass operation due to low line voltage or UPS fault conditions.

            UPS responses are as follows:
            • BYP - The UPS is attempting to transfer from normal inverter to bypass mode.
            • INV - The UPS is attempting to transfer from bypass mode to normal inverter mode.
            • ERR - The UPS is unable to switch to or from bypass.

            The Bypass command is valid only for APC UPS models that incorporate the bypass function, such as 
            the Matrix-UPS. Other APC UPS models do not respond to the command.
        """
        receive = self.process_command([ord('^')], debug)
        if debug == True:
            print('ups_to_bypass', receive)
        if len(receive) < 4:
            return -1
        if receive[0] != 79:      # O
            return -1
        if receive[1] != 75:      # K
            return -1
        if receive[2] != 13:      # CR
            return -1
        if receive[3] != 10:      # LR
            return -1
        return 0
    
    def turn_ups_on(self,debug=False):
        """
            Sending the key sequence "Ctrl" and ASCII character "N" or "n", followed by a greater 
            than 1.5 second delay, followed by another Ctrl N or Ctrl n is equivalent to momentarily 
            pushing the front ON button of the UPS. The format of the command in this document is 
            shown as Ctrl N(>1.5 sec)Ctrl N. If line voltage is not present, the UPS responds as if a 
            user pushed the front “on” button with no line voltage present. The Ctrl N command is 
            valid only on newer Smart-UPS models.
        """
        receive = self.process_command([14], debug)
        if debug == True:
            print('turn_ups_on', receive)
        time.sleep(2)
        receive = self.process_command([14], debug)
        if debug == True:
            print('turn_ups_on', receive)
        if len(receive) < 4:
            return -1
        if receive[0] != 79:      # O
            return -1
        if receive[1] != 75:      # K
            return -1
        if receive[2] != 13:      # CR
            return -1
        if receive[3] != 10:      # LR
            return -1
        return 0



###############################################################################

    def battery_test_result(self,debug=False):
        """
            Sending the ASCII character uppercase "X" causes the UPS to respond with the results of the 
            last battery test performed. The results are saved for only 5 minutes. The messages returned 
            include: "OK" indicating a good battery, "BT" indicating a battery that has failed the test 
            due to insufficient capacity, "NG” indicating an invalid test due to overload, and "NO" 
            indicating that no test results are available (i.e. the "W" Battery Test command was sent 
            more than 5 minutes prior to the "X" command).
        """
        receive = self.process_command([ord('X')], debug)
        if debug == True:
            print('battery_test_result', receive)
        if len(receive) < 4:
            return -1
        if receive[2] != 13:      # CR
            return -1
        if receive[3] != 10:      # LR
            return -1
        #---------------------------------------------        
        if receive[0] == 79 and receive[1] == 75: # OK
            return 0
        if receive[0] == 66 and receive[1] == 84: # BT
            return 1
        if receive[0] == 78 and receive[1] == 71: # NG
            return 2
        if receive[0] == 78 and receive[1] == 79: # NO
            return 3
        #---------------------------------------------
        return -2

    def number_of_battery_packs(self,debug=False):
        """
            Sending the ASCII character ">" causes the UPS to respond with a three-digit number directly 
            representing the number of external battery packs connected to the UPS.

            This command is valid only for APC UPS models designed to operate with SmartCell battery packs, 
            such as the Matrix-UPS. Only these UPSs can automatically sense the number of battery packs connected. 
            Other APC UPS models do not respond to the command.

            See the ">" (Battery Pack Configuration) command in Section 3.4, “UPS Customizing Commands,” for 
            information on manually entering the number of battery packs for UPSs, such as 3G (third generation) 
            Smart-UPS XL models, that support external battery packs but do not have the capacity to automatically sense the number.
        """
        receive = self.process_command([ord('>')], debug)
        if debug == True:
            print('number_of_battery_packs', receive)
        if len(receive) < 5:
            return -1
        if receive[3] != 13:      # CR
            return -1
        if receive[4] != 10:      # LR
            return -1
        #------------------------------------
        try:
            return int( chr(receive[0]) + chr(receive[1]) + chr(receive[2]) )
        except:
            return -2

    # def number_of_bad_battery_packs(self,debug=False):
    #     """
    #         Sending the ASCII character "<" causes the UPS to respond with a three-digit number directly representing 
    #         the number of bad battery packs connected to the UPS.

    #         This command is valid only for APC UPS models designed to operate with APC SmartCell battery packs, 
    #         such as the Matrix-UPS. Other APC UPS models do not respond to the command.
    #     """
    #     receive = self.process_command([ord('<')], debug)
    #     if debug == True:
    #         print('xxxxx', receive)
    #     if len(receive) == 0:
    #         return -1
    #     if receive[-2] != 13:      # CR
    #         return -1
    #     if receive[-1] != 10:      # LR
    #         return -1
    #     #-----------------------------------
    #     if receive[0] != 79:      # O
    #         return -1
    #     if receive[1] != 75:      # K
    #         return -1
    #     return 0
    
    def transfer_cause(self,debug=False):
        """
            Sending the ASCII character uppercase "G" causes the UPS to respond with the reason for the most recent 
            transfer to on-battery operation. The UPS returns one of the following ASCII characters:

            "R" for transfer due to unacceptable utility voltage rate of change.
            "H" for transfer due to detection of high utility voltage.
            "L" for transfer due to detection of low utility voltage.
            "T" for transfer due to detection of a line voltage notch or spike.
            "O" if no transfers have occurred yet.
            "S" for transfer in response to a UPS-Link Control Command (e.g. the Simulate Power Failure
                command, "U") or activation of the UPS's Test control (where applicable).

            If the UPS has not transferred to on-battery operation since being turned on, the UPS responds with the ASCII character "O".
        """
        receive = self.process_command([ord('G')], debug)
        if debug == True:
            print('transfer_cause', receive)
        if len(receive) < 3:
            return -1
        if receive[1] != 13:      # CR
            return -1
        if receive[2] != 10:      # LR
            return -1
        #-----------------------------------
        if receive[0] == 82:      # R
            return 1
        if receive[0] == 72:      # H
            return 2
        if receive[0] == 76:      # L
            return 3
        if receive[0] == 84:      # T
            return 4
        if receive[0] == 79:      # O
            return 0
        if receive[0] == 83:      # S
            return 5
        return -2

    # def firmware_version(self,debug=False):
    #     """
    #         Sending the ASCII character uppercase "V" causes the UPS to respond with a three character 
    #         alphanumeric representation of the UPS's firmware version. In the returned message, the first 
    #         character represents the UPS's base model type, the second character represents the UPS's 
    #         firmware version letter (which, for third generation Smart-UPS models is always W), and the 
    #         third character represents the UPS's utility voltage version. Decode the UPS base model type 
    #         and utility voltage version characters according to the following tables. Other UPS model type 
    #         characters may be included in the future. The "V" command is not available on the Smart-UPS v/s or the Back-UPS Pro.

    #         APC UPS Models (including derivatives such as RM, XL, etc.)     1stCharacter
    #         Smart-UPS 250                                                   2
    #         Smart-UPS 400, UPS 370ci                                        4
    #         Smart-UPS 600                                                   6
    #         Smart-UPS 900                                                   7
    #         Smart-UPS 1250                                                  8
    #         Smart-UPS 2000                                                  9
    #         Matrix-UPS 3000                                                 0
    #         Matrix-UPS 5000                                                 5
    #         Smart-UPS 450                                                   F
    #         Smart-UPS 700                                                   G
    #         Smart-UPS 1000                                                  I
    #         Smart-UPS 1400                                                  K
    #         Smart-UPS 2200                                                  M
    #         Smart-UPS 3000                                                  O

    #         Utility Voltage Version                                         3rdCharacter
    #         100 Vac                                                         A
    #         120 Vac                                                         D
    #         208 Vac                                                         M
    #         220/230/240 Vac                                                 I
    #         Matrix-UPS configured for 208 Vac input                         M
    #         Matrix-UPS configured for 240 Vac input                         I
    #         Matrix-UPS configured for 200 Vac input/output                  J
    #     """
    #     receive = self.process_command([ord('V')], debug)
    #     if debug == True:
    #         print('firmware_version', receive)
    #     if len(receive) == 0:
    #         return -1
    #     if receive[-2] != 13:      # CR
    #         return -1
    #     if receive[-1] != 10:      # LR
    #         return -1
    #     #-----------------------------------
    #     return 0

    def ups_nominal_battery_voltage_rating(self,debug=False):
        """
            Sending the ASCII character lowercase "g" causes the UPS to respond with a three-digit 
            number representing the UPS's nominal battery voltage rating. This is not the UPS's actual 
            battery voltage, which is reported by the "B" command, documented in Section 3.3, 
            "UPS Power Inquiry Commands"). For example, the UPS returns "024" (or no response on 
            early version UPSs) for a 24 Volt battery system, "018" for a 18 Volt battery system, 
            and "048" for a 48 Volt battery system.
        """
        receive = self.process_command([ord('g')], debug)
        if debug == True:
            print('ups_nominal_battery_voltage_rating', receive)
        if len(receive) < 5:
            return -1
        if receive[3] != 13:      # CR
            return -1
        if receive[4] != 10:      # LR
            return -1
        #-----------------------------------
        try:
            return int( chr(receive[0]) + chr(receive[1]) + chr(receive[2]) )
        except:
            return -2

    def battery_capacity(self,debug=False):
        """
            Sending the ASCII character lowercase "f" causes the UPS to respond with "ddd.d" 
            characters directly representing the UPS's remaining battery capacity as a percent 
            of the fully charged condition. The "f" command is not available on the 
            Smart-UPS v/s or the Back-UPS Pro.
        """
        OK = False
        counter = 0
        while (OK == False) and (counter < 3):
            receive = self.process_command([ord('f')], debug)
            if debug == True:
                print('battery_capacity', receive)
            if len(receive) < 7:
                print('battery_capacity', receive)
                result = -1
            else:
                if receive[5] != 13:      # CR
                    result = -1
                if receive[6] != 10:      # LR
                    result = -1
                #-----------------------------------
                try:
                    result = float( chr(receive[0]) + chr(receive[1]) + chr(receive[2]) + chr(receive[3]) + chr(receive[4]) )
                    OK = True
                except:
                    result = -2
            counter += 1
        return result


    def acceptable_line_quality(self,debug=False):
        """
            Sending the ASCII character "9" causes the UPS to respond with either the characters "FF", 
            denoting acceptable utility line quality, or "00", denoting unacceptable utility line quality. 
            No attempt is made here to better qualify the meaning of the returned messages.
        """
        receive = self.process_command([ord('9')], debug)
        if debug == True:
            print('acceptable_line_quality', receive)
        if len(receive) < 4:
            return -1
        if receive[2] != 13:      # CR
            return -1
        if receive[3] != 10:      # LR
            return -1
        #-----------------------------------
        if receive[0] == 70 and receive[1] == 70:      # FF
            return 0
        if receive[0] == 48 and receive[1] == 48:      # 00
            return 1
        return -2

    def ups_status(self,debug=False):
        """
            Sending the ASCII character uppercase "Q" causes the UPS to respond with a two-digit hexadecimal 
            coded message that can be deciphered to find the operational status of the UPS, as shown in the 
            following table. Bits 7 through 2 reflect the state of the UPS. For example, when the Smart-UPS is 
            performing a self-test, the state of Bit 3 also changes. Decode the two hexadecimal characters to 
            get two four-bit binary words. The second alphanumeric character represents bits 0 through 3; the 
            first alphanumeric character represents bits 4 through 7.

            Bit Representative UPS Operational Status
            7   1 = replace battery condition
            6   1 = low battery condition
            5   1 = overloaded output condition
            4   1 = on-battery mode of operation
            3   1 = on-line mode of operation
            2   1 = SmartBoost mode of operation (where applicable)
            1   1 = SmartTrim mode of operation (where applicable)
            0   1= run time calibration running

            The Smart-UPS v/s and Back-UPS Pro do not report bit 0. Older Smart-UPS models 
            (second generation) do not report bit 1, since they do not support SmartTrim.
        """
        OK = False
        counter = 0
        while (OK == False) and (counter < 3):
            receive = self.process_command([ord('Q')], debug)
            if debug == True:
                print('ups_status', receive)
            if len(receive) < 4:
                result = -1
            if receive[2] != 13:      # CR
                result = -1
            if receive[3] != 10:      # LR
                result = -1
            #-----------------------------------
            try:
                result = int(chr(receive[0])) + 10*int(chr(receive[1]))
                OK = True
            except:
                result = -2
            counter += 1
        return result




###############################################################################
# 3.3 UPS power inquiry commands

    def load_current(self,debug=False):
        """
            Sending the ASCII character "/" (slant) causes the UPS to respond with "dd.dd" characters 
            directly representing the true rms load current drawn from UPS. The typical accuracy of 
            this measurement is ±7.5% of the load rating of UPS.

            This command is valid only for the APC Matrix-UPS. Other APC UPS models do not respond to the command.
        """
        receive = self.process_command([ord('/')], debug)
        if debug == True:
            print('load_current', receive)
        if len(receive) < 7:
            return -1
        if receive[5] != 13:      # CR
            return -1
        if receive[6] != 10:      # LR
            return -1
        #-----------------------------------
        if receive[0] == 78 and receive[1] == 65: # NA
            return 0
        #-----------------------------------
        try:
            return float( chr(receive[0]) + chr(receive[1]) + chr(receive[2]) + chr(receive[3]) + chr(receive[4]) )
        except:
            return -2

    def apparent_load_power(self,debug=False):
        """
            Sending the ASCII character "\" (reverse slant) causes the UPS to respond with "ddd.dd" characters 
            directly representing the UPS's output load as a percentage of the full rated load in Volt-Amps. 
            The typical accuracy of this measurement is ±5% of the maximum of 105%.
            
            This command is valid only for the APC Matrix-UPS. Other APC UPS models do not respond to the command.
        """
        receive = self.process_command([ord('Y')], debug)
        if debug == True:
            print('apparent_load_power', receive)
        if len(receive) < 7:
            return -1
        if receive[5] != 13:      # CR
            return -1
        if receive[6] != 10:      # LR
            return -1
        #-----------------------------------
        if receive[0] == 78 and receive[1] == 65: # NA
            return 0
        #-----------------------------------
        try:
            return float( chr(receive[0]) + chr(receive[1]) + chr(receive[2]) + chr(receive[3]) + chr(receive[4]) )
        except:
            return -2


    def battery_voltage(self,debug=False):
        """
            Sending the ASCII character uppercase "B" caused the UPS to respond with "dd.dd" characters 
            directly representing the UPS's present battery voltage. The typical accuracy of this measurement 
            is ±5% of the maximum value of 24 Vdc, 34 Vdc or 68 Vdc (depending upon the UPS's nominal battery voltage). 
            See the UPS Nominal Battery Voltage Rating command, "g", in Section 3.2, "UPS Status Inquiry Commands." 
            The "B" command is not available on the Smart-UPS v/s or the Back-UPS Pro.
        """
        OK = False
        counter = 0
        while (OK == False) and (counter < 3):
            receive = self.process_command([ord('B')], debug)
            if debug == True:
                print('battery_voltage', receive)
            if len(receive) < 7:
                result = -1
            if receive[5] != 13:      # CR
                result = -1
            if receive[6] != 10:      # LR
                result = -1
            #-----------------------------------
            try:
                result = float( chr(receive[0]) + chr(receive[1]) + chr(receive[2]) + chr(receive[3]) + chr(receive[4]) )
                OK = True
            except:
                result = -2
            counter += 1
        return result
    

    def ups_internal_temperature(self,debug=False):
        """
            Sending the ASCII character uppercase "C" causes the UPS to respond with "ddd.d" characters directly 
            representing the UPS's present internal operating temperature in degrees Celsius. The typical accuracy 
            of this measurement is ±5% of the full scale value of 100°C. The "C" command is not available on the 
            Smart-UPS v/s or the Back-UPS Pro.
        """
        OK = False
        counter = 0
        while (OK == False) and (counter < 3):
            receive = self.process_command([ord('C')], debug)
            if debug == True:
                print('ups_internal_temperature', receive)
            if len(receive) < 7:
                result = -1
            if receive[5] != 13:      # CR
                result = -1
            if receive[6] != 10:      # LR
                result = -1
            #-----------------------------------
            try:
                result = float( chr(receive[0]) + chr(receive[1]) + chr(receive[2]) + chr(receive[3]) + chr(receive[4]) )
                OK = True
            except:
                result = -2
            counter += 1
        return result
        

    def ups_and_utility_operating_frequency(self,debug=False):
        """
            Sending the ASCII character uppercase "F" causes the UPS to respond with "dd.dd" characters 
            directly representing the UPS's present internal operating frequency. When operating on-line, 
            the UPS's internal operating frequency is synchronized to the line within variations within 3 Hz 
            of the nominal 50 or 60 Hz. The typical accuracy of this measurement is ±1% of the full scale value 
            of 63 Hz. The "F" command is not available on the Smart-UPS v/s or the Back-UPS Pro.
        """
        OK = False
        counter = 0
        while (OK == False) and (counter < 3):
            receive = self.process_command([ord('F')], debug)
            if debug == True:
                print('ups_and_utility_operating_frequency', receive)
            if len(receive) < 7:
                result = -1
            if receive[5] != 13:      # CR
                result = -1
            if receive[6] != 10:      # LR
                result = -1
            #-----------------------------------
            try:
                result = float( chr(receive[0]) + chr(receive[1]) + chr(receive[2]) + chr(receive[3]) + chr(receive[4]) )
                OK = True
            except:
                result = -2
            counter += 1
        return result

    def line_voltage(self,debug=False):
        """
            Sending the ASCII character uppercase "L" causes the UPS to respond with "ddd.d" characters directly 
            representing the UPS's present input voltage. The typical accuracy of this measurement is ±4% of the 
            aximum value of 142 Vac for 100 Vac and 120 Vac version UPSs. The typical accuracy of this measurement 
            is ±4% of the maximum value of 285 Vac for 208 Vac and 220/230/240 Vac version UPSs. The "L" command is 
            not available on the Smart-UPS v/s or the Back-UPS Pro.
        """
        OK = False
        counter = 0
        while (OK == False) and (counter < 3):
            receive = self.process_command([ord('L')], debug)
            if debug == True:
                print('line_voltage', receive)
            if len(receive) < 7:
                result = -1
            if receive[5] != 13:      # CR
                result = -1
            if receive[6] != 10:      # LR
                result = -1
            #-----------------------------------
            try:
                result = float( chr(receive[0]) + chr(receive[1]) + chr(receive[2]) + chr(receive[3]) + chr(receive[4]) )
                OK = True
            except:
                result -2
            counter += 1
        return result


    def maximum_line_voltage(self,debug=False):
        """
            Sending the ASCII character uppercase "M" causes the UPS to respond with "ddd.d" characters directly 
            representing the UPS's maximum input voltage as determined during the interval between command messages. 
            For example, if "M" is sent to the UPS every 24 hours, the UPS returns characters indicating the maximum 
            voltage over the last 24 hours. The "M" command is not available on the Smart-UPS v/s or the Back-UPS Pro.
        """
        receive = self.process_command([ord('M')], debug)
        if debug == True:
            print('maximum_line_voltage', receive)
        if len(receive) < 7:
            return -1
        if receive[5] != 13:      # CR
            return -1
        if receive[6] != 10:      # LR
            return -1
        #-----------------------------------
        try:
            return float( chr(receive[0]) + chr(receive[1]) + chr(receive[2]) + chr(receive[3]) + chr(receive[4]) )
        except:
            return -2

    def minimum_line_voltage(self,debug=False):
        """
            Sending the ASCII character uppercase "N" causes the UPS to respond with "ddd.d" characters directly 
            representing the UPS's minimum input voltage as determined during the interval between command messages. 
            For example, if "N" is sent to the UPS every 24 hours, the UPS returns characters indicating the minimum 
            voltage over the last 24 hours. The "N" command is not available on the Smart-UPS v/s or the Back-UPS Pro.
        """
        receive = self.process_command([ord('N')], debug)
        if debug == True:
            print('minimum_line_voltage', receive)
        if len(receive) < 7:
            return -1
        if receive[5] != 13:      # CR
            return -1
        if receive[6] != 10:      # LR
            return -1
        #-----------------------------------
        try:
            return float( chr(receive[0]) + chr(receive[1]) + chr(receive[2]) + chr(receive[3]) + chr(receive[4]) )
        except:
            return -2

    def output_voltage(self,debug=False):
        """
            Sending the ASCII character uppercase "O" causes the UPS to respond with "ddd.d" characters directly 
            representing the UPS's output voltage. The typical accuracy of this measurement is ±4% of the maximum 
            value of 142 Vac for 100 Vac and 120 Vac version UPSs. The typical accuracy of this measurement is ±4% 
            of the maximum value of 285 Vac for 208 Vac and 220/230/240 Vac version UPSs. The "O" command is not 
            available on the Smart-UPS v/s or the Back-UPS Pro.
        """
        OK = False
        counter = 0
        while (OK == False) and (counter < 3):
            receive = self.process_command([ord('O')], debug)
            if debug == True:
                print('output_voltage', receive)
            if len(receive) < 7:
                result = -1
            if receive[5] != 13:      # CR
                result = -2
            if receive[6] != 10:      # LR
                result = -3
            #-----------------------------------
            try:
                result = float( chr(receive[0]) + chr(receive[1]) + chr(receive[2]) + chr(receive[3]) + chr(receive[4]) )
                OK = True
            except:
                result -4
            counter += 1
        return result

    def load_power(self,debug=False):
        """
            Sending the ASCII character uppercase "P" causes the UPS to respond with "ddd.d" characters directly 
            representing the UPS's output load as a percentage of full rated load in Watts. The typical accuracy of 
            this measurement is ±3% of the maximum of 105%. The "P" command is not available on the Smart-UPS v/s or the Back-UPS Pro.
        """
        OK = False
        counter = 0
        while (OK == False) and (counter < 3):
            receive = self.process_command([ord('P')], debug)
            if debug == True:
                print('load_power', receive)
            if len(receive) < 7:
                result = -1
            else:
                if receive[5] != 13:      # CR
                    result = -1
                if receive[6] != 10:      # LR
                    result = -1
                #-----------------------------------
                try:
                    result = float( chr(receive[0]) + chr(receive[1]) + chr(receive[2]) + chr(receive[3]) + chr(receive[4]) )
                    OK = True
                except:
                    result = -2
            counter += 1
        return result




'''

    def xxxxx(self,debug=False):
        """

        """
        receive = self.process_command([ord('Y')], debug)
        if debug == True:
            print('xxxxx', receive)
        if len(receive) == 0:
            return -1
        if receive[-2] != 13:      # CR
            return -1
        if receive[-1] != 10:      # LR
            return -1
        #-----------------------------------
        if receive[0] != 79:      # O
            return -1
        if receive[1] != 75:      # K
            return -1
        return 0

        
'''   