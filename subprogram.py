from multiprocessing import Process
from multiprocessing.sharedctypes import Value, Array
import time

count = 1234
counter = Value('d', 0.000)
counter_string = Array('c', "Not working the quick brown fox jumped over the lazy dogs")

def main_loop(counter, counter_string):
    
    global count
    
    while True:
        #try:
        count = count + 0.1
        counter.value = count
        counter_string.value = "String is: " + "{:.1f}".format(count)                     
        #except:
        #    print("Temperature sensor failure.")                 

        # Sleep the process and reloop
        time.sleep(1.0)    

def get_count():
    global count
    return count
        
def get_counter():
    global counter
    return counter.value

def get_counter_string():
    global counter_string
    return counter_string.value
    
main_process = Process (target = main_loop, args=(counter, counter_string))
    
def shutdown():
    main_process.terminate()
    print("Sub program ended")  

def start():
    main_process.start()
    print("Sub program started")
    
