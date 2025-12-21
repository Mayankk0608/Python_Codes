import time
import random
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

class SortingAlgorithms:
    # SHELL SORT
    def shell_sort(self, arr):
        n = len(arr)
        gap = n // 2
        
        while gap > 0:
            for i in range(gap, n):
                temp = arr[i]
                j = i
                while j >= gap and arr[j - gap] > temp:
                    arr[j] = arr[j - gap]
                    j -= gap
                arr[j] = temp
            gap //= 2
        return arr
    
    # QUICK SORT
    def quick_sort(self, arr):
        if len(arr) <= 1:
            return arr
        
        pivot = arr[len(arr) // 2]
        left = [x for x in arr if x < pivot]
        middle = [x for x in arr if x == pivot]
        right = [x for x in arr if x > pivot]
        
        return self.quick_sort(left) + middle + self.quick_sort(right)
    
    def quick_sort_inplace(self, arr, low=0, high=None):
        if high is None:
            high = len(arr) - 1
        
        def partition(arr, low, high):
            pivot = arr[high]
            i = low - 1
            
            for j in range(low, high):
                if arr[j] <= pivot:
                    i += 1
                    arr[i], arr[j] = arr[j], arr[i]
            
            arr[i + 1], arr[high] = arr[high], arr[i + 1]
            return i + 1
        
        if low < high:
            pi = partition(arr, low, high)
            self.quick_sort_inplace(arr, low, pi - 1)
            self.quick_sort_inplace(arr, pi + 1, high)
        return arr
    
    # MERGE SORT
    def merge_sort(self, arr):
        if len(arr) <= 1:
            return arr
        
        mid = len(arr) // 2
        left = self.merge_sort(arr[:mid])
        right = self.merge_sort(arr[mid:])
        
        return self.merge(left, right)
    
    def merge(self, left, right):
        result = []
        i = j = 0
        
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        
        result.extend(left[i:])
        result.extend(right[j:])
        return result
    
    # HEAP SORT
    def heap_sort(self, arr):
        n = len(arr)
        
        # Build max heap
        for i in range(n // 2 - 1, -1, -1):
            self.heapify(arr, n, i)
        
        # Extract elements from heap
        for i in range(n - 1, 0, -1):
            arr[i], arr[0] = arr[0], arr[i]  # swap
            self.heapify(arr, i, 0)
        
        return arr
    
    def heapify(self, arr, n, i):
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2
        
        if left < n and arr[left] > arr[largest]:
            largest = left
        
        if right < n and arr[right] > arr[largest]:
            largest = right
        
        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            self.heapify(arr, n, largest)
    
    # LINEAR TIME SORTING - COUNTING SORT
    def counting_sort(self, arr):
        if not arr:
            return arr
        
        max_val = max(arr)
        min_val = min(arr)
        
        # Create count array
        count = [0] * (max_val - min_val + 1)
        
        # Store count of each element
        for num in arr:
            count[num - min_val] += 1
        
        # Build output array
        result = []
        for i in range(len(count)):
            result.extend([i + min_val] * count[i])
        
        return result
    
    # LINEAR TIME SORTING - RADIX SORT
    def radix_sort(self, arr):
        if not arr:
            return arr
        
        # Find maximum number to know number of digits
        max_num = max(arr)
        
        # Do counting sort for every digit
        exp = 1
        while max_num // exp > 0:
            self.counting_sort_for_radix(arr, exp)
            exp *= 10
        return arr
    
    def counting_sort_for_radix(self, arr, exp):
        n = len(arr)
        output = [0] * n
        count = [0] * 10
        
        # Store count of occurrences
        for i in range(n):
            index = (arr[i] // exp) % 10
            count[index] += 1
        
        # Change count[i] so it contains actual position
        for i in range(1, 10):
            count[i] += count[i - 1]
        
        # Build output array
        i = n - 1
        while i >= 0:
            index = (arr[i] // exp) % 10
            output[count[index] - 1] = arr[i]
            count[index] -= 1
            i -= 1
        
        # Copy output to arr
        for i in range(n):
            arr[i] = output[i]

class SortingComparison:
    def __init__(self):
        self.algorithms = SortingAlgorithms()
        self.time_complexities = {
            'Shell Sort': {'Best': 'O(n log n)', 'Average': 'O(n^(3/2))', 'Worst': 'O(n^2)'},
            'Quick Sort': {'Best': 'O(n log n)', 'Average': 'O(n log n)', 'Worst': 'O(n^2)'},
            'Merge Sort': {'Best': 'O(n log n)', 'Average': 'O(n log n)', 'Worst': 'O(n log n)'},
            'Heap Sort': {'Best': 'O(n log n)', 'Average': 'O(n log n)', 'Worst': 'O(n log n)'},
            'Counting Sort': {'Best': 'O(n + k)', 'Average': 'O(n + k)', 'Worst': 'O(n + k)'},
            'Radix Sort': {'Best': 'O(nk)', 'Average': 'O(nk)', 'Worst': 'O(nk)'}
        }
    
    def generate_test_cases(self, size=1000):
        """Generate different types of test arrays"""
        random_arr = [random.randint(0, size) for _ in range(size)]
        sorted_arr = sorted(random_arr)
        reverse_arr = sorted_arr[::-1]
        nearly_sorted = sorted_arr.copy()
        # Swap some elements to make it nearly sorted
        for _ in range(size // 20):  # 5% swaps
            i, j = random.randint(0, size-1), random.randint(0, size-1)
            nearly_sorted[i], nearly_sorted[j] = nearly_sorted[j], nearly_sorted[i]
        
        return {
            'Random': random_arr,
            'Sorted': sorted_arr,
            'Reverse': reverse_arr,
            'Nearly Sorted': nearly_sorted
        }
    
    def time_algorithm(self, algorithm, arr):
        """Time a sorting algorithm"""
        start_time = time.time()
        
        if algorithm == 'Shell Sort':
            self.algorithms.shell_sort(arr.copy())
        elif algorithm == 'Quick Sort':
            self.algorithms.quick_sort(arr.copy())
        elif algorithm == 'Merge Sort':
            self.algorithms.merge_sort(arr.copy())
        elif algorithm == 'Heap Sort':
            self.algorithms.heap_sort(arr.copy())
        elif algorithm == 'Counting Sort':
            self.algorithms.counting_sort(arr.copy())
        elif algorithm == 'Radix Sort':
            self.algorithms.radix_sort(arr.copy())
        
        return time.time() - start_time
    
    def compare_algorithms(self, sizes=[100, 500, 1000, 2000]):
        """Compare algorithms across different sizes"""
        results = defaultdict(lambda: defaultdict(list))
        algorithms = ['Shell Sort', 'Quick Sort', 'Merge Sort', 'Heap Sort']
        
        for size in sizes:
            test_cases = self.generate_test_cases(size)
            
            for case_name, arr in test_cases.items():
                for algo in algorithms:
                    time_taken = self.time_algorithm(algo, arr)
                    results[algo][case_name].append(time_taken)
                    results[algo]['Size'].append(size)
        
        return results
    
    def print_time_complexities(self):
        """Print time complexities of all algorithms"""
        print("TIME COMPLEXITIES OF SORTING ALGORITHMS")
        print("=" * 60)
        print(f"{'Algorithm':<15} {'Best Case':<15} {'Average Case':<15} {'Worst Case':<15}")
        print("-" * 60)
        
        for algo, complexities in self.time_complexities.items():
            print(f"{algo:<15} {complexities['Best']:<15} {complexities['Average']:<15} {complexities['Worst']:<15}")
        print()
    
    def plot_comparison(self, results):
        """Plot comparison of algorithms"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        axes = axes.flatten()
        
        test_cases = ['Random', 'Sorted', 'Reverse', 'Nearly Sorted']
        colors = ['red', 'blue', 'green', 'orange', 'purple']
        
        for idx, case in enumerate(test_cases):
            ax = axes[idx]
            for i, (algo, data) in enumerate(results.items()):
                if case in data:
                    sizes = list(set(data['Size']))
                    times = [data[case][data['Size'].index(size)] for size in sizes]
                    ax.plot(sizes, times, marker='o', label=algo, color=colors[i])
            
            ax.set_title(f'Performance on {case} Arrays')
            ax.set_xlabel('Array Size')
            ax.set_ylabel('Time (seconds)')
            ax.legend()
            ax.grid(True)
        
        plt.tight_layout()
        plt.show()

def demo_sorting_algorithms():
    """Demonstrate all sorting algorithms"""
    sorter = SortingAlgorithms()
    comparator = SortingComparison()
    
    # Test array
    test_array = [64, 34, 25, 12, 22, 11, 90, 88, 76, 50, 42, 33, 21, 19, 8, 5]
    print("Original Array:", test_array)
    print("\n" + "="*50 + "\n")
    
    # Test each algorithm
    algorithms = [
        ('Shell Sort', sorter.shell_sort),
        ('Quick Sort', sorter.quick_sort),
        ('Merge Sort', sorter.merge_sort),
        ('Heap Sort', sorter.heap_sort),
        ('Counting Sort', sorter.counting_sort),
        ('Radix Sort', sorter.radix_sort)
    ]
    
    for name, algorithm in algorithms:
        arr_copy = test_array.copy()
        sorted_arr = algorithm(arr_copy)
        print(f"{name}: {sorted_arr}")
    
    print("\n" + "="*50 + "\n")
    
    # Print time complexities
    comparator.print_time_complexities()
    
    # Performance comparison
    print("PERFORMANCE COMPARISON")
    print("=" * 40)
    
    test_cases = comparator.generate_test_cases(1000)
    algorithms_to_test = ['Shell Sort', 'Quick Sort', 'Merge Sort', 'Heap Sort']
    
    for case_name, arr in test_cases.items():
        print(f"\n{case_name} Array (1000 elements):")
        print("-" * 30)
        
        for algo in algorithms_to_test:
            time_taken = comparator.time_algorithm(algo, arr)
            print(f"{algo:<12}: {time_taken:.6f} seconds")
    
    # Linear time sorting demonstration
    print("\n" + "="*50)
    print("LINEAR TIME SORTING DEMONSTRATION")
    print("="*50)
    
    large_array = [random.randint(0, 1000) for _ in range(5000)]
    print(f"Large array size: {len(large_array)}")
    
    # Test counting sort (good for limited range)
    counting_time = comparator.time_algorithm('Counting Sort', large_array)
    print(f"Counting Sort time: {counting_time:.6f} seconds")
    
    # Test radix sort
    radix_time = comparator.time_algorithm('Radix Sort', large_array)
    print(f"Radix Sort time: {radix_time:.6f} seconds")
    
    # Compare with traditional O(n log n) sorts
    quick_time = comparator.time_algorithm('Quick Sort', large_array)
    print(f"Quick Sort time: {quick_time:.6f} seconds")

if __name__ == "__main__":
    demo_sorting_algorithms()
    
    # Uncomment to run comprehensive comparison with plots
    # comparator = SortingComparison()
    # results = comparator.compare_algorithms()
    # comparator.plot_comparison(results)