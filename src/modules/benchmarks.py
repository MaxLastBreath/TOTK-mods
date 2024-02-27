import os
import re
from modules.logger import log

def load_benchmark(self):
    benchmark_file = os.path.join(self.sdmc_dir, "TOTKBenchmark.txt")
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
                    self.benchmarks[keyword] = {
                        "Total Frames": numbers[0],
                        "Average FPS": numbers[1],
                        "1% Low FPS": numbers[2],
                        "0.1% Lowest FPS": numbers[3],
                    }
    except FileNotFoundError:
        log.info("No Benchmarks detected.")
    print(self.benchmarks)
