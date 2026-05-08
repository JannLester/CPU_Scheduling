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
        print("1. FCFS (First-Come, First-Served)")
        print("2. SJF (Shortest Job First - Non-preemptive)")
        print("3. SRTF (Shortest Remaining Time First - Preemptive SJF)")
        print("4. Priority Scheduling (Non-preemptive)")
        print("5. Round Robin")
        choice = input("Enter choice (1-5): ")
        if choice in ['1', '2', '3', '4', '5']:
            return choice
        print("Invalid choice. Enter a number between 1 and 5.")


def collect_processes(algorithm):
    n = get_positive_int("Enter how many processes: ")

    processes = []
    for i in range(1, n + 1):
        print(f"\n--- Process {i} ---")
        at = get_non_negative_int(f"AT for P{i}: ")
        bt = get_positive_int(f"BT for P{i}: ")
        
        process = {
            "id": i,
            "at": at,
            "bt": bt
        }

        if algorithm == '4':
            # Priority Scheduling
            priority = get_non_negative_int(f"Priority for P{i} (lower number = higher priority): ")
            process["priority"] = priority

        processes.append(process)

    return processes


def schedule_processes(processes, algorithm, quantum=None):
    current_time = 0
    finished_processes = []
    gantt = []
    
    def add_to_gantt(pid, start, finish):
        if gantt and gantt[-1]['id'] == pid and gantt[-1]['finish'] == start:
            gantt[-1]['finish'] = finish
        else:
            gantt.append({'id': pid, 'start': start, 'finish': finish})

    ready_queue = []
    pool = sorted([p.copy() for p in processes], key=lambda x: x['at'])
    for p in pool:
        p['remaining_bt'] = p['bt']

    if algorithm in ['1', '2', '4']:  # Non-preemptive
        while pool or ready_queue:
            while pool and pool[0]['at'] <= current_time:
                ready_queue.append(pool.pop(0))
            
            if not ready_queue:
                current_time = pool[0]['at']
                continue
                
            if algorithm == '1': # FCFS
                ready_queue.sort(key=lambda x: x['at'])
            elif algorithm == '2': # SJF
                ready_queue.sort(key=lambda x: (x['bt'], x['at']))
            elif algorithm == '4': # Priority
                ready_queue.sort(key=lambda x: (x['priority'], x['at']))
                
            p = ready_queue.pop(0)
            p['start'] = current_time
            p['finish'] = current_time + p['bt']
            p['tat'] = p['finish'] - p['at']
            p['wt'] = p['tat'] - p['bt']
            
            add_to_gantt(p['id'], p['start'], p['finish'])
            current_time = p['finish']
            finished_processes.append(p)

    elif algorithm == '3':  # SRTF (Preemptive SJF)
        completed = 0
        n = len(processes)
        
        while completed != n:
            while pool and pool[0]['at'] <= current_time:
                ready_queue.append(pool.pop(0))
                
            if not ready_queue:
                current_time = pool[0]['at']
                continue
                
            ready_queue.sort(key=lambda x: (x['remaining_bt'], x['at']))
            p = ready_queue[0]
            
            add_to_gantt(p['id'], current_time, current_time + 1)
                
            p['remaining_bt'] -= 1
            current_time += 1
            
            if p['remaining_bt'] == 0:
                p['finish'] = current_time
                p['tat'] = p['finish'] - p['at']
                p['wt'] = p['tat'] - p['bt']
                finished_processes.append(p)
                ready_queue.pop(0)
                completed += 1

    elif algorithm == '5':  # Round Robin
        completed = 0
        n = len(processes)
        
        while pool and pool[0]['at'] <= current_time:
            ready_queue.append(pool.pop(0))
            
        while completed != n:
            if not ready_queue:
                current_time = pool[0]['at']
                while pool and pool[0]['at'] <= current_time:
                    ready_queue.append(pool.pop(0))
                continue
                
            p = ready_queue.pop(0)
                
            time_to_run = min(quantum, p['remaining_bt'])
            
            add_to_gantt(p['id'], current_time, current_time + time_to_run)
            current_time += time_to_run
            p['remaining_bt'] -= time_to_run
            
            while pool and pool[0]['at'] <= current_time:
                ready_queue.append(pool.pop(0))
                
            if p['remaining_bt'] == 0:
                p['finish'] = current_time
                p['tat'] = p['finish'] - p['at']
                p['wt'] = p['tat'] - p['bt']
                finished_processes.append(p)
                completed += 1
            else:
                ready_queue.append(p)

    return finished_processes, gantt


def print_table(processes):
    has_priority = 'priority' in processes[0]
    width = 98 if has_priority else 85
    
    print("\n" + "=" * width)
    if has_priority:
        print(f"{'Process':<10} | {'Priority':<10} | {'AT':<12} | {'BT':<10} | {'TF':<10} | {'TT':<10} | {'WT':<10}")
    else:
        print(f"{'Process':<10} | {'AT':<12} | {'BT':<10} | {'TF':<10} | {'TT':<10} | {'WT':<10}")
    print("-" * width)

    for p in sorted(processes, key=lambda x: x['id']):
        if has_priority:
            print(f"P{p['id']:<9} | {p['priority']:<10} | {p['at']:<12} | {p['bt']:<10} | {p['finish']:<10} | {p['tat']:<10} | {p['wt']:<10}")
        else:
            print(f"P{p['id']:<9} | {p['at']:<12} | {p['bt']:<10} | {p['finish']:<10} | {p['tat']:<10} | {p['wt']:<10}")

    print("=" * width)


def draw_gantt(gantt):
    if not gantt:
        return
        
    print("\nGANTT CHART")

    # Upper Border
    for _ in gantt:
        print("+" + "-" * 7, end="")
    print("+")

    # Process IDs
    for g in gantt:
        print(f"|  P{g['id']:<2} ", end="")
    print("|")

    # Lower Border
    for _ in gantt:
        print("+" + "-" * 7, end="")
    print("+")

    # Timeline
    print(gantt[0]['start'], end="")
    for g in gantt:
        print(f"{g['finish']:>8}", end="")
    print("\n")


def print_manual_solving(processes, n):
    print("MANUAL SOLVING PER PROCESS:")
    print(f"{'TT (TF - TA)':<40} | {'WT (TT - Burst)':<40}")
    print("-" * 82)

    total_tat = 0
    total_wt = 0

    for p in sorted(processes, key=lambda x: x['id']):
        tat_str = f"P{p['id']}: {p['finish']} - {p['at']} = {p['tat']}"
        wt_str = f"P{p['id']}: {p['tat']} - {p['bt']} = {p['wt']}"
        print(f"{tat_str:<40} | {wt_str:<40}")

        total_tat += p['tat']
        total_wt += p['wt']

    print("\nSOLVING FOR AVERAGES:")
    print("-" * 40)
    print(f"Average TT = {total_tat} / {n} = {total_tat / n:.2f}")
    print(f"Average WT = {total_wt} / {n} = {total_wt / n:.2f}")
    print("-" * 40)


def main():
    try:
        algorithm = choose_algorithm()
        quantum = None
        if algorithm == '5':
            quantum = get_positive_int("Enter Time Quantum: ")
            
        processes = collect_processes(algorithm)
        
        finished_processes, gantt = schedule_processes(processes, algorithm, quantum)

        print_table(finished_processes)
        draw_gantt(gantt)
        print_manual_solving(finished_processes, len(processes))

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()