list_of_dicts = [
{"type":"character","counter":0,"trigger":True},
{"type":"character","counter":0,"trigger":True},
{"type":"character","counter":0,"trigger":True},
{"type":"character","counter":0,"trigger":True}
]
another_dicts = [
{"type":"event","counter":1000,"trigger":True},
{"type":"event","counter":1000,"trigger":True},
{"type":"event","counter":1000,"trigger":True},
]


new_list = [ each["counter"] for each in list_of_dicts + another_dicts if each["counter"] < 1000 and each["type"] == "event"]
new_ratio = len(new_list) / 10 * 100 if new_list != [] else 0
print(new_ratio)