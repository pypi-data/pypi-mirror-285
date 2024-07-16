import json
from pyModbusTCP.client import ModbusClient

# JSON 파일에서 MODBUS 주소 값을 읽어오는 함수
def load_modbus_addresses(json_file_path):
    with open(json_file_path, 'r') as file:
        return json.load(file)

# JSON 파일 경로 설정
monitor_modbus_address_file_path = 'config/monitor_modbus_addresses.json'
remote_modbus_address_file_path = 'config/remote_modbus_addresses.json'

# JSON 파일에서 MODBUS 주소 값을 로드
monitor_modbus_addresses = load_modbus_addresses(monitor_modbus_address_file_path)
remote_modbus_addresses = load_modbus_addresses(remote_modbus_address_file_path)

def get_modbus_address(data_type):
    # monitor_modbus_addresses 에서 값 찾기
    if data_type in monitor_modbus_addresses:
        return monitor_modbus_addresses[data_type]
    # remote_modbus_addresses 에서 값 찾기
    if data_type in remote_modbus_addresses:
        return remote_modbus_addresses[data_type]
    # 둘 다 없으면 default 값 반환
    return monitor_modbus_addresses.get("default", 0)

def read_modbus_data(device):
    print('### data_type: ', device['data_type'])
    modbus_address = get_modbus_address(device['data_type'])
    # print('modbus_address: ', modbus_address)
    modbus_client = ModbusClient(host=device['ip'], port=int(device['port']), unit_id=int(device['unit_id']), auto_open=True)
    register_address = int(device['register_address']) + modbus_address
    register_length = 1
    regs = modbus_client.read_holding_registers(register_address, register_length)
    print('modbus_address: ', modbus_address, " / regs: ", regs)
    if regs:
        return regs
    else:
        return None

# # 테스트용 device 예시
# device = {
#     'ip': 'gjl2.iptime.org',
#     'port': 504,
#     'unit_id': 1,
#     'register_address': 40000,
#     'data_type': '조도'
# }
#
# # 함수 호출 예시
# data = read_modbus_data(device)
# print(data)
