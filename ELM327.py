# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

#/***************************************************************************/
#/* Raspberry Pi ELM327 OBBII CAN BUS Diagnostic Software.                  */
#/*                                                                         */
#/* (C) Jason Birch 2018-04-27 V1.01                                        */
#/***************************************************************************/



import time
import serial



class ELM327:
	# Serial port constants. 
	SERIAL_PORT_NAME = "/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A800eaG9-if00-port0"
	SERIAL_PORT_BAUD = 38400
	SERIAL_PORT_TIME_OUT = 60

	# ELM327 Device related constants.
	ELM_CONNECT_SETTLE_PERIOD = 5
	ELM_CONNECT_TRY_COUNT = 5

	# Constant string responses.
	STRING_NOT_IMPLEMENTED = "!NOT IMPLEMENTED!"
	STRING_NO_DATA = "N/A"
	STRING_ERROR = "!ERROR!"
	STRING_TODO = ":TODO:"
	STRING_INVALID = "[INVALID]"
	STRING_NO_DESCRIPTION = "[NO DESCRIPTION]"


	# PID Numbers and their function pointers implemented in this class.
	PidFunctions = {}



	def __init__(self):
		self.InitResult = ""
		self.ValidPIDs = {}

#  /*************************************************/
# /* Read Vehicle OBD Standards lookup table data. */
#/*************************************************/
		self.VehicleObdStandards = {}
		try:
			with open("VehicleObdStandards.txt") as ThisFile:
				for ThisLine in ThisFile:
					Digit, Code = ThisLine.partition(" ")[::2]
					self.VehicleObdStandards[Digit] = Code.strip()
		except Exception as Catch:
			print("***** ERROR ***** VehicleObdStandards.txt : " + str(Catch))
			self.InitResult += "FAILED TO READ FILE: VehicleObdStandards.txt\n"


#  /**********************************************************/
# /* Read Commanded Secondary Air Status lookup table data. */
#/**********************************************************/
		self.CommandedSecondaryAirStatus = {}
		try:
			with open("CommandedSecondaryAirStatus.txt") as ThisFile:
				for ThisLine in ThisFile:
					Digit, Code = ThisLine.partition(" ")[::2]
					self.CommandedSecondaryAirStatus[Digit] = Code.strip()
		except Exception as Catch:
			print("***** ERROR ***** CommandedSecondaryAirStatus.txt : " + str(Catch))
			self.InitResult += "FAILED TO READ FILE: CommandedSecondaryAirStatus.txt\n"


#  /**********************************************/
# /* Read Fuel System Status lookup table data. */
#/**********************************************/
		self.FuelSystemStatus = {}
		try:
			with open("FuelSystemStatus.txt") as ThisFile:
				for ThisLine in ThisFile:
					Digit, Code = ThisLine.partition(" ")[::2]
					self.FuelSystemStatus[Digit] = Code.strip()
		except Exception as Catch:
			print("***** ERROR ***** FuelSystemStatus.txt : " + str(Catch))
			self.InitResult += "FAILED TO READ FILE: FuelSystemStatus.txt\n"


#  /**********************************************/
# /* Read OBDII Trouble Code lookup table data. */
#/**********************************************/
		self.TroubleCodePrefix = {}
		try:
			with open("TroubleCodePrefix.txt") as ThisFile:
				for ThisLine in ThisFile:
					Digit, Code = ThisLine.partition(" ")[::2]
					self.TroubleCodePrefix[Digit] = Code.strip()
		except Exception as Catch:
			print("***** ERROR ***** TroubleCodePrefix.txt : " + str(Catch))
			self.InitResult += "FAILED TO READ FILE: TroubleCodePrefix.txt\n"

#  /**********************************************************/
# /* Read OBDII Trouble Code Description lookup table data. */
#/**********************************************************/
		self.TroubleCodeDescriptions = {}
		# Load the ISO/SAE Trouble Code Descriptions.
		try:
			with open("TroubleCodes-ISO-SAE.txt") as ThisFile:
				for ThisLine in ThisFile:
					Code, Description = ThisLine.partition(" ")[::2]
					self.TroubleCodeDescriptions[Code] = Description.strip()
		except Exception as Catch:
			print("***** ERROR ***** TroubleCodes-ISO-SAE.txt : " + str(Catch))
			self.InitResult += "FAILED TO READ FILE: TroubleCodes-ISO-SAE.txt\n"

		# Load the Vehicle/Manufacturer Trouble Code Descriptions.
		try:
			with open("TroubleCodes-R53_Cooper_S.txt") as ThisFile:
				for ThisLine in ThisFile:
					Code, Description = ThisLine.partition(" ")[::2]
					self.TroubleCodeDescriptions[Code] = Description.strip()
		except Exception as Catch:
			print("***** ERROR ***** TroubleCodes-R53_Cooper_S.txt : " + str(Catch))
			self.InitResult += "FAILED TO READ FILE: TroubleCodes-R53_Cooper_S.txt\n"

#  /***************************************************/
# /* Read Mode 01 PID description lookup table data. */
#/***************************************************/
		self.PidDescriptionsMode01 = {}
		try:
			with open("PidDescriptionsMode01.txt") as ThisFile:
				for ThisLine in ThisFile:
					Digit, Code = ThisLine.partition(" ")[::2]
					self.PidDescriptionsMode01[Digit] = Code.strip()
		except:
			self.InitResult += "FAILED TO READ FILE: PidDescriptionsMode01.txt\n"

#  /***************************************************/
# /* Read Mode 05 PID description lookup table data. */
#/***************************************************/
		self.PidDescriptionsMode05 = {}
		try:
			with open("PidDescriptionsMode05.txt") as ThisFile:
				for ThisLine in ThisFile:
					Digit, Code = ThisLine.partition(" ")[::2]
					self.PidDescriptionsMode05[Digit] = Code.strip()
		except:
			self.InitResult += "FAILED TO READ FILE: PidDescriptionsMode05.txt\n"

#  /***************************************************/
# /* Read Mode 09 PID description lookup table data. */
#/***************************************************/
		self.PidDescriptionsMode09 = {}
		try:
			with open("PidDescriptionsMode09.txt") as ThisFile:
				for ThisLine in ThisFile:
					Digit, Code = ThisLine.partition(" ")[::2]
					self.PidDescriptionsMode09[Digit] = Code.strip()
		except:
			self.InitResult += "FAILED TO READ FILE: PidDescriptionsMode09.txt\n"

