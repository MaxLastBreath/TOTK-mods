import os
import re
from modules.logger import *

def load_last_benchmark(self, name):
    self.maincanvas.itemconfig(name, state="normal")
    for item in self.benchmark_dicts:
        if name is item:
            continue
        self.maincanvas.itemconfig(item, state="hidden")
    self.maincanvas.itemconfig("benchmark_info",text=
                                    f"TOTAL Frames - {self.benchmarks[name]['Total Frames']} Frames\n"
                                    f"Average - {self.benchmarks[name]['Average FPS']} FPS\n"
                                    f"1% Lowest FPS - {self.benchmarks[name]['1% Low FPS']} FPS\n"
                                    f"0.1% Lowest FPS - {self.benchmarks[name]['0.1% Lowest FPS']} FPS\n"
                               )
    self.maincanvas.itemconfig("no_benchmark", state="hidden")

def load_benchmark(self):
    benchmark_file = os.path.join(self.sdmc_dir, "TOTKBenchmark.txt")
    Last_Found = None
    try:
        with open(benchmark_file, "r") as benchmarks:
            for line in benchmarks:
                log.info(line.strip())
                for keyword in self.benchmark_dicts:
                    if keyword not in line:
                        continue
                    next_line = next(benchmarks).strip()
                    pattern = r"(\d+(\.\d+)?)"
                    frames = re.findall(pattern, next_line)
                    numbers = [float(num[0]) if '.' in num[0] else int(num[0]) for num in frames]
                    log.info(numbers)
                    self.benchmarks[keyword] = {
                        "Total Frames": numbers[0],
                        "Average FPS": numbers[1],
                        "1% Low FPS": numbers[3],
                        "0.1% Lowest FPS": numbers[5],
                    }
                    Last_Found = keyword
        if Last_Found is not None:
            load_last_benchmark(self, Last_Found)
        log.info(keyword)
    except FileNotFoundError:
        log.info("No Benchmarks detected.")
