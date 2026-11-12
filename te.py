import ctypes
from ctypes import *
import time
import win32api

vm = ctypes.WinDLL("c:/windows/system32/teVirtualMIDI.dll")
getver = vm.virtualMIDIGetVersion
getver.restype=c_wchar_p

major,minor,release,build=c_int(),c_int(),c_int(),c_int()
val = getver(byref(major), byref(minor), byref(release), byref(build))
print(val,major,minor,release,build)

#typedef void ( CALLBACK *LPVM_MIDI_DATA_CB )( LPVM_MIDI_PORT midiPort, LPBYTE midiDataBytes, DWORD length, DWORD_PTR dwCallbackInstance );
#CALLBACK = CFUNCTYPE(None, c_void_p, c_char_p, c_long, POINTER(c_long))

#LPVM_MIDI_PORT CALLBACK virtualMIDICreatePortEx2( LPCWSTR portName, LPVM_MIDI_DATA_CB callback, DWORD_PTR dwCallbackInstance, DWORD maxSysexLength, DWORD flags );
createPort2 = vm.virtualMIDICreatePortEx2
createPort2.restype = c_void_p
createPort2.argtypes = [c_wchar_p, c_void_p, POINTER(c_long), c_long, c_long]

closePort = vm.virtualMIDIClosePort
closePort.restype = c_void_p #CALLBACK
closePort.argtypes = [c_void_p]

getData = vm.virtualMIDIGetData
getData.restype = c_bool
getData.argtypes = [c_void_p, c_char_p, POINTER(c_int)]

sendData = vm.virtualMIDISendData
sendData.restype = c_bool
sendData.argtypes = [c_void_p, c_char_p, c_int]

porta = portb = portc = None
na = nb = nc = 0

def get_system_error_message(error_code=None):
    try:
        if error_code is None:
            error_code = win32api.GetLastError()
        error_message = win32api.FormatMessage(
            win32con.FORMAT_MESSAGE_FROM_SYSTEM,
            None,
            error_code,
            0,
            None,
        )
        return error_message.strip()
    except Exception as e:
        return f"Error retrieving system message: {e}"

def tester():
    global porta, portb, portc
    porta = createPort2("PIONEER DDJ-SX2", None, None, 10240, 1 + 2 + 4 + 8)
    portb = createPort2("Internal", None, None, 10240, 1 + 2 + 4 + 8)
    portc = createPort2("XONE-LED", None, None, 10240, 1 + 2 + 4 + 8)
    print("Port handles:", porta, portb, portc)
    if porta is None or portb is None or portc is None:
        print("Could not create ports? ERR:", win32api.GetLastError(), get_system_error_message())
        return

    def atob():
        global na, porta, portb
        buf1 = create_string_buffer(10240)
        while True:
            sz = c_int(10240)
            res = getData(porta, buf1, byref(sz))
            if res:
                sendData(portb, buf1, sz)
                na += 1
            else:
                print("ERR a->b:", win32api.GetLastError(), get_system_error_message())
                time.sleep(0.1)

    def btoa():
        global nb, porta, portb
        buf2 = create_string_buffer(10240)
        while True:
            sz = c_int(10240)
            res = getData(portb, buf2, byref(sz))
            if res:
                sendData(porta, buf2, sz)
                nb += 1
            else:
                print("ERR b->a:", win32api.GetLastError(), get_system_error_message())
                time.sleep(0.1)

    def ctob():
        global nc, portc, portb
        buf3 = create_string_buffer(10240)
        while True:
            sz = c_int(10240)
            res = getData(portc, buf3, byref(sz))
            if res:
                sendData(portb, buf3, sz)
                nc += 1
            else:
                print("ERR c->b:", win32api.GetLastError(), get_system_error_message())
                time.sleep(0.1)

    threada = Thread(target=atob, daemon=True)
    threadb = Thread(target=btoa, daemon=True)
    threadc = Thread(target=ctob, daemon=True)
    threada.start()
    threadb.start()
    threadc.start()

    na0 = nb0 = nc0 = 0
    while True:
        time.sleep(1)
        if na != na0 or nb != nb0 or nc != nc0:
            print(na, nb, nc, "| diff:", na - na0, nb - nb0, nc - nc0)
            na0 = na
            nb0 = nb
            nc0 = nc

    closePort(porta)
    closePort(portb)
    closePort(portc)

if __name__ == "__main__":
    tester()


    porta = createPort2("PIONEER DDJ-SX2", None, None, 10240, 1 + 2 + 4 + 8)
    portb = createPort2("Internal", None, None, 10240, 1 + 2 + 4 + 8)
    print("Port handles:",porta,portb)
    if porta is None or portb is None:
        print("Could not create ports? ERR:",win32api.GetLastError(), get_system_error_message())
        return
    t=0
    def atob():
        global na,porta,portb
        buf1 = create_string_buffer(10240)
        while True:
            sz = c_int(10240) 
            res = getData(porta, buf1, byref(sz))
            if res:
                sendData(portb, buf1, sz)
                na+=1                
            else:
                print("ERR a->b:",win32api.GetLastError(), get_system_error_message())
                time.sleep(0.1)
                #break
    def btoa():
        global nb,porta,portb
        buf2 = create_string_buffer(10240)
        while True:
            sz = c_int(10240) 
            res = getData(portb, buf2, byref(sz))
            if res:
                sendData(porta, buf2, sz)            
                nb+=1
            else:
                print("ERR b->a:",win32api.GetLastError(), get_system_error_message())
                time.sleep(0.1)
                #break
    from threading import Thread
    threada = Thread(target=atob, daemon=True)
    threadb = Thread(target=btoa, daemon=True)
    threada.start()
    threadb.start()
    na0=nb0=0
    while True:
        time.sleep(1)
        if na!=na0 or nb!=nb0:
            print(na,nb,na-na0,nb-nb0)
            na0=na
            nb0=nb
    closePort(porta)
    closePort(portb)

if __name__ == "__main__":
    tester()