#  /****************************************************************/
# /* Open the required serial port which the ELM327 device is on. */
#/****************************************************************/
		try:
			self.ELM327 = serial.Serial(self.SERIAL_PORT_NAME, self.SERIAL_PORT_BAUD)
			self.ELM327.timeout = self.SERIAL_PORT_TIME_OUT
			self.ELM327.write_timeout = self.SERIAL_PORT_TIME_OUT

			# Initialize the ELM327 device.
			self.Response = self.GetResponse(b'AT Z\r')

			# Echo Off, for faster communications.
			self.Response = self.GetResponse(b'AT E0\r')
			if self.Response != 'AT E0\nOK\n':
				self.InitResult += "FAILED: AT E0 (Set Echo Off)\n"

			# Don't print space characters, for faster communications.
			self.Response = self.GetResponse(b'AT S0\r')
			if self.Response != 'OK\n':
				self.InitResult += "FAILED: AT S0 (Set Space Characters Off)\n"

			# Set CAN communication protocol to ISO 9141-2 or auto detect on fail.
			self.Response = self.GetResponse(b'AT SP A3\r')
			if self.Response != 'OK\n':
				self.InitResult += "FAILED: AT SP A3 (Set Protocol ISO 9141-2 / Auto)\n"

			# Set CAN Baud to high speed.
			self.Response = self.GetResponse(b'AT IB 10\r')
			if self.Response != 'OK\n':
				self.InitResult += "FAILED: AT IB 10 (Set High Speed CAN BUS)\n"
		except:
			self.InitResult += "FAILED TO INITIALIZE ELM327 DEVICE.\n"



#/***********************************************/
#/* Close the serial port to the ELM327 device. */
#/***********************************************/
	def Close(self):
		self.Result = True

		# Close serial port.
		try:
			self.ELM327.close()
		except:
			self.Result = False



#/**************************************************/
#/* Perform a simple communication with the ELM327 */
#/* device to see if it is present and responding. */
#/**************************************************/
	def IsELM327Present(self):
		self.Result = False

		try:
			if self.GetResponse(b'AT @1\r') != "":
				self.Result = True
		except:
			self.Result = False

		return self.Result



#/*************************************************/
#/* Get any errors or warnings which occured      */
#/* during creation of an instance of this class. */
#/*************************************************/
	def GetInitResult(self):
		return self.InitResult



#/*******************************************/
#/* Get infomation about the ELM327 device. */
#/*******************************************/
	def GetInfo(self):
		self.Result = ""

		# Get the current serial port in use by the ELM327 device.
		self.Result += "Serial Port: " + self.ELM327.name + "\n"
		# Get the ELM device version.
		self.Response = self.GetResponse(b'AT I\r')
		self.Result += "ELM Device Version:      " + self.Response
		# Get the ELM device description.
		self.Response = self.GetResponse(b'AT @1\r')
		self.Result += "ELM Device Description:  " + self.Response
		# Get the ELM device user supplied description.
		self.Response = self.GetResponse(b'AT @2\r')
		self.Result += "ELM Device User Data:    " + self.Response
		# Get the current OBDII data protocol after OBDII CAN BUS communication.
		self.Response = self.GetResponse(b'AT DP\r')
		self.Result += "Using CAN BUS Protocol:  " + self.Response
		# Get the Voltage measured at the OBDII connector.
		self.Response = self.GetResponse(b'AT RV\r')
		self.Result += "Volt At OBDII Connector: " + self.Response
		# Get the CAN status.
		self.Response = self.GetResponse(b'AT CS\r')
		self.Result += "CAN Status:              " + self.Response
		# Get the key words.
		self.Response = self.GetResponse(b'AT KW\r')
		self.Result += "Key Words:               " + self.Response
		# Get the ELM327 buffer dump.
		self.Response = self.GetResponse(b'AT BD\r')
		self.Result += "ELM327 Buffer Dump:      " + self.Response
		# Get the programmable paramaters.
		self.Response = self.GetResponse(b'AT PPS\r')
		self.Result += "ELM327 Programmable Paramaters:\n" + self.Response

		return self.Result



#/********************************************************/
#/* Connect the ELM327 device to the CAN BUS on the ECU. */
#/* Then get a list of all of the valid PID addresses    */
#/* the ECU supports.                                    */
#/********************************************************/
	def Connect(self):
		self.Result = True

		# Wait before tring to connect to ensure EML device is idle.
		time.sleep(self.ELM_CONNECT_SETTLE_PERIOD)
		# Request Mode 01 PID 00 (Supported PIDs for Mode 01) to test connection.
		self.Response = self.GetResponse(b'0100\r')
		if self.Response.find("UNABLE TO CONNECT") != -1:
			self.Result = False
			# Close serial port if connection failed.
			self.ELM327.close()

		if self.Result == True:
			# Manually add standard PIDs supported, prefix with '!', don't show as user selectable option.
			# Application specific display locations.
			self.ValidPIDs['03'] = "! Show stored Diagnostic Trouble Codes"
			self.ValidPIDs['04'] = "! Clear Diagnostic Trouble Codes and stored values"
			self.ValidPIDs['07'] = "! Show pending Diagnostic Trouble Codes (detected during current or last driving cycle)"

			# Get Mode 01 PID support [01 -> 20].
			self.PID0100()
			# If Mode 01 PID 20 is supported, get Mode 01 PID support [21 -> 40].
			if '0120' in self.ValidPIDs:
				self.PID0120()
			# If Mode 01 PID 40 is supported, get Mode 01 PID support [41 -> 60].
			if '0140' in self.ValidPIDs:
				self.PID0140()
			# If Mode 01 PID 60 is supported, get Mode 01 PID support [61 -> 80].
			if '0160' in self.ValidPIDs:
				self.PID0160()
			# If Mode 01 PID 80 is supported, get Mode 01 PID support [81 -> A0].
			if '0180' in self.ValidPIDs:
				self.PID0180()
			# If Mode 01 PID A0 is supported, get Mode 01 PID support [A1 -> C0].
			if '01A0' in self.ValidPIDs:
				self.PID01A0()
			# If Mode 01 PID C0 is supported, get Mode 01 PID support [C1 -> E0].
			if '01C0' in self.ValidPIDs:
				self.PID01C0()
			# Get Mode 05 PID support.
			self.PID050100()
			# Get Mode 09 PID support.
			self.PID0900()

		return self.Result



