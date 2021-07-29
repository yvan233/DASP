import time
# i = 1
for i in range(3):
    print('subprocess print...', flush=True)
    time.sleep(i)
    i = i + 1