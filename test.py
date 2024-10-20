class Some:
    def __init__(self) -> None:
        self.value = {"key":"value"}

some = Some()
a_list = []

a_list.extend([some.value] * 1)
print(a_list)