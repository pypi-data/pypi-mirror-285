import time

my_lst = [0, 0, 0]
my_lst2 = [0, 0, 0]
t1 = time.perf_counter()
for _ in range(1000):
	for i in range(10000):
		result = my_lst == my_lst2
t2 = time.perf_counter()
print(t2 - t1)
