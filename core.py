
import heapq
from threading import Thread, Semaphore
from time import sleep
from enum import Enum
from typing import Callable

time_unit = 1
global_time = 0


class Direction(Enum):
    UP = 2
    DOWN = 1
    IDLE = 0


class ReqType(Enum):
    EXTERNAL = 0
    INTERNAL = 1


class Request:
    def __init__(self, src, dst):
        self.type = ReqType.EXTERNAL
        self.src = src
        self.dst = dst
        self.target = src
        self.src_arrival = global_time
        self.dst_arrival = -1

        self.cost = 0

    def convertToInternal(self):
        self.type = ReqType.INTERNAL
        self.target = self.dst
        self.dst_arrival = global_time

    def __repr__(self) -> str:
        return self.type.name+"->"+repr(self.target)

    def __lt__(self, other):
        return self.target < other.target
    def __le__(self, other):
        return self.target <= other.target
    def __eq__(self, other):
        return self.target == other.target


# TODO: FCFS
class PriorityQ(list):
    s = Semaphore(0)

    def put(self, item):
        self.s.release()
        heapq.heappush(self, item)

    def pop(self):
        self.s.acquire()
        return heapq.heappop(self)

    def top(self):
        return self[0]


class Elevator:
    def __init__(self):
        self.pq = PriorityQ()
        self.currentFloor = 0
        self.direction = Direction.IDLE

        # target
        self.t = None

    def submit(self, req: Request):
        self.pq.put([self.costFunc(req), req])

    def _update_costs(self):
        # TODO: starvation
        for i in range(len(self.pq)):
            self.pq[i][0] = self.costFunc(self.pq[i][1])

    def _scheduler(self):
        # target selection
        if self.t == None:
            self.t = self.pq.pop()
            print(self.pq)
        else:
            # if there is better target, switch the target
            if len(self.pq) != 0:
                candid = self.pq.top()
                # compare costs
                if candid[0] < self.t[0]:
                    self.pq.put(self.t)
                    self.t = self.pq.pop()

        cost, req = self.t

        # elevator move
        if self.currentFloor > req.target:
            self.currentFloor -= 1
            self.direction = Direction.DOWN
        elif self.currentFloor < req.target:
            self.currentFloor += 1
            self.direction = Direction.UP

        self._update_costs()

        if self.currentFloor == req.target:
            if req.type == ReqType.EXTERNAL:
                req.convertToInternal()
                self.pq.put([self.costFunc(req), req])
            self.t = None
        else:
            # TODO
            self.pq.put([self.costFunc(req), req])

        # debug
        print(self.currentFloor)

    # TODO
    def costFunc(self, req: Request) -> int:
        return 0



# bara inke b kodom asansor pass bede
# TODO: singleton
class Elevators:
    def __init__(self, num) -> None:
        self.elevators = []
        for _ in range(num):
            self.elevators.append(Elevator())

        Thread(target=self.runner).start()

    def runner(self):
        global global_time
        global time_unit
        while True:
            for e in self.elevators:
                e._scheduler()
            sleep(time_unit)
            global_time+=1

    def submit(self, req: Request):
        # TODO
        self.elevators[0].submit(req)




######################################################################


if __name__ == "__main__":
    e = Elevators(1)

    while (True):
        req = [int(x) for x in input().split()]  # external internal
        e.submit(Request(req[0], req[1]))

        # print(e.elevators[0].pq)