#/***************************************************************/
#/* Return a list of PIDs the currently connected ECU supports. */
#/***************************************************************/
	def GetValidPIDs(self):
		return self.ValidPIDs



#/**********************************************************************/
#/* Get and return the information for the specified PID from the ECU. */
#/**********************************************************************/
	def DoPID(self, PID):
		try:
			if PID in self.PidFunctions:
				self.Result = self.PidFunctions[PID](self)
			else:
				self.Result = self.STRING_NOT_IMPLEMENTED
		except Exception as Catch:
			print("***** ERROR ***** in PID" + str(PID) + " : " + str(Catch))
			self.Result = self.STRING_ERROR

		return self.Result



#/*************************************************/
#/* Talk to the ELM327 device over a serial port. */
#/* Send request data, and wait for the response. */
#/* The expected response ends with a prompt      */
#/* character '>', the ELM327 provides promting   */
#/* for more user requests.                       */
#/* Otherwise a timeout occurs waiting for a      */
#/* response.                                     */
#/*************************************************/
	def GetResponse(self, Data):
		self.ELM327.write(Data)
		self.Response = ""
		self.ReadChar = 1
		while self.ReadChar != b'>' and self.ReadChar != 0:
			self.ReadChar = self.ELM327.read()
			if self.ReadChar != b'>':
				self.Response += str(self.ReadChar, 'utf-8')
		return self.Response.replace('\r', '\n').replace('\n\n', '\n').replace('NO DATA', '00000000000000')



#/*****************************************************************/
#/* Resolve a bitmaped supported PIDs response from the ECU and   */
#/* add them to the list of currently supported PIDs for the ECU. */
#/*****************************************************************/
	def ResolvePidData(self, PidMode, PidData, PidStart, PidDescriptions):
		self.PidStartValue = int(PidStart, 16)
		self.PidValue = int(PidData, 16)
		self.Count = self.PidStartValue + (len(PidData) * 4)
		while self.PidValue > 0:
			if self.PidValue % 2 > 0:
				self.PidIndex = '%2.2X' % self.Count
				if self.PidIndex in PidDescriptions:
					self.ValidPIDs[PidMode + self.PidIndex] = PidDescriptions[self.PidIndex]
				else:
					self.ValidPIDs[PidMode + self.PidIndex] = STRING_NO_DESCRIPTION
			self.PidValue = int(self.PidValue / 2)
			self.Count -= 1



#/**********************************************************/
#/* Convert pairs of data bytes into actual trouble codes, */
#/* translating the first digit as required, and ignoring  */
#/* zero value data.                                       */
#/**********************************************************/
	def DataToTroubleCodes(self, Data):
		self.TroubleCodes = list()
		while len(Data) > 0:
			self.ThisCode = Data[:4]
			if int(self.ThisCode) != 0:
				self.TroubleCodes.append(self.TroubleCodePrefix[self.ThisCode[0]] + self.ThisCode[1:])
			Data = Data[4:]
		return self.TroubleCodes



#/*****************************************************/
#/* Get the trouble codes from the ECU and lookup the */
#/* trouble code descriptions. Return the data in a   */
#/* data array.                                       */
#/*****************************************************/
	def GetTroubleCodeData(self, OBDIImode):
		self.TroubleCodeData = {}
		self.Response = self.GetResponse(OBDIImode + b'\r')
		self.Response = self.PruneData(self.Response, 1)
		self.TroubleCodes = self.DataToTroubleCodes(self.Response)
		for self.TroubleCode in self.TroubleCodes:
			if self.TroubleCode in self.TroubleCodeDescriptions:
				self.TroubleCodeData[self.TroubleCode] = self.TroubleCodeDescriptions[self.TroubleCode]
			else:
				self.TroubleCodeData[self.TroubleCode] = STRING_NO_DESCRIPTION
		return self.TroubleCodeData



#/*******************************************************/
#/* The OBDII protocol will sometimes prefix a response */
#/* with confirmation of the request sent or other      */
#/* unwanted bytes of data. Use this function to remove */
#/* unwanted bytes from the start of lines, and         */
#/* concatenate the remainder of the response into a    */
#/* single line of data, ready for processing.          */
#/*******************************************************/
	def PruneData(self, Data, RemoveByteCount):
		self.Response = ""
		for Line in Data.split('\n'):
			self.Response += Line[2 * RemoveByteCount:]
		return self.Response


#/**************************************/
#/* ODBII MODE 01 - Show current data. */
#/**************************************/

# PID0100 Supported PIDs for Mode 1 [01 -> 20].
	def PID0100(self):
		self.Response = self.GetResponse(b'0100\r')
		self.Response = self.PruneData(self.Response, 2)
		self.ResolvePidData('01', self.Response, '00', self.PidDescriptionsMode01)
	PidFunctions["0100"] = PID0100


