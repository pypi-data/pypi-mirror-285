import multiprocessing
import time
import fedml
from fedml.computing.scheduler.scheduler_core.shared_resource_manager import FedMLSharedResourceManager


class B:
    def __init__(self):
        self.q = FedMLSharedResourceManager.get_instance().get_queue()
        self.e = FedMLSharedResourceManager.get_instance().get_event()

    def run(self, queue_obj, event_obj, queue_obj2, event_obj2):
        print("B, run sub entry")

        while True:
            time.sleep(1)
            content = queue_obj.get(block=False, timeout=0.5)
            content2 = queue_obj2.get(block=False, timeout=0.5)
            print(f"B, run sub, content {content}, content2 {content2}")


class A:
    def __init__(self):
        self.q = FedMLSharedResourceManager.get_instance().get_queue()
        self.e = FedMLSharedResourceManager.get_instance().get_event()

    def run(self, queue_obj, event_obj):
        print("A, run sub entry")

        b_obj = B()
        multiprocessing.Process(target=b_obj.run, args=(queue_obj, event_obj, b_obj.q, b_obj.e,)).start()

        while True:
            time.sleep(1)
            b_obj.q.put("test")
            #content = queue_obj.get(block=False, timeout=0.5)
            #print(f"A, run sub, content {content}")
            print(f"A, run sub")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    fedml._init_multiprocessing()

    a_obj = A()
    multiprocessing.Process(target=a_obj.run, args=(a_obj.q, a_obj.e,)).start()
    while True:
        time.sleep(1)
        a_obj.q.put("test")
        print("run main")

