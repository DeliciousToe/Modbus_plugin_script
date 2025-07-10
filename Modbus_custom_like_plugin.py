#!/usr/bin/env python3

import sys
import struct
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder

def read_modbus_data(endpoint, slave_id, function_code, address, count, data_type, timeout_str):
    client = None
    try:
        if not endpoint.startswith("tcp://"):
            return "ERROR: Nieprawidłowy format endpointu. Oczekiwano tcp://IP:Port"
        parts = endpoint[len("tcp://"):].split(':')
        if len(parts) != 2:
            return "ERROR: Nieprawidłowy format endpointu. Oczekiwano tcp://IP:Port"

        host = parts[0]
        port = int(parts[1])

        timeout = float(timeout_str.replace('s', ''))

        client = ModbusTcpClient(host, port=port, timeout=timeout)

        if not client.connect():
            return f"ERROR: Nie można połączyć się z {host}:{port}"

        required_registers = 2 if data_type in ["float", "uint32", "int32"] else (4 if data_type == "double" else 1)
        if count < required_registers:
            return f"ERROR: Niewystarczająca liczba rejestrów. Wymagane: {required_registers}"

        result = None
        if function_code == 3:
            result = client.read_holding_registers(address, count, unit=slave_id)
        elif function_code == 4:
            result = client.read_input_registers(address, count, unit=slave_id)
        else:
            client.close()
            return f"ERROR: Nieobsługiwany kod funkcji Modbus: {function_code}"

        if result.isError():
            client.close()
            return f"Error: Błąd Modbus: {result}"

        decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.Big, wordorder=Endian.Big)

        value = None
        if data_type == "float":
            value = decoder.decode_32bit_float()
        elif data_type == "double":
            value = decoder.decode_64bit_float()
        elif data_type == "uint16":
            value = decoder.decode_16bit_uint()
        elif data_type == "int16":
            value = decoder.decode_16bit_int()
        elif data_type == "uint32":
            value = decoder.decode_32bit_uint()
        elif data_type == "int32":
            value = decoder.decode_32bit_int()
        else:
            client.close()
            return f"ERROR: Nieobsługiwany typ danych: {data_type}"

        return str (value)

    except ValueError as e:
        return f"ERROR: Błąd parsowania parametru: {e}"
    except Exception as e:
        return f"ERROR: Wystąpił nieoczekiwany błąd: {e}"
    finally:
        if client:
            client.close()

if __name__ == "__main__":
    if len(sys.argv) != 8:
        print("ERROR: Nieprawidłowa liczba argumentów.")
        print("Użycie: modbus_read.py <endpoint> <slave_id> <function_code> <address> <count> <data_type> <timeout>")
        sys.exit(1)

    endpoint = sys.argv[1]
    slave_id = int(sys.argv[2])
    function_code = int(sys.argv[3])
    address = int(sys.argv[4])
    count = int(sys.argv[5])
    data_type = sys.argv[6]
    timeout_str = sys.argv[7]

    result = read_modbus_data(endpoint, slave_id, function_code, address, count, data_type, timeout_str)
    print(result)
    sys.exit(0)