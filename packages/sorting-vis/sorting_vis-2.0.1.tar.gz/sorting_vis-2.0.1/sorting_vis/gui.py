"""A customtkinter gui that utilises various sorting algorithms to visualise
how an array is sorted
"""

from configparser import ConfigParser
from os import path
from random import randint
from time import time
from tkinter import BOTH, END, Canvas, messagebox
from typing import List

from customtkinter import (
    CTk,
    CTkButton,
    CTkEntry,
    CTkFont,
    CTkFrame,
    CTkImage,
    CTkLabel,
    CTkOptionMenu,
    CTkSegmentedButton,
    CTkToplevel,
    set_appearance_mode,
    set_default_color_theme,
    set_widget_scaling,
)
from PIL import Image

from sorting_vis.constants import (
    ASSETS_PATH,
    AVAILABLE_SORTING_FUNCTIONS,
    CONFIG_PATH,
    LOWER_SAMPLE_BOUND_PLACEHOLDER,
    MAXIMUM_ARRAY_SAMPLES,
    MAXIMUM_ARRAY_VALUE,
    MINIMUM_ARRAY_SAMPLES,
    MINIMUM_ARRAY_VALUE,
    SAMPLE_COUNT_PLACEHOLDER,
    UPPER_SAMPLE_BOUND_PLACEHOLDER,
)

cfg = ConfigParser()


