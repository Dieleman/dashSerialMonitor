import serial
import time
import multiprocessing

import datetime

class SerialProcess(multiprocessing.Process):

    def __init__(self, taskQ, resultQ, logToFile=True):
        # super(SerialProcess, self).__init__(target=self.loop_iterator,args=(serial_port, baudrate, timeout))

        # As soon as you uncomment this, you'll get an error.
        # self.ser = serial.Serial(serial_port, baudrate=baudrate, timeout=timeout)
        multiprocessing.Process.__init__(self)
        self.serial_port = "COM1"
        self.baudrate = 115200
        self.timeout = 1

        self.taskQ = taskQ
        self.resultQ = resultQ
        self.usbPort = 'COM1'
        print("init funished")

    def close(self):
        self.sp.close()

    def sendData(self, data):
        print("sendData start...")
        # self.sp.write(data)
        time.sleep(3)
        print("sendData done: " + data)

    def run(self):
        print("Run")
        #ser = serial.Serial(self.serial_port, baudrate=self.baudrate, timeout=self.timeout)
        #print(ser)
        # self.sp.flushInput()
        i = 0
        f = open('log.txt','w')
        f.write("Datetime,Power (W),PW (ns)\n")
        while True:

            # look for incoming tornado request
            if not self.taskQ.empty():
                task = self.taskQ.get()

                # send it to the arduino
               # self.sp.write(task + "\n");
                print("arduino received from tornado: " + task)

            # look for incoming serial data
            # if (self.sp.inWaiting() > 0):
            #     result = self.sp.readline().replace("\n", "")
            #
            #     # send it back to tornado
            time.sleep(.1)
            i += 1
            self.resultQ.put(str(i))
            ts = time.time()
            f.write("%s, %.4f, %.4f\n" % (datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'),i,i*10))
            f.flush()
            if(i >= 10):
                 ser = serial.Serial(self.serial_port, baudrate=self.baudrate, timeout=self.timeout)