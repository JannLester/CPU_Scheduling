def get_positive_int(prompt):
    while True:
        try:
            value = int(input(prompt))
            if value <= 0:
                print("Value must be greater than 0.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter an integer.")


def get_non_negative_int(prompt):
    while True:
        try:
            value = int(input(prompt))
            if value < 0:
                print("Value cannot be negative.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter an integer.")


def choose_algorithm():
    while True:
        print("\nChoose Algorithm:")
        print("1. FCFS")
        print("2. SJF (Non-preemptive)")
        print("3. SRTF (Preemptive)")
        print("4. Priority (Non-preemptive)")
        print("5. Round Robin")
        choice = input("Enter choice (1-5): ")
        if choice in ['1', '2', '3', '4', '5']:
            return choice
        print("Invalid choice.")


def collect_processes(algorithm):
    n = get_positive_int("Enter number of processes: ")
    processes = []

    for i in range(1, n + 1):
        print(f"\nProcess P{i}")
        at = get_non_negative_int("Arrival Time: ")
        bt = get_positive_int("Burst Time: ")

        process = {
            "id": i,
            "at": at,
            "bt": bt,
            "remaining_bt": bt
        }

        if algorithm == '4':
            process["priority"] = get_non_negative_int("Priority (lower = higher): ")

        processes.append(process)

    return processes


def schedule_processes(processes, algorithm, quantum=None):
    current_time = 0
    ready_queue = []
    pool = sorted(processes, key=lambda x: x['at'])
    finished = []
    gantt = []

    def add_gantt(pid, start, end):
        if gantt and gantt[-1]['id'] == pid and gantt[-1]['finish'] == start:
            gantt[-1]['finish'] = end
        else:
            gantt.append({'id': pid, 'start': start, 'finish': end})

    # ---------------- FCFS / SJF / Priority ----------------
    if algorithm in ['1', '2', '4']:

        while pool or ready_queue:
            while pool and pool[0]['at'] <= current_time:
                ready_queue.append(pool.pop(0))

            if not ready_queue:
                current_time = pool[0]['at']
                continue

            if algorithm == '1':
                ready_queue.sort(key=lambda x: x['at'])

            elif algorithm == '2':
                ready_queue.sort(key=lambda x: (x['bt'], x['at']))

            elif algorithm == '4':
                ready_queue.sort(key=lambda x: (x['priority'], x['at']))

            p = ready_queue.pop(0)

            start = current_time
            current_time += p['bt']

            p['finish'] = current_time
            p['tat'] = p['finish'] - p['at']
            p['wt'] = p['tat'] - p['bt']

            add_gantt(p['id'], start, current_time)
            finished.append(p)

    # ---------------- SRTF (FIXED RULE) ----------------
    elif algorithm == '3':

        completed = 0
        n = len(processes)

        while completed < n:

            while pool and pool[0]['at'] <= current_time:
                ready_queue.append(pool.pop(0))

            if not ready_queue:
                current_time = pool[0]['at']
                continue

            # ✅ YOUR FIX:
            # same remaining BT → newer arrival wins (higher AT priority)
            ready_queue.sort(key=lambda x: (x['remaining_bt'], -x['at']))

            p = ready_queue[0]

            add_gantt(p['id'], current_time, current_time + 1)

            p['remaining_bt'] -= 1
            current_time += 1

            if p['remaining_bt'] == 0:
                p['finish'] = current_time
                p['tat'] = p['finish'] - p['at']
                p['wt'] = p['tat'] - p['bt']

                finished.append(p)
                ready_queue.pop(0)
                completed += 1

    # ---------------- ROUND ROBIN ----------------
    elif algorithm == '5':

        quantum = get_positive_int("Enter Quantum: ")
        completed = 0
        n = len(processes)

        while pool and pool[0]['at'] <= current_time:
            ready_queue.append(pool.pop(0))

        while completed < n:

            if not ready_queue:
                current_time = pool[0]['at']
                while pool and pool[0]['at'] <= current_time:
                    ready_queue.append(pool.pop(0))
                continue

            p = ready_queue.pop(0)

            run_time = min(quantum, p['remaining_bt'])

            add_gantt(p['id'], current_time, current_time + run_time)

            current_time += run_time
            p['remaining_bt'] -= run_time

            while pool and pool[0]['at'] <= current_time:
                ready_queue.append(pool.pop(0))

            if p['remaining_bt'] == 0:
                p['finish'] = current_time
                p['tat'] = p['finish'] - p['at']
                p['wt'] = p['tat'] - p['bt']
                finished.append(p)
                completed += 1
            else:
                ready_queue.append(p)

    return finished, gantt


def print_table(processes):
    print("\nProcess Table")
    print("P | AT | BT | FT | TAT | WT")
    print("-" * 30)

    for p in sorted(processes, key=lambda x: x['id']):
        print(f"P{p['id']} | {p['at']} | {p['bt']} | {p['finish']} | {p['tat']} | {p['wt']}")


def draw_gantt(gantt):
    print("\nGantt Chart")

    for g in gantt:
        print(f"| P{g['id']} ", end="")
    print("|")

    print("0", end="")
    for g in gantt:
        print(f"  {g['finish']}", end="")
    print("\n")


def print_averages(processes):
    total_wt = sum(p['wt'] for p in processes)
    total_tat = sum(p['tat'] for p in processes)

    print(f"\nAWT = {total_wt / len(processes):.2f}")
    print(f"ATT = {total_tat / len(processes):.2f}")


def main():
    algo = choose_algorithm()
    processes = collect_processes(algo)

    finished, gantt = schedule_processes(processes, algo)

    print_table(finished)
    draw_gantt(gantt)
    print_averages(finished)


if __name__ == "__main__":
    main()
