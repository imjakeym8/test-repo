# list_of_dicts = [
# {"type":"character","counter":0,"trigger":True},
# {"type":"character","counter":0,"trigger":True},
# {"type":"character","counter":0,"trigger":True},
# {"type":"character","counter":0,"trigger":True}
# ]
# another_dicts = [
# {"type":"event","counter":1000,"trigger":True},
# {"type":"event","counter":1000,"trigger":True},
# {"type":"event","counter":1000,"trigger":True},
# ]
# 
# 
# new_list = [ each["counter"] for each in list_of_dicts + another_dicts if each["counter"] < 1000 and each["type"] == "event"]
# new_ratio = len(new_list) / 10 * 100 if new_list != [] else 0
# print(new_ratio)
# 
# my_array = [num for num in range(1, 101)]
# print(my_array)
# 
# low = 0
# high = len(my_array) - 1
# target = 42
# 
# while low <= high:
#     middle = low + (high - low) // 2
#     value = my_array[middle]
#     print(f"Middle: {middle}, Value: {value}")
# 
#     if value < target:
#         low = middle + 1
#     elif value > target:
#         high = middle - 1
#     else:
#         print(f"Found target {target} at index {middle}")
#         break
# else:
#     print(f"Target {target} not found.")

def func():
    return "apple","banana","carrot"

string = func()

print(string[0])
