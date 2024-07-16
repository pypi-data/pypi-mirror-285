import multiprocessing 

## print("load process")

class ProcessObj():
    def __init__(self, processobj:multiprocessing.Process) -> None:
        self.processobj = processobj 
    
    def Join(self):
        self.processobj.join()

class ProcessObjs():
    def __init__(self, processobjs:list[multiprocessing.Process]) -> None:
        self.processobjs = processobjs
    
    def Join(self):
        [i.join() for i in self.processobjs]

def Process(func, *args, count:int=1) -> ProcessObj | ProcessObjs:
    """
    注意调用这个函数的时候要放到if __name__ == "__main__"里面, 否则可能会报错
    """
    if count == 1:
        t = multiprocessing.Process(target=func, args=args)
        t.daemon = True 
        t.start()

        return ProcessObj(t)
    elif count > 1:
        ts = []
        for _ in range(count):
            t = multiprocessing.Process(target=func, args=args)
            t.daemon = True 
            t.start()

            ts.append(t)

        return ProcessObjs(ts)
    else:
        raise Exception("count异常")

    return p 

# import time 
# 
# def p(s:str, ss:str):
#     while True:
#         time.sleep(1)
#         print(s, ss, time.time())

if __name__ == "__main__":
    pass 
