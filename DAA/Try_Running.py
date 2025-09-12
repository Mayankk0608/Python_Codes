def Inserstion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1

        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
    
        arr[j + 1] = key

if __name__ == "__main__":
    arr = [9,5,4,15,7]
    print(f"Original Array: {arr}")

    Inserstion_sort(arr)
    print(f"\nSorted Array: {arr}")