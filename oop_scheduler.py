import sys
from dataclasses import dataclass
from typing import List, Callable

@dataclass
class Process:
    pid: int
    arrival_time: int
    burst_time: int
    priority: int = 0
    
    remaining_time: int = 0
    start_time: int = -1
    finish_time: int = 0
    
    def __post_init__(self):
        self.remaining_time = self.burst_time

    @property
    def turnaround_time(self) -> int:
        return self.finish_time - self.arrival_time

    @property
    def waiting_time(self) -> int:
        return self.turnaround_time - self.burst_time


@dataclass
class GanttSegment:
    pid: int
    start: int
    finish: int


class CPUScheduler:
    """Base class for all CPU scheduling algorithms."""
    def __init__(self, processes: List[Process]):
        self.processes = processes
        self.gantt_chart: List[GanttSegment] = []
        self.current_time = 0

    def record_execution(self, pid: int, duration: int):
        if not self.gantt_chart:
            self.gantt_chart.append(GanttSegment(pid, self.current_time, self.current_time + duration))
        else:
            last = self.gantt_chart[-1]
            if last.pid == pid and last.finish == self.current_time:
                last.finish += duration
            else:
                self.gantt_chart.append(GanttSegment(pid, self.current_time, self.current_time + duration))
        self.current_time += duration

    def run(self):
        raise NotImplementedError("Subclasses must implement run()")


class NonPreemptiveScheduler(CPUScheduler):
    def __init__(self, processes: List[Process], sort_key: Callable[[Process], any]):
        super().__init__(processes)
        self.sort_key = sort_key

    def run(self):
        pool = sorted(self.processes, key=lambda p: p.arrival_time)
        ready_queue: List[Process] = []
        
        while pool or ready_queue:
            while pool and pool[0].arrival_time <= self.current_time:
                ready_queue.append(pool.pop(0))
                
            if not ready_queue:
                self.current_time = pool[0].arrival_time
                continue
                
            ready_queue.sort(key=self.sort_key)
            active_process = ready_queue.pop(0)
            
            if active_process.start_time == -1:
                active_process.start_time = self.current_time
                
            self.record_execution(active_process.pid, active_process.burst_time)
            active_process.remaining_time = 0
            active_process.finish_time = self.current_time


class FCFS(NonPreemptiveScheduler):
    def __init__(self, processes: List[Process]):
        super().__init__(processes, sort_key=lambda p: p.arrival_time)


class SJF(NonPreemptiveScheduler):
    def __init__(self, processes: List[Process]):
        super().__init__(processes, sort_key=lambda p: (p.burst_time, p.arrival_time))


class Priority(NonPreemptiveScheduler):
    def __init__(self, processes: List[Process]):
        super().__init__(processes, sort_key=lambda p: (p.priority, p.arrival_time))


class SRTF(CPUScheduler):
    def run(self):
        pool = sorted(self.processes, key=lambda p: p.arrival_time)
        ready_queue: List[Process] = []
        completed = 0
        n = len(self.processes)
        
        while completed < n:
            while pool and pool[0].arrival_time <= self.current_time:
                ready_queue.append(pool.pop(0))
                
            if not ready_queue:
                self.current_time = pool[0].arrival_time
                continue
                
            ready_queue.sort(key=lambda p: (p.remaining_time, p.arrival_time))
            active_process = ready_queue[0]
            
            if active_process.start_time == -1:
                active_process.start_time = self.current_time
                
            self.record_execution(active_process.pid, 1)
            active_process.remaining_time -= 1
            
            if active_process.remaining_time == 0:
                active_process.finish_time = self.current_time
                ready_queue.pop(0)
                completed += 1


class RoundRobin(CPUScheduler):
    def __init__(self, processes: List[Process], quantum: int):
        super().__init__(processes)
        self.quantum = quantum

    def run(self):
        pool = sorted(self.processes, key=lambda p: p.arrival_time)
        ready_queue: List[Process] = []
        completed = 0
        n = len(self.processes)
        
        while pool and pool[0].arrival_time <= self.current_time:
            ready_queue.append(pool.pop(0))
            
        while completed < n:
            if not ready_queue:
                self.current_time = pool[0].arrival_time
                while pool and pool[0].arrival_time <= self.current_time:
                    ready_queue.append(pool.pop(0))
                continue
                
            active_process = ready_queue.pop(0)
            
            if active_process.start_time == -1:
                active_process.start_time = self.current_time
                
            time_to_run = min(self.quantum, active_process.remaining_time)
            self.record_execution(active_process.pid, time_to_run)
            active_process.remaining_time -= time_to_run
            
            while pool and pool[0].arrival_time <= self.current_time:
                ready_queue.append(pool.pop(0))
                
            if active_process.remaining_time == 0:
                active_process.finish_time = self.current_time
                completed += 1
            else:
                ready_queue.append(active_process)


