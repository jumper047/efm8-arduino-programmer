#! python
import serial, sys, struct, time, os.path





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


	def dump(self, firmware, size = 0x3fff, chunksize = 0x10):
		print ("Connected")
		self.conf()
		for i in range(size)[::chunksize]:
			print("===============================================")
			print("addr: %s" % hex(i))
			request = [0x5, 0x5, chunksize, (i >> 16) & 0xFF, (i >> 8) & 0xFF, i & 0xFF, 0]
			self.ser.write(request)
			print("request: " + bytes(request).hex())
			x = self.ser.read(chunksize + 1)
			print("response code: " + hex(x[0]))
			response = x[1:]
			print("response body: " + response.hex())
			newline = bytearray([chunksize, (i >> 8) & 0xFF, i & 0xFF, 0]) + response
			crc = 0
			for nextbyte in newline:
				crc = crc + nextbyte
			crc = (~crc + 1) & 0xFF
			newline.append(crc)
			firmware.write(":" + newline.hex() + "\n")
		firmware.write(":00000001FF\n")
			
			
			
			

	

if __name__ == "__main__":
        if len(sys.argv) != 3:
	        print ("usage: %s <port> <firmware.hex>" % sys.argv[0])
        	sys.exit(1)

        # if os.path.exists(sys.argv[2]):
        # 	print ("file %s exists, sorry, I won't overwrite" % sys.argv[2])
        # 	sys.exit(1)
        print ("Once")
        port=sys.argv[1]
        with open(sys.argv[2], 'x') as firmware:
                programmers = PI(port)
                programmers.dump(firmware)
