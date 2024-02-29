import os
import re
from modules.logger import *

def load_last_benchmark(self, name):
    self.maincanvas.itemconfig(name, state="normal")
    self.Curr_Benchmark = name
    if name is None:
        return
    for item in self.benchmark_dicts:
        if name is item:
            continue
        self.maincanvas.itemconfig(item, state="hidden")
    try:
        self.maincanvas.itemconfig("benchmark_info",text=
                                        f"TOTAL Frames - {self.benchmarks[name]['Total Frames']} Frames\n"
                                        f"Average - {self.benchmarks[name]['Average FPS']} FPS\n"
                                        f"1% Lowest FPS - {self.benchmarks[name]['1% Low FPS']} FPS\n"
                                        f"0.1% Lowest FPS - {self.benchmarks[name]['0.1% Lowest FPS']} FPS\n"
                                   )
        self.maincanvas.itemconfig("no_benchmark", state="hidden")
    except Exception as e:
        log.error(f"Benchmark failed. {e}")
        self.maincanvas.itemconfig("no_benchmark", state="normal")
        for item in self.benchmark_dicts:
            self.maincanvas.itemconfig(item, state="hidden")

def load_benchmark(self):
    benchmark_file = os.path.join(self.sdmc_dir, "TOTKBenchmark.txt")
    Last_Found = None
    try:
        with open(benchmark_file, "r") as benchmarks:
            for line in benchmarks:
                for keyword in self.benchmark_dicts:
                    if keyword not in line:
                        continue
                    next_line = next(benchmarks).strip()
                    pattern = r"(\d+(\.\d+)?)"
                    frames = re.findall(pattern, next_line)
                    numbers = [float(num[0]) if '.' in num[0] else int(num[0]) for num in frames]
                    log.info(numbers)
                    if numbers[2] == 1:
                        numbers.pop(2)
                    if numbers[3] == 0.1:
                        numbers.pop(3)
                    self.benchmarks[keyword] = {
                        "Total Frames": numbers[0],
                        "Average FPS": numbers[1],
                        "1% Low FPS": numbers[2],
                        "0.1% Lowest FPS": numbers[3],
                    }
                    Last_Found = keyword
        load_last_benchmark(self, Last_Found)
    except FileNotFoundError:
        log.info("No Benchmarks detected.")
