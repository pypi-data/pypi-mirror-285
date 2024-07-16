import time
from multiprocessing import Value
from os import getpid
from threading import Thread
import pytest
import sdrterm


def test_main():
    FILE_NAME = "../SDRSharp_20160101_231914Z_12kHz_IQ.wav"
    sdrterm.__setStartMethod()
    sdrterm.isDead = Value('b', 0)
    sdrterm.__deletePidFile = sdrterm.__generatePidFile(getpid())
    sdrterm.main(inFile=FILE_NAME,
                 outFile="/dev/null",
                 correct_iq=True,
                 # outFile=/tmp/out.bin,
                 omegaOut=5000, verbose=1)
    sdrterm.main(inFile=FILE_NAME,
                 outFile="/dev/null",
                 normalize_input=True,
                 omegaOut=5000, verbose=2)
    sdrterm.main(demod=sdrterm.DemodulationChoices.AM,
                 inFile=FILE_NAME,
                 outFile="/dev/null",
                 normalize_input=True,
                 omegaOut=5000, verbose=2)
    sdrterm.main(inFile=FILE_NAME,
                 outFile="/dev/null",
                 omegaOut=5000,
                 tuned=155685000,
                 center=-350000,
                 vfos="15000,-60000",
                 plot="ps,water,vfo")
    sdrterm.main(demod='p008',
                 inFile=FILE_NAME,
                 outFile="/dev/null",
                 omegaOut=5000,
                 tuned=155685000,
                 center=-350000,
                 vfos="15000,-60000",
                 plot="ps,water,vfo")
    sdrterm.main(inFile=FILE_NAME,
                 outFile="/dev/null",
                 omegaOut=5000,
                 tuned=155685000,
                 center=-350000,
                 vfos="15000,-60000",
                 plot="p008")
    thread = Thread(target=sdrterm.main, kwargs={
        'inFile': 'slowboi.local:9876',
        'fs':1024000,
        'enc':'B',
        'outFile': "/dev/null",
        'omegaOut': 5000,
        'tuned': 155685000,
        'center': -350000,
        'vfos': "15000,-60000",
        'plot': "ps,water,vfo"
    })
    thread.start()
    time.sleep(10)
    sdrterm.isDead.value = 1
    thread.join()
