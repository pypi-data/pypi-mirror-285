import json
from pyModbusTCP.client import ModbusClient

# JSON 파일에서 MODBUS 주소 값을 읽어오는 함수
def load_modbus_addresses(json_file_path):
    with open(json_file_path, 'r') as file:
        return json.load(file)

# Read 용 JSON 파일 경로 설정
modbus_address_file_path = 'config/monitor_modbus_addresses.json'

# Read 용 JSON 파일에서 MODBUS 주소 값을 로드
MODBUS_ADDRESSES = load_modbus_addresses(modbus_address_file_path)

def read_modbus_data(device):
    print('### data_type: ', device['data_type'])
    modbus_address = MODBUS_ADDRESSES.get(device['data_type'], "default")
    print('modbus_address: ', modbus_address)
    modbus_client = ModbusClient(host=device['ip'], port=int(device['port']), unit_id=int(device['unit_id']), auto_open=True)
    register_address = int(device['register_address']) + modbus_address
    register_length = 1
    regs = modbus_client.read_holding_registers(register_address, register_length)
    print('modbus_address: ', modbus_address, " / regs: ", regs)
    if regs:
        return regs
    else:
        return None