# PID0101 Get Monitor status since DTCs cleared from the ECU.
	def PID0101(self):
		self.Result = self.STRING_NO_DATA
		self.ResultArray = {}

		if '0101' in self.ValidPIDs:
			self.Response = self.GetResponse(b'0101\r')
			self.Response = self.PruneData(self.Response, 2)

			self.ResultVal1 = int(self.Response[:2], 16)
			if (self.ResultVal1 & 0x80) != 0:
				self.ResultArray["MIL"] = "ON"
			else:
				self.ResultArray["MIL"] = "OFF"
			self.ResultArray["TROUBLE CODE COUNT"] = int(self.ResultVal1 & 0x7F)

			self.ResultVal1 = int(self.Response[2:4], 16)
			if (self.ResultVal1 & 0x01) != 0:
				self.ResultArray["MISSFIRE"] = "TEST"
			if (self.ResultVal1 & 0x10) != 0:
				self.ResultArray["MISSFIRE"] += " [INCOMPLETE]"
			if (self.ResultVal1 & 0x02) != 0:
				self.ResultArray["FUEL SYSTEM"] = "TEST"
			if (self.ResultVal1 & 0x20) != 0:
				self.ResultArray["FUEL SYSTEM"] += " [INCOMPLETE]"
			if (self.ResultVal1 & 0x04) != 0:
				self.ResultArray["COMPONENTS"] = "TEST"
			if (self.ResultVal1 & 0x40) != 0:
				self.ResultArray["COMPONENTS"] += " [INCOMPLETE]"
			if (self.ResultVal1 & 0x08) != 0:
				self.ResultArray["IGNITION"] = "COMPRESSION"

				self.ResultVal1 = int(self.Response[4:6], 16)
				self.ResultVal2 = int(self.Response[6:8], 16)
				if (self.ResultVal1 & 0x01) != 0:
					self.ResultArray["NMHC CATALYST"] = "TEST"
				if (self.ResultVal2 & 0x01) != 0:
					self.ResultArray["NMHC CATALYST"] += " [INCOMPLETE]"
				if (self.ResultVal1 & 0x02) != 0:
					self.ResultArray["NOx/SCR MONITOR"] = "TEST"
				if (self.ResultVal2 & 0x02) != 0:
					self.ResultArray["NOx/SCR MONITOR"] += " [INCOMPLETE]"
				if (self.ResultVal1 & 0x04) != 0:
					self.ResultArray["Reserved 1"] = "TEST"
				if (self.ResultVal2 & 0x04) != 0:
					self.ResultArray["Reserved 1"] += " [INCOMPLETE]"
				if (self.ResultVal1 & 0x08) != 0:
					self.ResultArray["BOOST PRESSURE"] = "TEST"
				if (self.ResultVal2 & 0x08) != 0:
					self.ResultArray["BOOST PRESSURE"] += " [INCOMPLETE]"
				if (self.ResultVal1 & 0x10) != 0:
					self.ResultArray["Reserved 2"] = "TEST"
				if (self.ResultVal2 & 0x10) != 0:
					self.ResultArray["Reserved 2"] += " [INCOMPLETE]"
				if (self.ResultVal1 & 0x20) != 0:
					self.ResultArray["EXHAUST GAS SENSOR"] = "TEST"
				if (self.ResultVal2 & 0x20) != 0:
					self.ResultArray["EXHAUST GAS SENSOR"] += " [INCOMPLETE]"
				if (self.ResultVal1 & 0x40) != 0:
					self.ResultArray["PM FILTER MONITORING"] = "TEST"
				if (self.ResultVal2 & 0x40) != 0:
					self.ResultArray["PM FILTER MONITORING"] += " [INCOMPLETE]"
				if (self.ResultVal1 & 0x80) != 0:
					self.ResultArray["EGR/VVT SYSTEM"] = "TEST"
				if (self.ResultVal2 & 0x80) != 0:
					self.ResultArray["EGR/VVT SYSTEM"] += " [INCOMPLETE]"
			else:
				self.ResultArray["IGNITION"] = "SPARK"

				self.ResultVal1 = int(self.Response[4:6], 16)
				self.ResultVal2 = int(self.Response[6:8], 16)
				if (self.ResultVal1 & 0x01) != 0:
					self.ResultArray["CATALYST"] = "TEST"
				if (self.ResultVal2 & 0x01) != 0:
					self.ResultArray["CATALYST"] += " [INCOMPLETE]"
				if (self.ResultVal1 & 0x02) != 0:
					self.ResultArray["HEATED CATALYST"] = "TEST"
				if (self.ResultVal2 & 0x02) != 0:
					self.ResultArray["HEATED CATALYST"] += " [INCOMPLETE]"
				if (self.ResultVal1 & 0x04) != 0:
					self.ResultArray["EVAPORATIVE SYSTEM"] = "TEST"
				if (self.ResultVal2 & 0x04) != 0:
					self.ResultArray["EVAPORATIVE SYSTEM"] += " [INCOMPLETE]"
				if (self.ResultVal1 & 0x08) != 0:
					self.ResultArray["SECONDARY AIR SYSTEM"] = "TEST"
				if (self.ResultVal2 & 0x08) != 0:
					self.ResultArray["SECONDARY AIR SYSTEM"] += " [INCOMPLETE]"
				if (self.ResultVal1 & 0x10) != 0:
					self.ResultArray["A/C REFRIGERANT"] = "TEST"
				if (self.ResultVal2 & 0x10) != 0:
					self.ResultArray["A/C REFRIGERANT"] += " [INCOMPLETE]"
				if (self.ResultVal1 & 0x20) != 0:
					self.ResultArray["OXYGEN SENSOR"] = "TEST"
				if (self.ResultVal2 & 0x20) != 0:
					self.ResultArray["OXYGEN SENSOR"] += " [INCOMPLETE]"
				if (self.ResultVal1 & 0x40) != 0:
					self.ResultArray["OXYGEN SENSOR HEATER"] = "TEST"
				if (self.ResultVal2 & 0x40) != 0:
					self.ResultArray["OXYGEN SENSOR HEATER"] += " [INCOMPLETE]"
				if (self.ResultVal1 & 0x80) != 0:
					self.ResultArray["EGR SYSTEM"] = "TEST"
				if (self.ResultVal2 & 0x80) != 0:
					self.ResultArray["EGR SYSTEM"] += " [INCOMPLETE]"

			self.Result = self.ResultArray

		return self.Result
	PidFunctions["0101"] = PID0101


# PID0102 Freeze DTC.
	def PID0102(self):
		return self.GetResponse(b'0102\r')
	PidFunctions["0102"] = PID0102


# PID0103 Get the Fuel system status from the ECU.
	def PID0103(self):
		self.Result = self.STRING_NO_DATA
		self.ResultArray = {}

		if '0103' in self.ValidPIDs:
			self.Response = self.GetResponse(b'0103\r')
			self.Response = self.PruneData(self.Response, 2)
			if self.Response[:2] in self.FuelSystemStatus:
				self.ResultArray["Fuel System 1"] = self.FuelSystemStatus[self.Response[:2]]
			else:
				self.ResultArray["Fuel System 1"] = STRING_INVALID
			if self.Response[2:4] in self.FuelSystemStatus:
				self.ResultArray["Fuel System 2"] = self.FuelSystemStatus[self.Response[2:4]]
			else:
				self.ResultArray["Fuel System 2"] = STRING_INVALID

			self.Result = self.ResultArray

		return self.Result
	PidFunctions["0103"] = PID0103


