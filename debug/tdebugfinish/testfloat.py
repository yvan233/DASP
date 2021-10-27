import struct
def ReadFloat(high, low):
    """
    modbus 读取float函数
    """
    high = '%04x'%high
    low =  '%04x'%low
    v = high + low
    y_bytes = bytes.fromhex(v)
    y = struct.unpack('!f',y_bytes)[0]
    y = round(y,6)
    return y

print(ReadFloat(5854,0))
