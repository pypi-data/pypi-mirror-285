import os
import json
import csv
import time
import threading
from modbus_reader import read_modbus_data
from mqtt_publisher import setup_mqtt_client, publish_data

# 현재 작업 디렉토리 확인
print(f"Current working directory: {os.getcwd()}")

# JSON 파일 읽기
json_file_path = os.path.join(os.path.dirname(__file__), '../config/farm_info.json')
with open(json_file_path, 'r', encoding='utf-8') as json_file:
    farm_info = json.load(json_file)

# CSV 파일 읽기
csv_file_path = os.path.join(os.path.dirname(__file__), f"../config/{farm_info['modbus_csv_files'][0]}")
devices = []

with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        if row["reg_adres"]:  # register_address가 있는 경우에만 추가
            device_info = {
                "tag_id": row["tag_id"],
                "p_tag_id": row["parent_tag_id"],
                "zone_id": row["zone_id"],
                "room_id": row["room_id"],
                "data_type": row["data_type"],
                "ip": row["mdbs_ip_adres"],
                "port": row["port"],
                "unit_id": row["unit_id"] or "1",  # unit_id가 빈 값이면 기본값 1로 설정
                "register_address": row["reg_adres"],
                "data_format": row["data_format"],
                "scale_val": row["scale_val"],
                "unit": row["unit"],
                "remarks": row["remarks"],
                "grp_id": row["grp_id"],
                "first_bit_order_id": row["first_bit_order_id"],
                "enabled": row["enabled"]
            }
            devices.append(device_info)

# 각 그룹에 해당하는 장비들을 매핑
grouped_devices = {group['grp_id']: [] for group in farm_info['group']}
for device in devices:
    if device['grp_id'] in grouped_devices:
        grouped_devices[device['grp_id']].append(device)

# MQTT 클라이언트 설정 (주석 처리)
# client = setup_mqtt_client()

def publish_device_data(device, farm_info):
    modbus_data = read_modbus_data(device)
    if modbus_data is not None:
        payload = {
            "tnnt_id": farm_info["tnnt_id"],
            "tnnt_name": farm_info["tnnt_name"],
            "farm_id": farm_info["farm_id"],
            "farm_name": farm_info["farm_name"],
            "location": farm_info["location"],
            "device": device,
            "modbus_data": modbus_data
        }
        # MQTT 전송 대신 출력
        # publish_data(client, payload)
        print(f"Prepared data: {json.dumps(payload, indent=2)}")
    else:
        print(f"Failed to read data from device: {device['tag_id']}")
    time.sleep(1)  # 데이터 전송 간격 조절

def handle_write_group(device, farm_info):
    # WRITE 그룹에 대한 로직
    pass

def start_group_thread(group, farm_info, devices):
    while True:
        for device in devices:
            if group["grp_id"].upper() == "WRITE":
                handle_write_group(device, farm_info)
            else:
                publish_device_data(device, farm_info)
        time.sleep(group["poll_interval"])

# 데이터 전송 주기적으로 실행
threads = []
try:
    for group in farm_info["group"]:
        grp_id = group['grp_id']
        if grp_id in grouped_devices:
            thread = threading.Thread(target=start_group_thread, args=(group, farm_info, grouped_devices[grp_id]))
            thread.start()
            threads.append(thread)

    for thread in threads:
        thread.join()

except KeyboardInterrupt:
    print("Data publishing stopped.")
    # MQTT 클라이언트 종료 (주석 처리)
    # client.disconnect()
