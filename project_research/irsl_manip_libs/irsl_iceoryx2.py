### HOT-FIX
import sys
if not '/opt/python' in sys.path:
    sys.path.append('/opt/python')
###
import iceoryx2 as iox2
##
import ctypes
import io
import numpy as np
import pickle

class SubIce(object):
    def __init__(self, name):
        iox2.set_log_level_from_env_or(iox2.LogLevel.Info)
        self.node = iox2.NodeBuilder.new().create(iox2.ServiceType.Ipc)
        self.name = name
        self.service = (
            self.node.service_builder(iox2.ServiceName.new(self.name))
            .publish_subscribe(iox2.Slice[ctypes.c_uint8])
            .history_size(0)
            .open_or_create()
        )
        self.subscriber = self.service.subscriber_builder().create()
        self.verbose = False

    def has_samples(self):
        return self.subscriber.has_samples()

    def getData(self):
        recv = self.subscriber.receive()
        if recv is None:
            return None
        else:
            data = recv.payload()
            if self.verbose:
                print("received", recv.payload().len(), "bytes")
            c_buffer = ctypes.cast(data.as_ptr(), ctypes.POINTER(ctypes.c_ubyte * data.len()))[0]
            mem_view = memoryview(c_buffer)
            bbuf = io.BytesIO(mem_view)
            return bbuf

    def getLastData(self): ## non blocking receiving data
        while True:
            recv = self.subscriber.receive()
            if recv is None:
                return None
            else:
                if self.subscriber.has_samples():
                    if self.verbose:
                        print('skip sample')
                    continue
                data = recv.payload()
                if self.verbose:
                    print("received", recv.payload().len(), "bytes")
                    #sbuf=recv.payload()
                c_buffer = ctypes.cast(data.as_ptr(), ctypes.POINTER(ctypes.c_ubyte * data.len()))[0]
                mem_view = memoryview(c_buffer)
                bbuf = io.BytesIO(mem_view)
                return bbuf

class PubIce(object):
    def __init__(self, name):
        self.node = iox2.NodeBuilder.new().create(iox2.ServiceType.Ipc)
        self.name = name
        self.service = (
            self.node.service_builder(iox2.ServiceName.new(self.name))
            .publish_subscribe(iox2.Slice[ctypes.c_uint8])
            .open_or_create()
        )
        self.publisher = (
            self.service.publisher_builder()
            .initial_max_slice_len(16)
            .allocation_strategy(iox2.AllocationStrategy.PowerOfTwo)
            .create()
        )
        self.verbose = False

    def sendData(self, data): ## data : byteArray <= b'....' or io.BytesIO.getvalue()
        if type(data) is io.BytesIO:
            data = data.getvalue()
        required_memory_size = len(data)
        sample = self.publisher.loan_slice_uninit(required_memory_size)
        sbuf = sample.payload()
        ## copy
        cp_size = min(sbuf.len(), len(data))
        ctypes.memmove(sbuf.as_ptr(), data, cp_size)
        ##
        sample = sample.assume_init()
        sample.send()

class recvNumpy(SubIce):
    def __init__(self, ice_name):
        super().__init__(ice_name)
    #
    def getLastAry(self): ## non blocking receiving data
        buf = self.getLastData()
        if buf is None:
            return
        buf.seek(0)
        ary = np.load(buf)
        return ary
    #
    def getAllAry(self):
        lst = []
        while self.has_samples():
            buf = self.getData()
            if buf is None:
                break
            buf.seek(0)
            ary = np.load(buf)
            lst.append(ary)
        return lst

class sendNumpy(PubIce):
    def __init__(self, ice_name):
        super().__init__(ice_name)
    #
    def sendAry(self, ary):
        ## type check
        buf = io.BytesIO()
        np.save(buf, ary)
        self.sendData(buf)

## TODO pickle version