class Home(CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Sorting Algorithm Visualisation")
        self.protocol("WM_DELETE_WINDOW", self._handle_exit)
        self.geometry("500x500")
        self.minsize(500, 500)
        set_widget_scaling(0.9)
        set_default_color_theme(ASSETS_PATH / "TrojanBlue.json")
        set_appearance_mode("dark")

        self.default_font = CTkFont(family="Courier New")
        self.title_font = CTkFont(family="Courier New", size=25, weight="bold")
        self.large_button_font = CTkFont(family="Courier New", size=20)
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.validate_command = self.register(Home._validate_entry)

        self._make_content()
        self._place_content()
        self._update_entries_from_cfg_data()

    @staticmethod
    def _update_config(cfg, sec, opt, val):
        cfg.read(CONFIG_PATH)
        cfg[sec][opt] = str(val)

        with open(CONFIG_PATH, "w") as f:
            cfg.write(f)

    def _update_entries_from_cfg_data(self):
        entries = [
            cfg.get("main", "lsb"),
            cfg.get("main", "usb"),
            cfg.get("main", "sc"),
        ]
        for i in range(len(entries)):
            val = int(entries[i])
            if not val:
                continue
            if i == 0:
                self.e_lower_bound.insert(0, val)
            elif i == 1:
                self.e_upper_bound.insert(0, val)
            else:
                self.e_sample_count.insert(0, val)

    @staticmethod
    def _validate_entry(txt: str) -> bool:
        if (
            txt.isdigit()
            or not txt
            or any(
                txt == placeholder
                for placeholder in [
                    LOWER_SAMPLE_BOUND_PLACEHOLDER,
                    UPPER_SAMPLE_BOUND_PLACEHOLDER,
                    SAMPLE_COUNT_PLACEHOLDER,
                ]
            )
        ):
            return True
        return False

    def _handle_exit(self) -> None:
        if hasattr(self, "array_visualiser"):
            self.array_visualiser.sorter.paused = True
        self.destroy()

    def _make_content(self) -> None:
        self.l_title = CTkLabel(
            self,
            text="Sorting Algorithm Visualisation",
            font=self.title_font,
        )
        self.img_sorting = CTkLabel(
            self,
            text="",
            image=CTkImage(
                Image.open(path.join(ASSETS_PATH, "sorting_vis.png")),
                size=(300, 150),
            ),
        )
        self.img_bluemoji_1 = CTkLabel(
            self,
            text="",
            image=CTkImage(
                Image.open(path.join(ASSETS_PATH, "gasp.png")), size=(100, 100)
            ),
        )
        self.img_bluemoji_2 = CTkLabel(
            self,
            text="",
            image=CTkImage(
                Image.open(path.join(ASSETS_PATH, "thumbs_up.png")),
                size=(100, 100),
            ),
        )

        self.opts_algorithm = CTkOptionMenu(
            self,
            values=[
                " ".join(func.split("_")).title()
                for func in AVAILABLE_SORTING_FUNCTIONS
            ],
            font=self.default_font,
            command=lambda algo: self._update_config(
                cfg, "main", "algo", algo.replace(" ", "_")
            ),
        )
        cfg.read(CONFIG_PATH)
        self.opts_algorithm.set(cfg.get("main", "algo").replace("_", " "))
        self.l_algorithm = CTkLabel(
            self, text="Algorithm", font=self.default_font
        )

        self.e_lower_bound = CTkEntry(
            self,
            font=self.default_font,
            placeholder_text=LOWER_SAMPLE_BOUND_PLACEHOLDER,
            validate="key",
            validatecommand=(self.validate_command, "%P"),
        )
        self.e_lower_bound.bind(
            "<KeyRelease>",
            lambda _: Home._update_config(
                cfg, "main", "lsb", self.e_lower_bound.get()
            ),
        )

        self.e_upper_bound = CTkEntry(
            self,
            font=self.default_font,
            placeholder_text=UPPER_SAMPLE_BOUND_PLACEHOLDER,
            validate="key",
            validatecommand=(self.validate_command, "%P"),
        )
        self.e_upper_bound.bind(
            "<KeyRelease>",
            lambda _: Home._update_config(
                cfg, "main", "usb", self.e_upper_bound.get()
            ),
        )

        self.l_lower_bound = CTkLabel(
            self, text="Variance (lower bound)", font=self.default_font
        )
        self.l_upper_bound = CTkLabel(
            self, text="Variance (upper bound)", font=self.default_font
        )
        self.e_sample_count = CTkEntry(
            self,
            font=self.default_font,
            placeholder_text=SAMPLE_COUNT_PLACEHOLDER,
            validate="key",
            validatecommand=(self.validate_command, "%P"),
        )
        self.e_sample_count.bind(
            "<KeyRelease>",
            lambda _: Home._update_config(
                cfg, "main", "sc", self.e_sample_count.get()
            ),
        )

        self.l_sample_count = CTkLabel(
            self, text="Sample Count", font=self.default_font
        )
        self.b_randomly_fill_entries = CTkButton(
            self,
            text="Random 🎲",
            font=self.default_font,
            command=self._randomly_fill_entries,
            width=145,
        )
        self.b_clear_entries = CTkButton(
            self,
            text="Clear 🔥",
            font=self.default_font,
            command=self._clear_entries,
            width=145,
        )
        self.b_fill_max = CTkButton(
            self,
            font=self.default_font,
            text="Max ↑",
            command=self._fill_max_entries,
            width=145,
        )

        self.b_open_sorter = CTkButton(
            self,
            text="Open 📖",
            font=self.default_font,
            command=self._init_array_visualiser,
            width=145,
            fg_color="#156b2c",
        )

    def _place_content(self) -> None:
        self.l_title.place(relx=0.5, rely=0.415, anchor="c")
        self.img_sorting.place(relx=0.5, rely=0.1925, anchor="c")
        self.img_bluemoji_1.place(relx=0.115, rely=0.1925, anchor="c")
        self.img_bluemoji_2.place(relx=0.885, rely=0.1925, anchor="c")
        self.opts_algorithm.place(relx=0.3, rely=0.58, anchor="c")
        self.l_algorithm.place(relx=0.3, rely=0.53, anchor="c")
        self.e_lower_bound.place(relx=0.7, rely=0.58, anchor="c")
        self.e_upper_bound.place(relx=0.7, rely=0.705, anchor="c")
        self.l_lower_bound.place(relx=0.7, rely=0.53, anchor="c")
        self.l_upper_bound.place(relx=0.7, rely=0.655, anchor="c")
        self.e_sample_count.place(relx=0.3, rely=0.705, anchor="c")
        self.l_sample_count.place(relx=0.3, rely=0.655, anchor="c")
        self.b_open_sorter.place(relx=0.7, rely=0.905, anchor="c")
        self.b_randomly_fill_entries.place(relx=0.3, rely=0.805, anchor="c")
        self.b_clear_entries.place(relx=0.7, rely=0.805, anchor="c")
        self.b_fill_max.place(relx=0.3, rely=0.905, anchor="c")

    def _verify_entries(self) -> bool:
        try:
            self.lower_input = int(self.e_lower_bound.get())
            self.upper_input = int(self.e_upper_bound.get())
            self.sample_count_input = int(self.e_sample_count.get())
        except ValueError:
            messagebox.showerror("Error", "Entries have non-integer inputs.")
            return False

        if (
            self.lower_input < MINIMUM_ARRAY_VALUE
            or self.upper_input > MAXIMUM_ARRAY_VALUE
            or self.lower_input >= self.upper_input
            or self.sample_count_input > MAXIMUM_ARRAY_SAMPLES
            or self.sample_count_input < MINIMUM_ARRAY_SAMPLES
        ):
            messagebox.showerror(
                "Error",
                "Entries must contain integers within bounds.",
            )
            return False
        else:
            return True

    def _init_array_visualiser(self) -> None:
        if self._verify_entries():
            if hasattr(self, "array_visualiser"):
                return messagebox.showerror(
                    "Error", "You can only have one sorting instance open."
                )
            self.array_visualiser = ArrayVisualiser(
                self,
                self.lower_input,
                self.upper_input,
                self.sample_count_input,
                self.opts_algorithm.get(),
            )
            return

    def _clear_entries(self) -> None:
        self.e_lower_bound.delete(0, END)
        self.e_upper_bound.delete(0, END)
        self.e_sample_count.delete(0, END)
        self.e_lower_bound.focus()
        self.e_upper_bound.focus()
        self.e_sample_count.focus()
        self.focus()
        for sec in ["lsb", "usb", "sc"]:
            Home._update_config(cfg, "main", sec, "0")

    def _randomly_fill_entries(self) -> None:
        self._clear_entries()
        self.e_lower_bound.insert(
            0, f"{randint(MINIMUM_ARRAY_VALUE, int(MAXIMUM_ARRAY_VALUE / 2))}"
        )
        self.e_upper_bound.insert(
            0,
            f"{randint(int(self.e_lower_bound.get()) + 1, MAXIMUM_ARRAY_VALUE)}",
        )
        self.e_sample_count.insert(
            0, f"{randint(MINIMUM_ARRAY_SAMPLES, MAXIMUM_ARRAY_SAMPLES)}"
        )
        Home._update_config(cfg, "main", "lsb", self.e_lower_bound.get())
        Home._update_config(cfg, "main", "usb", self.e_upper_bound.get())
        Home._update_config(cfg, "main", "sc", self.e_sample_count.get())

    def _fill_max_entries(self) -> None:
        self._clear_entries()
        self.e_lower_bound.insert(0, MINIMUM_ARRAY_VALUE)
        self.e_upper_bound.insert(0, MAXIMUM_ARRAY_VALUE)
        self.e_sample_count.insert(0, MAXIMUM_ARRAY_SAMPLES)
        Home._update_config(cfg, "main", "lsb", MINIMUM_ARRAY_VALUE)
        Home._update_config(cfg, "main", "usb", MAXIMUM_ARRAY_VALUE)
        Home._update_config(cfg, "main", "sc", MAXIMUM_ARRAY_SAMPLES)


class ArrayVisualiser(CTkToplevel):
    def __init__(
        self,
        master: Home,
        lowerbound: int,
        upperbound: int,
        samplecount: int,
        algorithm: str,
    ) -> None:
        super().__init__(master)

        self.attributes("-fullscreen", True)
        self.title(algorithm)
        self.protocol("WM_DELETE_WINDOW", self._handle_exit)
        self.geometry(
            f"{self.master.screen_width}x{self.master.screen_height}"
        )
        set_widget_scaling(0.9)

        self.master = master
        self.lowerbound = lowerbound
        self.upperbound = upperbound
        self.samplecount = samplecount
        self.algorithm = algorithm
        self.parsed_algorithm = "_".join(self.algorithm.casefold().split(" "))

        self._make_content()
        self._place_content()
        self._init_arr()

        from sorting_vis.algorithms import Algorithms

        self.sorter = Algorithms(self)
        cfg.read(CONFIG_PATH)
        setattr(
            self.sorter,
            "render_checking_complete",
            bool(int(cfg.get("main", "check"))),
        )
        self.currently_sorting = False

    def _handle_exit(self) -> None:
        if self.currently_sorting:
            self.b_toggle_sort.invoke()
        self.master.after(10, self.destroy)
        del self.master.array_visualiser

    def _make_content(self) -> None:
        self.frame = CTkFrame(self)
        self.b_init_sort = CTkButton(
            self.frame,
            text="Start",
            command=lambda: self._init_sort(self.arr),
            state="disabled",
            font=self.master.large_button_font,
        )
        self.b_new_arr = CTkButton(
            self.frame,
            text="New",
            command=self._init_arr,
            font=self.master.large_button_font,
        )
        self.b_toggle_sort = CTkButton(
            self.frame,
            text="Pause",
            font=self.master.large_button_font,
            state="disabled",
            command=self._toggle_sort,
        )
        self.b_exit = CTkButton(
            self.frame,
            text="Exit",
            font=self.master.large_button_font,
            command=self._handle_exit,
            fg_color="#ED3B4D",
            hover_color="#590911",
        )
        self.l_checking = CTkLabel(
            self, font=self.master.default_font, text="Checking Animation"
        )
        self.sb_toggle_checking = CTkSegmentedButton(
            self,
            font=self.master.large_button_font,
            values=["On", "Off"],
            command=self._toggle_checking,
        )
        self.sb_toggle_checking.set(
            {"0": "Off", "1": "On"}[cfg.get("main", "check")]
        )
        for button in self.sb_toggle_checking._buttons_dict.values():
            button.configure(width=self.master.winfo_screenwidth() * 0.09 / 2)

        self.arr_canvas = Canvas(
            self.frame,
            width=self.master.screen_width - 60,
            height=self.master.screen_height * 0.9 - 60,
            background="#2d4485",
        )
        self.canvas_width = self.arr_canvas.winfo_reqwidth() - 10
        self.canvas_height = self.arr_canvas.winfo_reqheight() - 21

    def _place_content(self):
        self.frame.pack(fill=BOTH, expand=True)
        self.l_checking.place(relx=0.30, rely=0.9, anchor="c")
        self.sb_toggle_checking.place(
            relx=0.30, rely=0.93725, relheight=0.05, relwidth=0.09, anchor="c"
        )
        self.b_init_sort.place(
            relx=0.40, rely=0.93725, relheight=0.05, relwidth=0.09, anchor="c"
        )
        self.b_new_arr.place(
            relx=0.50, rely=0.93725, relheight=0.05, relwidth=0.09, anchor="c"
        )
        self.b_toggle_sort.place(
            relx=0.60, rely=0.93725, relheight=0.05, relwidth=0.09, anchor="c"
        )
        self.b_exit.place(
            relx=0.70, rely=0.93725, relheight=0.05, relwidth=0.09, anchor="c"
        )
        self.arr_canvas.pack(padx=30, pady=(30, 78))

    def _toggle_checking(self, choice) -> None:
        if choice == "On":
            val = 1
        else:
            val = 0
        Home._update_config(cfg, "main", "check", val)
        setattr(self.sorter, "render_checking_complete", val)

    def _estimate_sorting_time(self) -> None:
        if self.parsed_algorithm == "bogo_sort":
            return "a long time... probably"

        from sorting_vis.bare_algorithms import BareAlgorithms

        start = time()
        getattr(BareAlgorithms, self.parsed_algorithm)(
            [*self.arr], self.arr_length
        )
        end = time()

        return end - start

    def _init_arr(self) -> None:
        self.currently_sorting = False
        self.b_toggle_sort.configure(state="disabled", text="Pause")
        self.b_init_sort.configure(state="normal")

        self.arr = [
            randint(self.lowerbound, self.upperbound)
            for _ in range(self.samplecount)
        ]
        self.arr_length = len(self.arr)
        self.minval = min(self.arr)
        self.maxval = max(self.arr)
        self.range = self.maxval - self.minval

        self.bar_width = self.canvas_width / self.arr_length

        self.sorting_time = self._estimate_sorting_time()

        self._render_arr(self.arr)

    def _init_sort(self, arr: List[int]) -> None:
        self.currently_sorting = True
        self.sorter.paused = False
        self.b_toggle_sort.configure(state="normal")
        self.b_init_sort.configure(state="disabled")
        self.b_new_arr.configure(state="disabled")

        getattr(self.sorter, self.parsed_algorithm)(arr)

    def _toggle_sort(self) -> None:
        if self.currently_sorting:
            self.sorter.paused = True
            self.currently_sorting = False
            self.b_toggle_sort.configure(text="Resume", state="normal")
            self.b_new_arr.configure(state="normal")
        else:
            self.sorter.paused = False
            self.currently_sorting = True
            self.b_toggle_sort.configure(text="Pause", state="normal")
            self.b_new_arr.configure(state="disabled")
            self._init_sort(self.sorter.paused_arr)

    def _render_arr(
        self,
        arr: List[int],
        sorting_indices: List[int] = [],
        green_up_to: int = 0,
        complete: bool = False,
        fail: bool = False,
    ) -> None:
        self.arr_canvas.delete("columns")

        for i, item in enumerate(arr):
            x1 = i * self.bar_width + 3
            y1 = self.canvas_height * (1 - (item - self.minval) / self.range)
            x2 = x1 + self.bar_width
            y2 = self.canvas_height

            if not fail:
                if green_up_to > 0 and i <= green_up_to:
                    fill = "#28b842"
                    outline = "#229937"
                elif not complete:
                    fill = "#eb3f3f" if i in sorting_indices else "#aebac2"
                    outline = "#eb6e6e" if i in sorting_indices else "#c7cdd1"
                else:
                    fill = "#28b842"
                    outline = "#229937"
            else:
                fill = "#ed3b4d"
                outline = "#590911"

            self.arr_canvas.create_rectangle(
                x1, y1, x2, y2, fill=fill, outline=outline, tags="columns"
            )

        if complete:
            self.currently_sorting = False
            self.b_toggle_sort.configure(state="disabled")
            self.b_new_arr.configure(state="normal")

        self.update()

    def _render_checking_complete(self, arr: List[int]) -> bool:
        if all(arr[i] <= arr[i + 1] for i in range(self.arr_length - 1)):
            for i in range(self.arr_length):
                self._render_arr(arr, green_up_to=i)
            self._render_arr(arr, complete=True)
            return True
        else:
            self._render_arr(arr, fail=True, complete=True)
            messagebox.showerror(
                "Error", "Array could not be sorted properly."
            )
            return False


if __name__ == "__main__":
    from .__main__ import start

    start()
