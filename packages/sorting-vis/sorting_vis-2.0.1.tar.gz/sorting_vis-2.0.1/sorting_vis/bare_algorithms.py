from typing import List


class BareAlgorithms:
    @staticmethod
    def bubble_sort(arr: List[int], length: int) -> None:
        for i in range(length):
            for j in range(length - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]

    @staticmethod
    def selection_sort(arr: List[int], length: int) -> None:
        for i in range(length):
            min_index = i
            for j in range(i, length):
                if arr[j] < arr[min_index]:
                    min_index = j
            if min_index != i:
                arr[i], arr[min_index] = arr[min_index], arr[i]

    @staticmethod
    def insertion_sort(arr: List[int], length: int) -> None:
        for i in range(1, length):
            j = i
            while j > 0 and arr[j - 1] > arr[j]:
                arr[j], arr[j - 1] = arr[j - 1], arr[j]
                j -= 1

    @staticmethod
    def merge_sort(arr: List[int], length: int) -> None:
        def merge_sort_recursive(arr, left_index, right_index):
            if left_index >= right_index:
                return None

            mid = (left_index + right_index) // 2
            merge_sort_recursive(arr, left_index, mid)
            merge_sort_recursive(arr, mid + 1, right_index)
            merge(arr, left_index, mid, right_index)

        def merge(arr, left_index, mid, right_index):
            left_copy = arr[left_index : mid + 1]
            right_copy = arr[mid + 1 : right_index + 1]

            left_copy_index = right_copy_index = 0
            sorted_index = left_index

            while left_copy_index < len(left_copy) and right_copy_index < len(
                right_copy
            ):
                if left_copy[left_copy_index] <= right_copy[right_copy_index]:
                    arr[sorted_index] = left_copy[left_copy_index]
                    left_copy_index += 1
                else:
                    arr[sorted_index] = right_copy[right_copy_index]
                    right_copy_index += 1
                sorted_index += 1

            while left_copy_index < len(left_copy):
                arr[sorted_index] = left_copy[left_copy_index]
                left_copy_index += 1
                sorted_index += 1

            while right_copy_index < len(right_copy):
                arr[sorted_index] = right_copy[right_copy_index]
                right_copy_index += 1
                sorted_index += 1

        merge_sort_recursive(arr, 0, length - 1)

    @staticmethod
    def shell_sort(arr: List[int], length: int) -> None:
        gap = length // 2

        while gap > 0:
            for i in range(gap, length):
                temp = arr[i]
                j = i
                while j >= gap and arr[j - gap] > temp:
                    arr[j] = arr[j - gap]
                    j -= gap
                arr[j] = temp

            gap //= 2

    @staticmethod
    def cocktail_shaker_sort(arr: List[int], length: int) -> None:
        start = 0
        end = length - 1

        while start <= end:
            swapped = False

            for i in range(start, end):
                if arr[i] > arr[i + 1]:
                    arr[i], arr[i + 1] = arr[i + 1], arr[i]
                    swapped = True

            if not swapped:
                break

            end -= 1

            swapped = False

            for i in range(end, start, -1):
                if arr[i - 1] > arr[i]:
                    arr[i], arr[i - 1] = arr[i - 1], arr[i]
                    swapped = True

            start += 1

    @staticmethod
    def quick_sort(arr: List[int], length: int) -> None:
        def partition(arr, low, high):
            pivot = arr[high]
            i = low - 1
            for j in range(low, high):
                if arr[j] <= pivot:
                    i += 1
                    arr[i], arr[j] = arr[j], arr[i]

            arr[i + 1], arr[high] = arr[high], arr[i + 1]
            return i + 1

        def quick_sort_recursive(arr, low, high):
            if low < high:
                pi = partition(arr, low, high)
                quick_sort_recursive(arr, low, pi - 1)
                quick_sort_recursive(arr, pi + 1, high)

        quick_sort_recursive(arr, 0, len(arr) - 1)

    @staticmethod
    def heap_sort(arr: List[int], length: int) -> None:
        def heapify(arr, n, i):
            largest = i
            left = 2 * i + 1
            right = 2 * i + 2

            if left < n and arr[i] < arr[left]:
                largest = left

            if right < n and arr[largest] < arr[right]:
                largest = right

            if largest != i:
                arr[i], arr[largest] = arr[largest], arr[i]

                heapify(arr, n, largest)

        for i in range(length // 2 - 1, -1, -1):
            heapify(arr, length, i)

        for i in range(length - 1, 0, -1):
            arr[i], arr[0] = arr[0], arr[i]

            heapify(arr, i, 0)

    @staticmethod
    def radix_sort(arr: List[int], length: int) -> None:
        def counting_sort(arr, exp, n):
            output = [0] * n
            count = [0] * 10

            for i in range(n):
                index = arr[i] // exp
                count[index % 10] += 1

            for i in range(1, 10):
                count[i] += count[i - 1]

            i = n - 1
            while i >= 0:
                index = arr[i] // exp
                output[count[index % 10] - 1] = arr[i]
                count[index % 10] -= 1

                i -= 1

            for i in range(n):
                arr[i] = output[i]

        max_value = max(arr)
        exp = 1

        while max_value // exp > 0:
            counting_sort(arr, exp, length)
            exp *= 10

    @staticmethod
    def gnome_sort(arr: List[int], length: int) -> None:
        index = 0

        while index < length:
            if index == 0:
                index += 1
            if arr[index] >= arr[index - 1]:
                index += 1
            else:
                arr[index], arr[index - 1] = arr[index - 1], arr[index]
                index -= 1

    @staticmethod
    def odd_even_sort(arr: List[int], length: int) -> None:
        is_sorted = False

        while not is_sorted:
            is_sorted = True

            for i in range(1, length - 1, 2):
                if arr[i] > arr[i + 1]:
                    arr[i], arr[i + 1] = arr[i + 1], arr[i]
                    is_sorted = False

            for i in range(0, length - 1, 2):
                if arr[i] > arr[i + 1]:
                    arr[i], arr[i + 1] = arr[i + 1], arr[i]
                    is_sorted = False

    @staticmethod
    def double_selection_sort(arr: List[int], length: int) -> None:
        for i in range(length // 2):
            min_index = i
            max_index = i
            for j in range(i + 1, length - i):
                if arr[j] < arr[min_index]:
                    min_index = j
                if arr[j] > arr[max_index]:
                    max_index = j

            if min_index != i:
                arr[i], arr[min_index] = arr[min_index], arr[i]

            if max_index == i:
                max_index = min_index

            if max_index != length - i - 1:
                arr[length - i - 1], arr[max_index] = (
                    arr[max_index],
                    arr[length - i - 1],
                )

    @staticmethod
    def cycle_sort(arr: List[int], length: int) -> None:
        for cycle_start in range(length - 1):
            item = arr[cycle_start]
            pos = cycle_start
            for i in range(cycle_start + 1, length):
                if arr[i] < item:
                    pos += 1

            if pos == cycle_start:
                continue

            while item == arr[pos]:
                pos += 1

            arr[pos], item = item, arr[pos]

            while pos != cycle_start:
                pos = cycle_start
                for i in range(cycle_start + 1, length):
                    if arr[i] < item:
                        pos += 1

                while item == arr[pos]:
                    pos += 1

                arr[pos], item = item, arr[pos]

    @staticmethod
    def pigeonhole_sort(arr: List[int], length: int) -> None:
        min_value = min(arr)
        max_value = max(arr)
        size = max_value - min_value + 1
        holes = [0] * size

        for num in arr:
            holes[num - min_value] += 1

        index = 0
        for i in range(size):
            while holes[i] > 0:
                arr[index] = i + min_value
                index += 1
                holes[i] -= 1

    @staticmethod
    def comb_sort(arr: List[int], length: int) -> None:
        gap = length
        shrink_factor = 1.3
        swapped = True

        while gap > 1 or swapped:
            gap = int(gap / shrink_factor)
            if gap < 1:
                gap = 1

            swapped = False

            for i in range(len(arr) - gap):
                if arr[i] > arr[i + gap]:
                    arr[i], arr[i + gap] = arr[i + gap], arr[i]
                    swapped = True

    @staticmethod
    def pancake_sort(arr: List[int], length: int) -> None:
        def flip(arr: List[int], k: int) -> None:
            left = 0
            while left < k:
                arr[left], arr[k] = arr[k], arr[left]
                left += 1
                k -= 1

        for size in range(length, 1, -1):
            max_index = arr.index(max(arr[:size]))
            if max_index != size - 1:
                flip(arr, max_index)
                flip(arr, size - 1)