class ApplicationUI:
    @staticmethod
    def prompt_int(msg: str, min_val: int = 0) -> int:
        while True:
            try:
                v = int(input(msg))
                if v < min_val:
                    print(f"Please enter a number >= {min_val}")
                    continue
                return v
            except ValueError:
                print("Invalid input! Please enter a valid number.")

    @classmethod
    def setup_processes(cls, requires_priority: bool) -> List[Process]:
        num = cls.prompt_int("Enter number of processes: ", min_val=1)
        processes = []
        for i in range(1, num + 1):
            print(f"\n[ Process {i} Details ]")
            at = cls.prompt_int(f"Arrival Time for P{i}: ", min_val=0)
            bt = cls.prompt_int(f"Burst Time for P{i}: ", min_val=1)
            pr = 0
            if requires_priority:
                pr = cls.prompt_int(f"Priority for P{i} (lower = higher priority): ", min_val=0)
            processes.append(Process(pid=i, arrival_time=at, burst_time=bt, priority=pr))
        return processes

    @staticmethod
    def show_metrics(processes: List[Process]):
        processes.sort(key=lambda p: p.pid)
        print("\n" + "=" * 65)
        print(f"{'PID':<5} | {'Arrival':<8} | {'Burst':<6} | {'Finish':<8} | {'Turnaround':<10} | {'Waiting':<8}")
        print("-" * 65)
        
        sum_tat = sum_wt = 0
        for p in processes:
            print(f"P{p.pid:<4} | {p.arrival_time:<8} | {p.burst_time:<6} | {p.finish_time:<8} | {p.turnaround_time:<10} | {p.waiting_time:<8}")
            sum_tat += p.turnaround_time
            sum_wt += p.waiting_time
        print("=" * 65)
        
        count = len(processes)
        print(f"\n* Average Turnaround Time : {sum_tat/count:.2f}")
        print(f"* Average Waiting Time    : {sum_wt/count:.2f}")

    @staticmethod
    def show_gantt(gantt: List[GanttSegment]):
        if not gantt:
            return
            
        print("\n[ GANTT CHART ]")
        cell_width = 8
        top_line = "+"
        mid_line = "|"
        bot_line = "+"
        
        for g in gantt:
            top_line += "-" * cell_width + "+"
            mid_line += f"P{g.pid}".center(cell_width) + "|"
            bot_line += "-" * cell_width + "+"
            
        print(top_line)
        print(mid_line)
        print(bot_line)
        
        time_line = str(gantt[0].start)
        for g in gantt:
            time_str = str(g.finish)
            pad_len = (cell_width + 1) - len(time_str)
            time_line += " " * max(0, pad_len) + time_str
        print(time_line + "\n")


def main():
    print("========================================")
    print(" CPU Scheduling Simulator")
    print("========================================")
    print("1. First-Come, First-Served (FCFS)")
    print("2. Shortest Job First (SJF)")
    print("3. Shortest Remaining Time First (SRTF)")
    print("4. Priority Scheduling")
    print("5. Round Robin (RR)")
    
    choice = ApplicationUI.prompt_int("\nSelect an algorithm (1-5): ", min_val=1)
    if choice not in range(1, 6):
        print("Exiting...")
        sys.exit(0)
        
    quantum = None
    if choice == 5:
        quantum = ApplicationUI.prompt_int("Enter Time Quantum: ", min_val=1)
        
    processes = ApplicationUI.setup_processes(requires_priority=(choice == 4))
    
    scheduler = None
    if choice == 1:
        scheduler = FCFS(processes)
    elif choice == 2:
        scheduler = SJF(processes)
    elif choice == 3:
        scheduler = SRTF(processes)
    elif choice == 4:
        scheduler = Priority(processes)
    elif choice == 5:
        scheduler = RoundRobin(processes, quantum)
        
    if scheduler:
        scheduler.run()
        ApplicationUI.show_metrics(scheduler.processes)
        ApplicationUI.show_gantt(scheduler.gantt_chart)

if __name__ == "__main__":
    main()