# PID0104 Get the current Calculated Engine Load from the ECU.
	def PID0104(self):
		self.Result = self.STRING_NO_DATA

		if '0104' in self.ValidPIDs:
			self.Response = self.GetResponse(b'0104\r')
			self.Response = self.PruneData(self.Response, 2)
			self.Result = 100 * int(self.Response, 16) / 255

		return self.Result
	PidFunctions["0104"] = PID0104



# PID0105 Get the current Engine Coolant Temperature from the ECU.
	def PID0105(self):
		self.Result = self.STRING_NO_DATA

		if '0105' in self.ValidPIDs:
			self.Response = self.GetResponse(b'0105\r')
			self.Response = self.PruneData(self.Response, 2)
			self.Result = int(self.Response, 16) - 40

		return self.Result
	PidFunctions["0105"] = PID0105


# PID0106 Get the current Short Term Fuel Trim Bank1 from the ECU.
	def PID0106(self):
		self.Result = self.STRING_NO_DATA

		if '0106' in self.ValidPIDs:
			self.Response = self.GetResponse(b'0106\r')
			self.Response = self.PruneData(self.Response, 2)
			self.Result = (100 * int(self.Response, 16) / 128) - 100

		return self.Result
	PidFunctions["0106"] = PID0106


# PID0107 Get the Long term fuel trim—Bank from the ECU.
	def PID0107(self):
		self.Result = self.STRING_NO_DATA

		if '0107' in self.ValidPIDs:
			self.Response = self.GetResponse(b'0107\r')
			self.Response = self.PruneData(self.Response, 2)
			self.Result = (100 * int(self.Response, 16) / 128) - 100

		return self.Result
	PidFunctions["0107"] = PID0107


# PID0108 Get the Short term fuel trim—Bank 2 from the ECU.
	def PID0108(self):
		self.Result = self.STRING_NO_DATA

		if '0108' in self.ValidPIDs:
			self.Response = self.GetResponse(b'0108\r')
			self.Response = self.PruneData(self.Response, 2)
			self.Result = (100 * int(self.Response, 16) / 128) - 100

		return self.Result
	PidFunctions["0108"] = PID0108


# PID0109 Get the Long term fuel trim—Bank 2 from the ECU.
	def PID0109(self):
		self.Result = self.STRING_NO_DATA

		if '0109' in self.ValidPIDs:
			self.Response = self.GetResponse(b'0109\r')
			self.Response = self.PruneData(self.Response, 2)
			self.Result = (100 * int(self.Response, 16) / 128) - 100

		return self.Result
	PidFunctions["0109"] = PID0109


# PID010A Get the Fuel pressure (gauge pressure) from the ECU.
	def PID010A(self):
		self.Result = self.STRING_NO_DATA

		if '010A' in self.ValidPIDs:
			self.Response = self.GetResponse(b'010A\r')
			self.Response = self.PruneData(self.Response, 2)
			self.Result = 3 * int(self.Response, 16)

		return self.Result
	PidFunctions["010A"] = PID010A


# PID010B Get the Intake manifold absolute pressure from the ECU.
	def PID010B(self):
		self.Result = self.STRING_NO_DATA

		if '010B' in self.ValidPIDs:
			self.Response = self.GetResponse(b'010B\r')
			self.Response = self.PruneData(self.Response, 2)
			self.Result = int(self.Response, 16)

		return self.Result
	PidFunctions["010B"] = PID010B


# PID010C Get the current Engine RPM from the ECU.
	def PID010C(self):
		self.Result = self.STRING_NO_DATA

		if '010C' in self.ValidPIDs:
			self.Response = self.GetResponse(b'010C\r')
			self.Response = self.PruneData(self.Response, 2)
			self.Result = (256 * int(self.Response[:2], 16) + int(self.Response[2:4], 16)) / 4

		return self.Result
	PidFunctions["010C"] = PID010C


# PID010D Get the Vehicle speed from the ECU.
	def PID010D(self):
		self.Result = self.STRING_NO_DATA

		if '010D' in self.ValidPIDs:
			self.Response = self.GetResponse(b'010D\r')
			self.Response = self.PruneData(self.Response, 2)
			self.Result = int(self.Response[:2], 16)

		return self.Result
	PidFunctions["010D"] = PID010D


# PID010E Get the Timing advance from the ECU.
	def PID010E(self):
		self.Result = self.STRING_NO_DATA

		if '010E' in self.ValidPIDs:
			self.Response = self.GetResponse(b'010E\r')
			self.Response = self.PruneData(self.Response, 2)
			self.Result = (int(self.Response[:2], 16) / 2) - 64

		return self.Result
	PidFunctions["010E"] = PID010E


# PID010F Get the Intake air temperature from the ECU.
	def PID010F(self):
		self.Result = self.STRING_NO_DATA

		if '010F' in self.ValidPIDs:
			self.Response = self.GetResponse(b'010F\r')
			self.Response = self.PruneData(self.Response, 2)
			self.Result = int(self.Response[:2], 16) - 40

		return self.Result
	PidFunctions["010F"] = PID010F


# PID0110 Get the MAF air flow rate from the ECU.
	def PID0110(self):
		self.Result = self.STRING_NO_DATA

		if '0110' in self.ValidPIDs:
			self.Response = self.GetResponse(b'0110\r')
			self.Response = self.PruneData(self.Response, 2)
			self.Result = (256 * int(self.Response[:2], 16) + int(self.Response[2:4], 16)) / 100

		return self.Result
	PidFunctions["0110"] = PID0110


# PID0111 Get the Throttle position from the ECU.
	def PID0111(self):
		self.Result = self.STRING_NO_DATA

		if '0111' in self.ValidPIDs:
			self.Response = self.GetResponse(b'0111\r')
			self.Response = self.PruneData(self.Response, 2)
			self.Result = 100 * int(self.Response[:2], 16) / 255

		return self.Result
	PidFunctions["0111"] = PID0111


