from rtlsdr import RtlSdr
import math
import curses
from curses import wrapper
import threading, time, signal
import requests
from datetime import timedelta
import psutil
from gpiozero import CPUTemperature
#from audio_tones import AudioTones
from firebase import firebase
firebase = firebase.FirebaseApplication('https://notjamming-1-default-rtdb.firebaseio.com', None)

NUM_SAMPLES = 32768

#serial_numbers = RtlSdr.get_device_serial_addresses()
#device_index0 = RtlSdr.get_device_index_by_serial('00000433')
a = RtlSdr.get_device_name(0)
print(a)
#sdrX0 = RtlSdr(device_index0)
#print('sdrX0:')
#print(sdrX0)

alarma_anterior='notpresente'
WAIT_TIME_SECONDS = 300
rssi=0
rssi1=0
rssi2=0
class ProgramKilled(Exception):
    pass

def foo():
    print(time.ctime())

    cpu = str(psutil.cpu_percent())
    memory = psutil.virtual_memory()
    mem_info = str(memory.percent)
    disk = psutil.disk_usage('/')
    disk_info = str(disk.percent)
    cput = CPUTemperature()
    print("temperatura-> ", cput.temperature)

    print("CPU Info-> ", cpu)
    print("Memory Info->", mem_info)
    print("Disk Info->", disk_info)
    result = firebase.post('ping', {'device':'0001A', 'cpu':cpu, 'memory':mem_info,'disk':disk_info, 'temperature':cpu
t.temperature})

def signal_handler(signum, frame):
    raise ProgramKilled

class Job(threading.Thread):
    def __init__(self, interval, execute, *args, **kwargs):
        threading.Thread.__init__(self)
        self.daemon = False
        self.stopped = threading.Event()
        self.interval = interval
        self.execute = execute
        self.args = args
        self.kwargs = kwargs

    def stop(self):
        self.stopped.set()
        self.join()
    def run(self):
        while not self.stopped.wait(self.interval.total_seconds()):
            self.execute(*self.args, **self.kwargs)

def main():
#def main(stdscr):
#   foo()
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    job = Job(interval=timedelta(seconds=WAIT_TIME_SECONDS), execute=foo)
    job.start()

    print("inicio")
    try: 
        sdr = RtlSdr(0)
        sdr.sample_rate = 1.024e6
        sdr.center_freq = 315.0e6
        sdr.freq_correction = 20
        sdr.gain = 'auto'
    except:
        sdr=0
        print('no hay sdr') 
    try:
        sdr1 = RtlSdr(1)
        sdr1.sample_rate = 1.024e6
        sdr1.center_freq = 868.0e6
        sdr1.freq_correction = 20
        sdr1.gain = 'auto'
        print('sdr1')
    except:
        sdr1 = 0
        print('no hay sdr1')
    try:
        sdr2 = RtlSdr(2)
        sdr2.sample_rate = 1.024e6
        sdr2.center_freq = 915.0e6
        sdr2.freq_correction = 20
        sdr2.gain = 'auto'
        print('sdr2')
    except: 
        sdr2 = 0
        print('no hay sdr2')
    
    print("despues de sdr2")
#configure device
#sdr.sample_rate = 1.024e6# Hz
#sdr.center_freq = 433.9e6# Hz
#sdr.freq_correction = 20# PPM
#sdr.gain = 'auto'


    for i in range(0, 10):
        if not (not sdr):
            rssi = MeasureRSSI(sdr)
        if not not sdr1:
            rssi1 = MeasureRSSI(sdr1)
        if not not sdr2:
            rssi2 = MeasureRSSI(sdr2)

