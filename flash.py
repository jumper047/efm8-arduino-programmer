#! python
import serial, sys, struct, time


class PI():
	def __init__(self, com):
		self.ser = serial.Serial(com, 1000000, timeout = 1)
		time.sleep(2)

	def conf(self,):

		# init Programming Interface (PI)
		while True:
			try:
				self.ser.write(b'\x01\x00')
				x=self.ser.read(1)
				assert x == b'\x81'
				break
			except:
				print ("error com")			
				while self.ser.read(1) != '': pass

		print ("PI initiated")


	def prog(self, firmware):

		print ("Connected")

		#f = open(firmware,'r').readlines()
		f = firmware.splitlines()

		self.conf()

		# erase device
		self.ser.write(b'\x04\x00')
		assert self.ser.read(1)==b'\x84'
		
		print ("Device erased")
		
		# write hex file
		for i in f:  # skip first and second lines
			assert(i[0] == ':')			
			size = int(i[1:3],16)
			assert(size + 4 < 256)	   
			addrh = int(i[3:5],16)
			addrl = int(i[5:7],16)
			if i[7:9] != '00':
				continue
			data = bytearray.fromhex(i[9:9 + size*2])
			assert(len(data) == size)	 
			crc = addrh + addrl
			for j in range(len(data)):
				crc += data[j]
			crc = crc & 0xFF
			#print('Addr: 0x04%X, Len: 0x02%X, Data: %s' % (addrl + (addrh << 8), len(data), data.hex()))
			print('Addr: {:04X}, Len: {:02X}, Data: {}'.format((addrl + (addrh << 8)), len(data), data.hex()))
			self.ser.write([0x3, len(data) + 5, len(data), 0, addrh, addrl, crc])
			self.ser.write(data)
			response = self.ser.read(1)
			if response != b'\x83':
				print('fuck')
                                return None
		
			

		# reset device
		self.ser.write(b'\x02\x00')
		assert self.ser.read(1)==b'\x82' 

		# reset device
		self.ser.write(b'\x02\x00')
		assert self.ser.read(1)==b'\x82' 

		# reset device
		self.ser.write(b'\x02\x00')
		assert self.ser.read(1)==b'\x82' 
		print ("Device reset")

if __name__ == "__main__":

        if len(sys.argv) != 3:
                print ("usage: %s <port> <firmware.hex>" % sys.argv[0])
                sys.exit(1)
        print ("Once")
        port=sys.argv[1]
        firmware=open(sys.argv[2], 'r').read()
        programmers = PI(port)
        programmers.prog(firmware)