# PID0112 Get the Commanded secondary air status from the ECU.
	def PID0112(self):
		self.Result = self.STRING_NO_DATA

		if '0112' in self.ValidPIDs:
			self.Response = self.GetResponse(b'0112\r')
			self.Response = self.PruneData(self.Response, 2)
			if self.Response in self.CommandedSecondaryAirStatus:
				self.Result = self.CommandedSecondaryAirStatus[self.Response]
			else:
				self.Result = STRING_INVALID

		return self.Result
	PidFunctions["0112"] = PID0112


# PID0113 Get the Oxygen sensors present (in 2 banks) from the ECU.
	def PID0113(self):
		self.Result = self.STRING_NO_DATA
		self.ResultArray = {}

		if '0113' in self.ValidPIDs:
			self.Response = self.GetResponse(b'0113\r')
			self.Response = self.PruneData(self.Response, 2)
			self.ResultVal = int(self.Response[:2], 16)
			self.ResultArray["BANK1"] = (self.ResultVal & 0x0F)
			self.ResultArray["BANK2"] = (self.ResultVal & 0xF0) >> 4

			self.Result = self.ResultArray

		return self.Result
	PidFunctions["0113"] = PID0113


# PID0114 Get the current Oxygen Sensor 1 Voltage & Short Term Fuel Trim from the ECU.
	def PID0114(self):
		self.Result = self.STRING_NO_DATA

		if '0114' in self.ValidPIDs:
			self.Response = self.GetResponse(b'0114\r')
			self.Response = self.PruneData(self.Response, 2)
			self.Result = { int(self.Response[:2], 16) / 200, (100 * int(self.Response[2:4], 16) / 128) - 100 }

		return self.Result
	PidFunctions["0114"] = PID0114


# PID0115 Get the current Oxygen Sensor 2 Voltage & Short Term Fuel Trim from the ECU.
	def PID0115(self):
		self.Result = self.STRING_NO_DATA

		if '0115' in self.ValidPIDs:
			self.Response = self.GetResponse(b'0115\r')
			self.Response = self.PruneData(self.Response, 2)
			self.Result = { int(self.Response[:2], 16) / 200, (100 * int(self.Response[2:4], 16) / 128) - 100 }

		return self.Result
	PidFunctions["0115"] = PID0115


# PID0116 Get the current Oxygen Sensor 3 Voltage & Short Term Fuel Trim from the ECU.
	def PID0116(self):
		self.Result = self.STRING_NO_DATA

		if '0116' in self.ValidPIDs:
			self.Response = self.GetResponse(b'0116\r')
			self.Response = self.PruneData(self.Response, 2)
			self.Result = { int(self.Response[:2], 16) / 200, (100 * int(self.Response[2:4], 16) / 128) - 100 }

		return self.Result
	PidFunctions["0116"] = PID0116


# PID0117 Get the current Oxygen Sensor 4 Voltage & Short Term Fuel Trim from the ECU.
	def PID0117(self):
		self.Result = self.STRING_NO_DATA

		if '0117' in self.ValidPIDs:
			self.Response = self.GetResponse(b'0117\r')
			self.Response = self.PruneData(self.Response, 2)
			self.Result = { int(self.Response[:2], 16) / 200, (100 * int(self.Response[2:4], 16) / 128) - 100 }

		return self.Result
	PidFunctions["0117"] = PID0117


# PID0118 Get the current Oxygen Sensor 5 Voltage & Short Term Fuel Trim from the ECU.
	def PID0118(self):
		self.Result = self.STRING_NO_DATA

		if '0118' in self.ValidPIDs:
			self.Response = self.GetResponse(b'0118\r')
			self.Response = self.PruneData(self.Response, 2)
			self.Result = { int(self.Response[:2], 16) / 200, (100 * int(self.Response[2:4], 16) / 128) - 100 }

		return self.Result
	PidFunctions["0118"] = PID0118


# PID0119 Get the current Oxygen Sensor 6 Voltage & Short Term Fuel Trim from the ECU.
	def PID0119(self):
		self.Result = self.STRING_NO_DATA

		if '0119' in self.ValidPIDs:
			self.Response = self.GetResponse(b'0119\r')
			self.Response = self.PruneData(self.Response, 2)
			self.Result = { int(self.Response[:2], 16) / 200, (100 * int(self.Response[2:4], 16) / 128) - 100 }

		return self.Result
	PidFunctions["0119"] = PID0119


# PID011A Get the current Oxygen Sensor 7 Voltage & Short Term Fuel Trim from the ECU.
	def PID011A(self):
		self.Result = self.STRING_NO_DATA

		if '011A' in self.ValidPIDs:
			self.Response = self.GetResponse(b'011A\r')
			self.Response = self.PruneData(self.Response, 2)
			self.Result = { int(self.Response[:2], 16) / 200, (100 * int(self.Response[2:4], 16) / 128) - 100 }

		return self.Result
	PidFunctions["011A"] = PID011A


# PID011B Get the current Oxygen Sensor 8 Voltage & Short Term Fuel Trim from the ECU.
	def PID011B(self):
		self.Result = self.STRING_NO_DATA

		if '011B' in self.ValidPIDs:
			self.Response = self.GetResponse(b'011B\r')
			self.Response = self.PruneData(self.Response, 2)
			self.Result = { int(self.Response[:2], 16) / 200, (100 * int(self.Response[2:4], 16) / 128) - 100 }

		return self.Result
	PidFunctions["011B"] = PID011B


# PID011C Get the OBD standards this vehicle conforms to from the ECU.
	def PID011C(self):
		self.Result = self.STRING_NO_DATA

		if '011C' in self.ValidPIDs:
			self.Response = self.GetResponse(b'011C\r')
			self.Response = self.PruneData(self.Response, 2)
			if self.Response in self.VehicleObdStandards:
				self.Result = self.VehicleObdStandards[self.Response]
			else:
				self.Result = STRING_INVALID

		return self.Result
	PidFunctions["011C"] = PID011C


# PID011D
# PID011E
# PID011F


# PID0120 Supported PIDs for Mode 1 [21 -> 40].
	def PID0120(self):
		self.Response = self.GetResponse(b'0120\r')
		self.Response = self.PruneData(self.Response, 2)
		self.ResolvePidData('01', self.Response, '20', self.PidDescriptionsMode01)
	PidFunctions["0120"] = PID0120


