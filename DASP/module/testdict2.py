# 测试json格式化输出
import json
info = [{'ID': 'room_1', 'value': ['room_2', 'room_4']}, {'ID': 'room_2', 'value': ['room_1', 'room_3', 'room_5']}, {'ID': 'room_3', 'value': ['room_2', 'room_6', 'pump_1']}, {'ID': 'room_6', 'value': ['room_3', 'room_5', 'room_7']}, {'ID': 'room_7', 'value': ['room_6', 'room_8', 'pump_1', 'communication_node']}, {'ID': 'room_8', 'value': ['room_7', 'pump_2', 'communication_node']}, {'ID': 'communication_node', 'value': ['room_7', 'room_8']}, {'ID': 'pump_1', 'value': ['room_3', 'room_7', 'pump_2', 'heatpump_1']}, {'ID': 'pump_2', 'value': ['room_8', 'pump_1', 'heatpump_1']}, {'ID': 'heatpump_1', 'value': ['pump_1', 'pump_2']}, {'ID': 'room_4', 'value': ['room_1', 'room_5']}, {'ID': 'room_5', 'value': ['room_2', 'room_4', 'room_6']}]
infolist = json.dumps(info, indent=2)
print (info)
print (infolist)