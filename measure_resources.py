"""
Measure resource usage for the car simulation.
"""
import time
import tracemalloc
import psutil
import os
import sys

# Start memory tracking
tracemalloc.start()
process = psutil.Process(os.getpid())

# Get baseline
start_time = time.perf_counter()
start_cpu = process.cpu_times()
start_mem = process.memory_info().rss

# Import and run the simulation
sys.path.insert(0, '.')
from core_v2 import ButterflyFx
from core_v2.tests.test_car_trip_simulation import simulate_1_mile_trip

# Suppress print output for clean metrics
import io
old_stdout = sys.stdout
sys.stdout = io.StringIO()

fuel_result, tire_result = simulate_1_mile_trip()

sys.stdout = old_stdout

# Get final measurements
end_time = time.perf_counter()
end_cpu = process.cpu_times()
end_mem = process.memory_info().rss
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

# Calculate
elapsed = end_time - start_time
cpu_user = end_cpu.user - start_cpu.user
cpu_system = end_cpu.system - start_cpu.system
mem_used = end_mem - start_mem

print('=' * 60)
print('RESOURCE USAGE FOR 1-MILE CAR SIMULATION')
print('=' * 60)
print()
print(f'  Execution Time:     {elapsed*1000:.2f} ms ({elapsed:.4f} seconds)')
print()
print(f'  CPU Time (user):    {cpu_user*1000:.2f} ms')
print(f'  CPU Time (system):  {cpu_system*1000:.2f} ms')
print(f'  CPU Time (total):   {(cpu_user+cpu_system)*1000:.2f} ms')
print()
print(f'  Memory (current):   {current/1024:.2f} KB ({current/1024/1024:.2f} MB)')
print(f'  Memory (peak):      {peak/1024:.2f} KB ({peak/1024/1024:.2f} MB)')
print(f'  Memory delta:       {mem_used/1024:.2f} KB')
print()
print(f'  Process RSS:        {end_mem/1024/1024:.2f} MB')
print()
print('=' * 60)
print('SIMULATION RESULTS (recap)')
print('=' * 60)
fuel_ml = fuel_result['total_fuel_L'] * 1000
rubber_mg = tire_result['total_rubber_mass_g'] * 1000
print(f'  Fuel consumed:      {fuel_ml:.2f} mL')
print(f'  Rubber worn:        {rubber_mg:.4f} mg')
print()