# PID0121 Get the Distance traveled with malfunction indicator lamp (MIL) on from the ECU.
	def PID0121(self):
		self.Result = self.STRING_NO_DATA

		if '0121' in self.ValidPIDs:
			self.Response = self.GetResponse(b'0121\r')
			self.Response = self.PruneData(self.Response, 2)
			self.Result = 256 * int(self.Response[:2], 16) + int(self.Response[2:4], 16)

		return self.Result
	PidFunctions["0121"] = PID0121


# PID0122
# PID0123
# PID0124
# PID0125
# PID0126
# PID0127
# PID0128
# PID0129
# PID012A
# PID012B
# PID012C
# PID012D
# PID012E
# PID012F
# PID0130
# PID0131
# PID0132
# PID0133
# PID0134
# PID0135
# PID0136
# PID0137
# PID0138
# PID0139
# PID013A
# PID013B
# PID013C
# PID013D
# PID013E
# PID013F


# PID0140 Supported PIDs for Mode 1 [41 -> 60].
	def PID0140(self):
		self.Response = self.GetResponse(b'0140\r')
		self.Response = self.PruneData(self.Response, 2)
		self.ResolvePidData('01', self.Response, '40', self.PidDescriptionsMode01)
	PidFunctions["0140"] = PID0140


# PID0141
# PID0142
# PID0143
# PID0144
# PID0145
# PID0146
# PID0147
# PID0148
# PID0149
# PID014A
# PID014B
# PID014C
# PID014D
# PID014E
# PID014F
# PID0150
# PID0151
# PID0152
# PID0153
# PID0154
# PID0155
# PID0156
# PID0157
# PID0158
# PID0159
# PID015A
# PID015B
# PID015C
# PID015D
# PID015E
# PID015F


# PID0160 Supported PIDs for Mode 1 [61 -> 80].
	def PID0160(self):
		self.Response = self.GetResponse(b'0160\r')
		self.Response = self.PruneData(self.Response, 2)
		self.ResolvePidData('01', self.Response, '60', self.PidDescriptionsMode01)
	PidFunctions["0160"] = PID0160


# PID0161
# PID0162
# PID0163
# PID0164
# PID0165
# PID0166
# PID0167
# PID0168
# PID0169
# PID016A
# PID016B
# PID016C
# PID016D
# PID016E
# PID016F
# PID0170
# PID0171
# PID0172
# PID0173
# PID0174
# PID0175
# PID0176
# PID0177
# PID0178
# PID0179
# PID017A
# PID017B
# PID017C
# PID017D
# PID017E
# PID017F


# PID0180 Supported PIDs for Mode 1 [81 -> A0].
	def PID0180(self):
		self.Response = self.GetResponse(b'0180\r')
		self.Response = self.PruneData(self.Response, 2)
		self.ResolvePidData('01', self.Response, '80', self.PidDescriptionsMode01)
	PidFunctions["0180"] = PID0180


# PID0181
# PID0182
# PID0183
# PID0184
# PID0185
# PID0186
# PID0187
# PID0188
# PID0189
# PID018A
# PID018B
# PID018C
# PID018D
# PID018E
# PID018F
# PID0190
# PID0191
# PID0192
# PID0193
# PID0194
# PID0195
# PID0196
# PID0197
# PID0198
# PID0199
# PID019A
# PID019B
# PID019C
# PID019D
# PID019E
# PID019F


# PID01A0 Supported PIDs for Mode 1 [A1 -> C0].
	def PID01A0(self):
		self.Response = self.GetResponse(b'01A0\r')
		self.Response = self.PruneData(self.Response, 2)
		self.ResolvePidData('01', self.Response, 'A0', self.PidDescriptionsMode01)
	PidFunctions["01A0"] = PID01A0


# PID01A1
# PID01A2
# PID01A3
# PID01A4
# PID01A5
# PID01A6
# PID01A7
# PID01A8
# PID01A9
# PID01AA
# PID01AB
# PID01AC
# PID01AD
# PID01AE
# PID01AF
# PID01B0
# PID01B1
# PID01B2
# PID01B3
# PID01B4
# PID01B5
# PID01B6
# PID01B7
# PID01B8
# PID01B9
# PID01BA
# PID01BB
# PID01BC
# PID01BD
# PID01BE
# PID01BF


# PID01C0 Supported PIDs for Mode 1 [C1 -> E0].
	def PID01C0(self):
		self.Response = self.GetResponse(b'01C0\r')
		self.Response = self.PruneData(self.Response, 2)
		self.ResolvePidData('01', self.Response, 'C0', self.PidDescriptionsMode01)
	PidFunctions["01C0"] = PID01C0


# PID01C1
# PID01C2
# PID01C3
# PID01C4
# PID01C5
# PID01C6
# PID01C7
# PID01C8
# PID01C9
# PID01CA
# PID01CB
# PID01CC
# PID01CD
# PID01CE
# PID01CF
# PID01D0
# PID01D1
# PID01D2
# PID01D3
# PID01D4
# PID01D5
# PID01D6
# PID01D7
# PID01D8
# PID01D9
# PID01DA
# PID01DB
# PID01DC
# PID01DD
# PID01DE
# PID01DF


#/*******************************************/
#/* ODBII MODE 02 - Show freeze frame data. */
#/*******************************************/


#/*********************************************************/
#/* ODBII MODE 03 - Show stored diagnostic trouble codes. */
#/*********************************************************/

# PID03 Get the Stored Trouble Codes from the ECU.
	def PID03(self):
		return self.GetTroubleCodeData(b'03')
	PidFunctions["03"] = PID03


#/*********************************************************************/
#/* ODBII MODE 04 - Clear diagnostic trouble codes and stored values. */
#/*********************************************************************/

# PID04 Erase all Pending/Stored Trouble Codes and Data from the ECU.
	def PID04(self):
		return self.GetResponse(b'04\r')
	PidFunctions["04"] = PID04


#/**************************************************************************/
#/* ODBII MODE 05 - Test results, oxygen sensor monitoring (non CAN only). */
#/**************************************************************************/

# PID050100 Supported PIDs for Mode 0501 [01 -> 20].
	def PID050100(self):
		self.Response = self.GetResponse(b'050100\r')
		self.Response = self.PruneData(self.Response, 3)
		self.ResolvePidData('05', self.Response, '00', self.PidDescriptionsMode05)
	PidFunctions["050100"] = PID050100


