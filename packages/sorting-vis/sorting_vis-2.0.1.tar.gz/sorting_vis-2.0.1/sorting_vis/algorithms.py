from random import shuffle
from tkinter import messagebox
from typing import List


class Algorithms:
    def __init__(self, master: object) -> None:
        self.master = master
        self.paused = False
        self.paused_arr = []
        self.arr_length = self.master.arr_length

    def _on_finish(self, arr):
        flag = True
        if self.render_checking_complete:
            self.master.b_toggle_sort.configure(state="disabled")
            if not self.master._render_checking_complete(arr):
                flag = False
        else:
            self.master._render_arr(arr, complete=True)
        if flag:
            messagebox.showinfo(
                "Info",
                f"{self.master.algorithm} took {self.master.sorting_time}{'s' if self.master.parsed_algorithm != 'bogo_sort' else ''}",
            )

    def bubble_sort(self, arr: List[int]) -> None:
        for i in range(self.arr_length):
            for j in range(self.arr_length - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    if self.paused:
                        self.paused_arr = arr.copy()
                        return "pause"
                    self.master._render_arr(arr, [j, j + 1])

        self._on_finish(arr)

    def selection_sort(self, arr: List[int]) -> None:
        for i in range(self.arr_length):
            min_index = i
            for j in range(i, self.arr_length):
                if arr[j] < arr[min_index]:
                    min_index = j
            if min_index != i:
                arr[i], arr[min_index] = arr[min_index], arr[i]
                if self.paused:
                    self.paused_arr = arr.copy()
                    return "pause"
                self.master._render_arr(arr, [i, min_index])

        self._on_finish(arr)

    def insertion_sort(self, arr: List[int]) -> None:
        for i in range(1, self.arr_length):
            j = i
            while j > 0 and arr[j - 1] > arr[j]:
                arr[j], arr[j - 1] = arr[j - 1], arr[j]
                if self.paused:
                    self.paused_arr = arr.copy()
                    return "pause"
                self.master._render_arr(arr, [j, j - 1])
                j -= 1

        self._on_finish(arr)

    def merge_sort(self, arr: List[int]) -> None:
        def merge_sort_recursive(arr, left_index, right_index):
            if left_index >= right_index:
                return None

            mid = (left_index + right_index) // 2
            if merge_sort_recursive(arr, left_index, mid) == "pause":
                return "pause"
            if merge_sort_recursive(arr, mid + 1, right_index) == "pause":
                return "pause"
            if merge(arr, left_index, mid, right_index) == "pause":
                return "pause"
            return None

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

                if self.paused:
                    self.paused_arr = arr.copy()
                    return "pause"
                self.master._render_arr(arr, [sorted_index])

            while left_copy_index < len(left_copy):
                arr[sorted_index] = left_copy[left_copy_index]
                left_copy_index += 1
                sorted_index += 1
                if self.paused:
                    self.paused_arr = arr.copy()
                    return "pause"
                self.master._render_arr(arr, [sorted_index])

            while right_copy_index < len(right_copy):
                arr[sorted_index] = right_copy[right_copy_index]
                right_copy_index += 1
                sorted_index += 1
                if self.paused:
                    self.paused_arr = arr.copy()
                    return "pause"
                self.master._render_arr(arr, [sorted_index])
            return None

        if merge_sort_recursive(arr, 0, self.arr_length - 1) != "pause":
            self._on_finish(arr)
        else:
            return "pause"

    def shell_sort(self, arr: List[int]) -> None:
        gap = self.arr_length // 2

        while gap > 0:
            for i in range(gap, self.arr_length):
                temp = arr[i]
                j = i
                while j >= gap and arr[j - gap] > temp:
                    arr[j] = arr[j - gap]
                    j -= gap

                    if self.paused:
                        self.paused_arr = arr.copy()
                        return "pause"
                    self.master._render_arr(arr, [j, j - gap])

                arr[j] = temp
                if self.paused:
                    self.paused_arr = arr.copy()
                    return "pause"
                self.master._render_arr(arr, [j, i])

            gap //= 2

        self._on_finish(arr)

    def cocktail_shaker_sort(self, arr: List[int]) -> None:
        start = 0
        end = self.arr_length - 1

        while start <= end:
            swapped = False

            for i in range(start, end):
                if arr[i] > arr[i + 1]:
                    arr[i], arr[i + 1] = arr[i + 1], arr[i]
                    swapped = True
                self.master._render_arr(arr, [i, i + 1])
                if self.paused:
                    self.paused_arr = arr.copy()
                    return "pause"

            if not swapped:
                break

            end -= 1

            swapped = False

            for i in range(end, start, -1):
                if arr[i - 1] > arr[i]:
                    arr[i], arr[i - 1] = arr[i - 1], arr[i]
                    swapped = True
                self.master._render_arr(arr, [i - 1, i])
                if self.paused:
                    self.paused_arr = arr.copy()
                    return "pause"

            start += 1

        self._on_finish(arr)

    def quick_sort(self, arr: List[int]) -> None:
        def partition(arr, low, high):
            pivot = arr[high]
            i = low - 1
            for j in range(low, high):
                if arr[j] <= pivot:
                    i += 1
                    arr[i], arr[j] = arr[j], arr[i]
                    self.master._render_arr(arr, [i, j])
                    if self.paused:
                        self.paused_arr = arr.copy()
                        return "pause"
            arr[i + 1], arr[high] = arr[high], arr[i + 1]
            self.master._render_arr(arr, [i + 1, high])
            return i + 1

        def quick_sort_recursive(arr, low, high):
            if low < high:
                pi = partition(arr, low, high)
                if pi == "pause":
                    return "pause"
                if quick_sort_recursive(arr, low, pi - 1) == "pause":
                    return "pause"
                if quick_sort_recursive(arr, pi + 1, high) == "pause":
                    return "pause"

        if quick_sort_recursive(arr, 0, len(arr) - 1) is None:
            self._on_finish(arr)
        else:
            return "pause"

    def heap_sort(self, arr: List[int]) -> None:
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
                if self.paused:
                    self.paused_arr = arr.copy()
                    return "pause"
                self.master._render_arr(arr, [i, largest])

                heapify(arr, n, largest)

        for i in range(self.arr_length // 2 - 1, -1, -1):
            heapify(arr, self.arr_length, i)

        for i in range(self.arr_length - 1, 0, -1):
            arr[i], arr[0] = arr[0], arr[i]
            if self.paused:
                self.paused_arr = arr.copy()
                return "pause"
            self.master._render_arr(arr, [i, 0])

            heapify(arr, i, 0)

        self._on_finish(arr)

    def radix_sort(self, arr: List[int]) -> None:
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
                if self.paused:
                    self.paused_arr = arr.copy()
                    return "pause"
                self.master._render_arr(output, [count[index % 10]])

                i -= 1

            for i in range(n):
                arr[i] = output[i]

        max_value = max(arr)
        exp = 1

        while max_value // exp > 0:
            if counting_sort(arr, exp, self.arr_length) is None:
                exp *= 10
            else:
                return "pause"

        self._on_finish(arr)

    def gnome_sort(self, arr: List[int]) -> None:
        index = 0

        while index < self.arr_length:
            if index == 0:
                index += 1
            if arr[index] >= arr[index - 1]:
                index += 1
            else:
                arr[index], arr[index - 1] = arr[index - 1], arr[index]
                index -= 1

                if self.paused:
                    self.paused_arr = arr.copy()
                    return "pause"
                self.master._render_arr(arr, [index, index + 1])

        self._on_finish(arr)

    def odd_even_sort(self, arr: List[int]) -> None:
        is_sorted = False

        while not is_sorted:
            is_sorted = True

            for i in range(1, self.arr_length - 1, 2):
                if arr[i] > arr[i + 1]:
                    arr[i], arr[i + 1] = arr[i + 1], arr[i]
                    is_sorted = False
                    if self.paused:
                        self.paused_arr = arr.copy()
                        return "pause"
                    self.master._render_arr(arr, [i, i + 1])

            for i in range(0, self.arr_length - 1, 2):
                if arr[i] > arr[i + 1]:
                    arr[i], arr[i + 1] = arr[i + 1], arr[i]
                    is_sorted = False
                    if self.paused:
                        self.paused_arr = arr.copy()
                        return "pause"
                    self.master._render_arr(arr, [i, i + 1])

        self._on_finish(arr)

    def double_selection_sort(self, arr: List[int]) -> None:
        for i in range(self.arr_length // 2):
            min_index = i
            max_index = i
            for j in range(i + 1, self.arr_length - i):
                if arr[j] < arr[min_index]:
                    min_index = j
                if arr[j] > arr[max_index]:
                    max_index = j

            if min_index != i:
                arr[i], arr[min_index] = arr[min_index], arr[i]
                self.master._render_arr(arr, [i, min_index])
                if self.paused:
                    self.paused_arr = arr.copy()
                    return "pause"

            if max_index == i:
                max_index = min_index

            if max_index != self.arr_length - i - 1:
                arr[self.arr_length - i - 1], arr[max_index] = (
                    arr[max_index],
                    arr[self.arr_length - i - 1],
                )
                self.master._render_arr(
                    arr, [self.arr_length - i - 1, max_index]
                )
                if self.paused:
                    self.paused_arr = arr.copy()
                    return "pause"

        self._on_finish(arr)

    def cycle_sort(self, arr: List[int]) -> None:
        for cycle_start in range(self.arr_length - 1):
            item = arr[cycle_start]
            pos = cycle_start
            for i in range(cycle_start + 1, self.arr_length):
                if arr[i] < item:
                    pos += 1

            if pos == cycle_start:
                continue

            while item == arr[pos]:
                pos += 1

            arr[pos], item = item, arr[pos]
            self.master._render_arr(arr, [pos])
            if self.paused:
                self.paused_arr = arr.copy()
                return "pause"

            while pos != cycle_start:
                pos = cycle_start
                for i in range(cycle_start + 1, self.arr_length):
                    if arr[i] < item:
                        pos += 1

                while item == arr[pos]:
                    pos += 1

                arr[pos], item = item, arr[pos]
                self.master._render_arr(arr, [pos])
                if self.paused:
                    self.paused_arr = arr.copy()
                    return "pause"

        self._on_finish(arr)

    def pigeonhole_sort(self, arr: List[int]) -> None:
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
                self.master._render_arr(arr, [i, index])
                if self.paused:
                    self.paused_arr = arr.copy()
                    return "pause"

        self._on_finish(arr)

    def comb_sort(self, arr: List[int]) -> None:
        gap = self.arr_length
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
                    self.master._render_arr(arr, [i, i + gap])
                    if self.paused:
                        self.paused_arr = arr.copy()
                        return "pause"

        self._on_finish(arr)

    def pancake_sort(self, arr: List[int]) -> None:
        def flip(arr: List[int], k: int) -> None:
            left = 0
            while left < k:
                arr[left], arr[k] = arr[k], arr[left]
                left += 1
                k -= 1

        for size in range(self.arr_length, 1, -1):
            max_index = arr.index(max(arr[:size]))
            if max_index != size - 1:
                flip(arr, max_index)
                flip(arr, size - 1)
                self.master._render_arr(arr, [max_index, size - 1])
                if self.paused:
                    self.paused_arr = arr.copy()
                    return "pause"

        self._on_finish(arr)

    def bogo_sort(self, arr: List[int]) -> None:
        while not all(
            arr[i] <= arr[i + 1] for i in range(self.arr_length - 1)
        ):
            shuffle(arr)
            if self.paused:
                self.paused_arr = arr.copy()
                return "pause"
            self.master._render_arr(arr)

        self._on_finish(arr)
