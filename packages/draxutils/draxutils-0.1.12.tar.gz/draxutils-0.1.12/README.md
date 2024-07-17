Credit to https://www.kaggle.com/code/stassl/displaying-inline-images-in-pandas-dataframe.

Usage example:
```python
from datasets import load_dataset
# Load Fashion MNIST dataset
rows = load_dataset("zalando-datasets/fashion_mnist", split="test")
rows.set_format(type="pandas") # rows is a datasets.Dataset object from Hugging Face
df = rows[:]

from draxutils import show_pd
show_pd(df)

# if there is a column with multiple images, you can specify the column name
# show_pd(df, imglist_key='mycol')
```

```python
# Extended Timer Usage Example

from simple_timer import Timer, timer, time_this, timed
import time

# Example 1: Using start() and end() methods
print("Example 1: start() and end() methods")
timer.start()
time.sleep(1)  # Simulate some work
elapsed = timer.end()
print(f"Elapsed time: {elapsed:.6f} seconds")
print(timer)  # Output the total time

# Example 2: Using lap() method
print("\nExample 2: lap() method")
timer.start()
for i in range(3):
    time.sleep(0.5)  # Simulate some work
    lap_time = timer.lap(f"Lap {i+1}")
    print(f"Lap {i+1} time: {lap_time:.6f} seconds")
total_time = timer.end()
print(f"Total time: {total_time:.6f} seconds")

# Print all laps
for lap_name, _, lap_time in timer.laps:
    print(f"{lap_name}: {lap_time:.6f} seconds")

# Example 3: Using as a context manager
print("\nExample 3: Context Manager")
with Timer() as t:
    time.sleep(0.75)  # Simulate some work
    t.lap("Midpoint")
    time.sleep(0.75)  # More work
print(t)
print(f"Lap time: {t.laps[0][2]:.6f} seconds")

# Example 4: Using as a decorator
print("\nExample 4: Decorator")
@timed
def some_function():
    time.sleep(1)  # Simulate some work

some_function()
print(f"Function execution time: {some_function.elapsed:.6f} seconds")

# Example 5: Multiple timers
print("\nExample 5: Multiple Timers")
timer1 = Timer()
timer2 = Timer()

timer1.start()
time.sleep(0.5)
timer2.start()
time.sleep(0.5)
print(f"Timer 1: {timer1.elapsed:.6f} seconds")
print(f"Timer 2: {timer2.elapsed:.6f} seconds")
timer2.end()
timer1.end()
print(f"Final Timer 1: {timer1}")
print(f"Final Timer 2: {timer2}")
```