# PID050101
# PID050102
# PID050103
# PID050104
# PID050105
# PID050106
# PID050107
# PID050108
# PID050109
# PID05010A
# PID05010B
# PID05010C
# PID05010D
# PID05010E
# PID05010F
# PID050110
# PID050121
# PID050122
# PID050123
# PID050124
# PID050125
# PID050126
# PID050127
# PID050128
# PID050129
# PID05012A
# PID05012B
# PID05012C
# PID05012D
# PID05012E
# PID05012F


#/***********************************************************************/
#/* ODBII MODE 06 - Test results, other component/system monitoring.    */
#/*               (Test results, oxygen sensor monitoring for CAN only) */
#/***********************************************************************/


#/*******************************************************************/
#/* ODBII MODE 07 - Show pending diagnostic trouble codes.          */
#/*                 (detected during current or last driving cycle) */
#/*******************************************************************/

# Get the Pending Trouble Codes from the ECU.
	def PID07(self):
		return self.GetTroubleCodeData(b'07')
	PidFunctions["07"] = PID07


#/*******************************************************************/
#/* ODBII MODE 08 - Control operation of on-board component/system. */
#/*******************************************************************/


#/************************************************/
#/* ODBII MODE 09 - Request vehicle information. */
#/************************************************/

# PID0900 Supported PIDs for Mode 09 [01 -> 20].
	def PID0900(self):
		self.Response = self.GetResponse(b'0900\r')
		self.Response = self.PruneData(self.Response, 3)
		self.ResolvePidData('09', self.Response, '00', self.PidDescriptionsMode09)
	PidFunctions["0900"] = PID0900


	def PID0901(self):
		return self.STRING_TODO
	PidFunctions["0901"] = PID0901


# PID0901 Get the VIN Message Count in PID 02.
	def PID0901(self):
		self.Result = self.STRING_NO_DATA

		if '0901' in self.ValidPIDs:
			self.Response = self.GetResponse(b'0901\r')
			self.Response = self.PruneData(self.Response, 2)
			self.Result = int(self.Response, 16)

		return self.Result
	PidFunctions["0901"] = PID0901


# PID0902 Get the current Vehicle VIN Number from the ECU.
	def PID0902(self):
		self.Result = self.STRING_NO_DATA

		if '0902' in self.ValidPIDs:
			self.Response = self.GetResponse(b'0902\r')
			self.Response = self.PruneData(self.Response, 3)
			self.Result = str(bytearray.fromhex(self.Response).replace(bytes([0x00]), b' '), 'UTF-8')

		return self.Result
	PidFunctions["0902"] = PID0902


	def PID0903(self):
		return self.STRING_TODO
	PidFunctions["0903"] = PID0903


# PID0903 Get the Calibration ID message count for PID 04.
	def PID0903(self):
		self.Result = self.STRING_NO_DATA

		if '0903' in self.ValidPIDs:
			self.Response = self.GetResponse(b'0903\r')
			self.Response = self.PruneData(self.Response, 2)
			self.Result = int(self.Response, 16)

		return self.Result
	PidFunctions["0903"] = PID0903


# PID0904 Get the current Calibration ID from the ECU.
	def PID0904(self):
		self.Result = self.STRING_NO_DATA

		if '0904' in self.ValidPIDs:
			self.Response = self.GetResponse(b'0904\r')
			self.Response = self.PruneData(self.Response, 3)
			self.Result = str(bytearray.fromhex(self.Response).replace(bytes([0x00]), b' '), 'UTF-8')

		return self.Result
	PidFunctions["0904"] = PID0904


	def PID0905(self):
		return self.STRING_TODO
	PidFunctions["0905"] = PID0905


# PID0905 Get Calibration verification numbers (CVN) message count for PID 06.
	def PID0905(self):
		self.Result = self.STRING_NO_DATA

		if '0905' in self.ValidPIDs:
			self.Response = self.GetResponse(b'0905\r')
			self.Response = self.PruneData(self.Response, 2)
			self.Result = int(self.Response, 16)

		return self.Result
	PidFunctions["0905"] = PID0905


# PID0906 Get the current Calibration Verification Numbers from the ECU.
	def PID0906(self):
		self.Result = self.STRING_NO_DATA

		if '0906' in self.ValidPIDs:
			self.Response = self.GetResponse(b'0906\r')
			self.Result = self.PruneData(self.Response, 3)

		return self.Result
	PidFunctions["0906"] = PID0906


	def PID0907(self):
		return self.STRING_TODO
	PidFunctions["0907"] = PID0907


	def PID0908(self):
		return self.STRING_TODO
	PidFunctions["0908"] = PID0908


	def PID0909(self):
		return self.STRING_TODO
	PidFunctions["0909"] = PID0909


# PID0907 Get In-use performance tracking message count for PID 08 and 0B.
	def PID0907(self):
		self.Result = self.STRING_NO_DATA

		if '0907' in self.ValidPIDs:
			self.Response = self.GetResponse(b'0907\r')
			self.Response = self.PruneData(self.Response, 2)
			self.Result = int(self.Response, 16)

		return self.Result
	PidFunctions["0907"] = PID0907


# PID0908


# PID0909 Get ECU name message count for PID 0A.
	def PID0909(self):
		self.Result = self.STRING_NO_DATA

		if '0909' in self.ValidPIDs:
			self.Response = self.GetResponse(b'0909\r')
			self.Response = self.PruneData(self.Response, 2)
			self.Result = int(self.Response, 16)

		return self.Result
	PidFunctions["0909"] = PID0909


# PID090A Get the current ECU Name from the ECU.
	def PID090A(self):
		self.Result = self.STRING_NO_DATA

		if '090A' in self.ValidPIDs:
			self.Response = self.GetResponse(b'090A\r')
			self.Response = self.PruneData(self.Response, 3)
			self.Result = str(bytearray.fromhex(self.Response).replace(bytes([0x00]), b' '), 'UTF-8')

		return self.Result
	PidFunctions["090A"] = PID090A


# PID090B


#/****************************************************************************/
#/* ODBII MODE 0A - Permanent diagnostic trouble codes (DTCs, Cleared DTCs). */
#/****************************************************************************/
