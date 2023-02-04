
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
    def __init__(self):
        self.s = Semaphore(0)
        super().__init__()

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
        for t in self.pq:
            _, r = t
            if req.src == r.src and req.dst == r.dst:
                return
        self.pq.put([self.costFunc(req), req])

    def _update_costs(self):
        # TODO: starvation
        SE = 1
        SI = 0.5
        for i in range(len(self.pq)):
            self.pq[i][0] = self.costFunc(self.pq[i][1])
            if self.pq[i][1].type == ReqType.INTERNAL:
                self.pq[i][0] -= int((global_time -
                                     self.pq[i][1].src_arrival) * SI)
            else:
                self.pq[i][0] -= int((global_time -
                                     self.pq[i][1].dst_arrival) * SE)

    def _scheduler(self):
        if len(self.pq) == 0:
            return

        # target selection
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
        else:
            # TODO
            self.pq.put([self.costFunc(req), req])

    # TODO
    def costFunc(self, req: Request) -> int:
        # Cost = |currentFloor - targetFloor| + DREWARD if direction != targetDirection
        DREWARD = 5
        cost = abs(self.currentFloor - req.target)
        direct = Direction.UP if self.currentFloor < req.target else Direction.DOWN
        if self.direction != direct and self.direction != Direction.IDLE:
            cost += DREWARD
        return cost


# bara inke b kodom asansor pass bede
# TODO: singleton
class Elevators:
    def __init__(self, num) -> None:
        self.elevators: list[Elevator] = []
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
            global_time += 1
            # debug
            for e in self.elevators:
                print(e.currentFloor,end=", ")
            print("")

    def submit(self, req: Request):
        # Select the lowest cost elevator
        best = 0
        cost = self.elevators[0].costFunc(req)
        for i in range(1, len(self.elevators)):
            c = self.elevators[i].costFunc(req)
            if c < cost:
                cost = c
                best = i
        self.elevators[best].submit(req)

#        # select the elevator with the lowest cost sum
#        sum = sum(self.elevators[0].pq)
#        best = 0
#        for i in range(1, len(self.elevators)):
#            s = sum(self.elevators[i].pq)
#            if s < sum:
#                sum = s
#                best = i
#        self.elevators[best].submit(req)


######################################################################


if __name__ == "__main__":
    e = Elevators(3)

    while (True):
        req = [int(x) for x in input().split()]  # external internal
        e.submit(Request(req[0], req[1]))