# Measure minimum RSSI over a few readings, auto-adjust for dongle gain
    min_rssi = 1000
    min_rssi1 = 1000
    min_rssi2 = 1000
    for i in range(0, 10):
        if(not not sdr):
            rssi = MeasureRSSI(sdr)
            min_rssi = min(min_rssi, rssi)
            ampl_offset = min_rssi
            max_rssi = MeasureRSSI(sdr) - ampl_offset
            avg_rssi = max_rssi + 20
            counter = 0
            previo = 0
        if(not not sdr1):
            rssi1 = MeasureRSSI(sdr1)
            min_rssi1 = min(min_rssi1, rssi1)
            ampl_offset1 = min_rssi1
            max_rssi1 = MeasureRSSI(sdr1) - ampl_offset1
            avg_rssi1 = max_rssi1 + 20
            counter1 = 0
            previo1 = 0
        if(not not sdr2): 
            rssi2 = MeasureRSSI(sdr2)
            min_rssi2 = min(min_rssi2, rssi2)
            ampl_offset2 = min_rssi2
            max_rssi2 = MeasureRSSI(sdr2) - ampl_offset2
            avg_rssi2 = max_rssi2 + 20
            counter2 = 0
            previo = 0
    alarma_anterior='inicial'
    alarma_anterior1='inicial'
    alarma_anterior2='inicial'
    ii=0
    iii=0
    ii1=0
    iii1=0
    ii2=0
    iii2=0
    while(True):
        if not not sdr:
            rssi = MeasureRSSI(sdr) - ampl_offset
            avg_rssi = ((15 * avg_rssi) + rssi) / 16
            max_rssi = max(max_rssi, rssi)

            counter += 1
            if counter & 0x1F == 0:
                max_rssi = rssi
                if(max_rssi)>5:
                    if(alarma_anterior=='jammer'):
                        alarma_anterior = 'jammer'
                    else:
                        r = requests.post('https://us-central1-notjamming-1.cloudfunctions.net/simuladorjammer2', json
={
                          "device": "0001A",
                          "rssi": max_rssi,
                          "secuencia":ii,
                          "secuencia2":iii,
                          "frecuencia":"315",
                          "jammer315": "jammer"
                        })
                        ii=ii+1
                        print(max_rssi)
                        alarma_anterior = 'jammer'
            else:
                if(alarma_anterior=='notpresente'):
                    alarma_anterior = 'notpresente'
                else:
                    r = requests.post('https://us-central1-notjamming-1.cloudfunctions.net/simuladorjammerOff2', json=
{
                        "device": "0001A",
                        "rssi": 0,
                        "jammer315": "notpresente",
                        "frecuencia": "315",
                        "secuencia": ii,
                        "secuencia2": iii
                    })
                    iii=iii+1

                    alarma_anterior = 'notpresente'

        if not not sdr1: 
            rssi1 = MeasureRSSI(sdr1) - ampl_offset1
            avg_rssi1 = ((15 * avg_rssi1) + rssi1) / 16
            max_rssi1 = max(max_rssi1, rssi1)

            counter1 += 1
            if counter1 & 0x1F == 0:
                max_rssi1 = rssi1
                if(max_rssi1)>5:
                    if(alarma_anterior1=='jammer'):
                        alarma_anterior1 = 'jammer'
                    else:
                        r = requests.post('https://us-central1-notjamming-1.cloudfunctions.net/simuladorjammer2', json
={
                            "device": "0001A",
                            "rssi": max_rssi,
                            "secuenciay":ii,
                            "secuencia2y":iii,
                            "frecuencia":"868",
                        })
                        ii=ii+1

                        alarma_anterior = 'jammer'
                else:
                    if(alarma_anterior=='notpresente'):
                        alarma_anterior = 'notpresente'
                    else:

                        r = requests.post('https://us-central1-notjamming-1.cloudfunctions.net/simuladorjammerOff2', j
son={
                           "device": "0001A",
                           "rssi": 0,
                           "jammer868": "notpresente",
                           "frecuencia": "868",
                           "secuenciay": ii1,
                           "secuencia2y": iii1
                        })
                        iii1=iii1+1
                        alarma_anterior = 'notpresente'



        if not not sdr2: 
            rssi2 = MeasureRSSI(sdr2) - ampl_offset2
            avg_rssi2 = ((15 * avg_rssi2) + rssi2) / 16 
            max_rssi2 = max(max_rssi2, rssi2)
        

            counter2 += 1
            if counter2 & 0x1F == 0:
                max_rssi2 = rssi2
                if(max_rssi2)>5:
                    if(alarma_anterior2=='jammer'):
                        alarma_anterior2 = 'jammer'
                    else:
                        r2 = requests.post('https://us-central1-notjamming-1.cloudfunctions.net/simuladorjammer2', jso
n={
                           "device": "0001A",
                           "rssi": max_rssi2,
                           "secuenciax":ii2,
                           "secuencia2x":iii2,
                           "frecuencia":"915",
                           "jammer915": "jammer"
                        })
                        ii2=ii2+1

                        alarma_anterior2 = 'jammer'
                else:
                    if(alarma_anterior2=='notpresente'):
                        alarma_anterior2 = 'notpresente'
                    else:
                        r2 = requests.post('https://us-central1-notjamming-1.cloudfunctions.net/simuladorjammerOff2', 
json={
                           "device": "0001A",
                           "rssi": 0,
                           "jammer915": "notpresente",
                           "secuenciax":ii2,
                           "secuencia2x":iii2,
                           "frecuencia":"915"
                        })
                        iii2=iii2+1

                        alarma_anterior2 = 'notpresente'

def MeasureRSSI_1(sdr):
    samples = sdr.read_samples(NUM_SAMPLES)
    power = 0.0
    for sample in samples:
        power += (sample.real * sample.real) + (sample.imag * sample.imag)
    return 10 * (math.log(power) - math.log(NUM_SAMPLES))

# Second go: read raw bytes, square and add those
def MeasureRSSI_2(sdr):
    data_bytes = sdr.read_bytes(NUM_SAMPLES * 2)
    power = 0
    for next_byte in data_bytes:
        signed_byte = next_byte + next_byte - 255
        power += signed_byte * signed_byte
    return 10 * (math.log(power) - math.log(NUM_SAMPLES) - math.log(127)) - 70

# Third go: modify librtlsdr, do the square-and-add calculation in C
def MeasureRSSI_3(sdr):
    while(True):
        try:
            return sdr.read_power_dB(NUM_SAMPLES) - 112
        except OSError: # e.g. SDR unplugged...
            pass # go round and try again, SDR will be replugged sometime...

# Select the desired implementation here:
def MeasureRSSI(sdr):
    return MeasureRSSI_3(sdr)

def redirect_stderr():
    import os, sys
    sys.stderr.flush()
    err = open('/dev/null', 'a+')
    os.dup2(err.fileno(), sys.stderr.fileno()) # send ALSA underrun error messages to /dev/null

if __name__ == "__main__":
    import os, sys
    main()
