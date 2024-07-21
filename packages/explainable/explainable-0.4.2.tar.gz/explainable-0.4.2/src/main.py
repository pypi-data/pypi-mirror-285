import time

import explainable

# start the server
explainable.init()

# create your data
lst = [0, 1, 2]

# start observing
lst = explainable.observe("view1", lst)

# change your data
while True:
  lst[0] += 1
  lst[1] -= 1
  print(lst)

  time.sleep(1)
