"""Step-by-step sorting visualizer for five algorithms."""

from __future__ import annotations

import argparse
import random
import tkinter as tk
from collections.abc import Generator
from dataclasses import dataclass
from tkinter import messagebox, ttk
from typing import Callable


MAX_VALUES = 50
INITIAL_PAUSE_MS = 1500


@dataclass(frozen=True)
class Step:
    highlights: tuple[int, ...]
    action: str
    changed: bool = False


StepGenerator = Generator[Step, None, None]
StepFactory = Callable[[list[int]], StepGenerator]


def bubble_sort_steps(values: list[int]) -> StepGenerator:
    """Bubble sort: compare neighbours and move the larger value right."""

    for end in range(len(values) - 1, 0, -1):
        swapped = False
        for index in range(end):
            changed = values[index] > values[index + 1]
            if changed:
                values[index], values[index + 1] = values[index + 1], values[index]
                swapped = True
            yield Step(
                (index, index + 1),
                "Байрыг сольсон" if changed else "Харьцуулсан",
                changed,
            )
        if not swapped:
            return


def selection_sort_steps(values: list[int]) -> StepGenerator:
    """Selection sort: find the smallest remaining value for each position."""

    size = len(values)
    for left in range(size - 1):
        smallest = left
        for index in range(left + 1, size):
            changed = values[index] < values[smallest]
            if changed:
                smallest = index
            yield Step((smallest, index), "Хамгийн багыг хайж байна", False)
        if smallest != left:
            values[left], values[smallest] = values[smallest], values[left]
            yield Step((left, smallest), "Байрыг сольсон", True)


def insertion_sort_steps(values: list[int]) -> StepGenerator:
    """Insertion sort: insert each value into the sorted left-hand side."""

    for index in range(1, len(values)):
        item = values[index]
        position = index
        while position > 0:
            if values[position - 1] <= item:
                yield Step((position - 1, position), "Харьцуулсан", False)
                break
            values[position] = values[position - 1]
            values[position - 1] = item
            position -= 1
            yield Step((position, position + 1), "Зүүн тийш шилжүүлсэн", True)


def merge_sort_steps(values: list[int]) -> StepGenerator:
    """Recursive merge sort, yielding after every write to the main list."""

    def merge(left: int, middle: int, right: int) -> StepGenerator:
        first = values[left:middle]
        second = values[middle:right]
        first_index = second_index = 0
        output = left

        while first_index < len(first) and second_index < len(second):
            if first[first_index] <= second[second_index]:
                values[output] = first[first_index]
                first_index += 1
            else:
                values[output] = second[second_index]
                second_index += 1
            yield Step((output,), "Хэсгүүдийг нэгтгэж байна", True)
            output += 1

        while first_index < len(first):
            values[output] = first[first_index]
            first_index += 1
            yield Step((output,), "Үлдсэн утгыг байрлуулсан", True)
            output += 1
        while second_index < len(second):
            values[output] = second[second_index]
            second_index += 1
            yield Step((output,), "Үлдсэн утгыг байрлуулсан", True)
            output += 1

    def sort_range(left: int, right: int) -> StepGenerator:
        if right - left <= 1:
            return
        middle = (left + right) // 2
        yield from sort_range(left, middle)
        yield from sort_range(middle, right)
        yield from merge(left, middle, right)

    yield from sort_range(0, len(values))


def quick_sort_steps(values: list[int]) -> StepGenerator:
    """Lomuto quicksort, yielding once per comparison or pivot swap."""

    def sort_range(low: int, high: int) -> StepGenerator:
        if low >= high:
            return
        pivot = values[high]
        boundary = low

        for index in range(low, high):
            changed = values[index] <= pivot
            if changed:
                values[boundary], values[index] = values[index], values[boundary]
                current_boundary = boundary
                boundary += 1
            else:
                current_boundary = boundary
            yield Step(
                (index, high, current_boundary),
                "Pivot-той харьцуулсан",
                changed and current_boundary != index,
            )

        changed = boundary != high
        values[boundary], values[high] = values[high], values[boundary]
        yield Step((boundary, high), "Pivot-ийг байрлуулсан", changed)
        yield from sort_range(low, boundary - 1)
        yield from sort_range(boundary + 1, high)

    yield from sort_range(0, len(values) - 1)


@dataclass(frozen=True)
class Algorithm:
    name: str
    factory: StepFactory
    color: str


ALGORITHMS = (
    Algorithm("Bubble sort", bubble_sort_steps, "#4f8cff"),
    Algorithm("Selection sort", selection_sort_steps, "#9b6cff"),
    Algorithm("Insertion sort", insertion_sort_steps, "#f59e52"),
    Algorithm("Merge sort", merge_sort_steps, "#37b987"),
    Algorithm("Quick sort", quick_sort_steps, "#ef5da8"),
)


@dataclass
class ChartState:
    values: list[int]
    highlights: tuple[int, ...] = ()
    changed: bool = False
    steps: int = 0
    finished: bool = False


class AlgorithmChart:
    def __init__(self, parent: ttk.Frame, algorithm: Algorithm, background: str) -> None:
        self.algorithm = algorithm
        self.status = tk.StringVar(value="Хүлээж байна")
        self.frame = ttk.Frame(parent, style="Chart.TFrame", padding=(10, 8))

        header = ttk.Frame(self.frame, style="Chart.TFrame")
        header.pack(fill="x", pady=(0, 4))
        ttk.Label(header, text=algorithm.name, style="ChartTitle.TLabel").pack(side="left")
        ttk.Label(header, textvariable=self.status, style="ChartStatus.TLabel").pack(
            side="right"
        )

        self.canvas = tk.Canvas(
            self.frame,
            bg=background,
            height=200,
            highlightthickness=0,
            relief="flat",
        )
        self.canvas.pack(fill="both", expand=True)

    def draw(self, state: ChartState, maximum: int) -> None:
        canvas = self.canvas
        canvas.delete("all")
        width = max(canvas.winfo_width(), 120)
        height = max(canvas.winfo_height(), 100)
        top = 21 if len(state.values) <= 16 else 8
        bottom = 18
        plot_height = max(1, height - top - bottom)

        if not state.values:
            canvas.create_text(
                width / 2,
                height / 2,
                text="Өгөгдөл хүлээж байна",
                fill="#94a3b8",
                font=("Segoe UI", 9),
            )
            return

        bar_width = width / len(state.values)
        highlighted = set(state.highlights)
        for index, value in enumerate(state.values):
            x1 = index * bar_width + 1
            x2 = max(x1 + 1, (index + 1) * bar_width - 1)
            bar_height = max(1, value / max(maximum, 1) * plot_height)
            if index in highlighted:
                color = "#f8fafc" if state.changed else "#fde047"
            else:
                color = self.algorithm.color
            canvas.create_rectangle(
                x1,
                top + plot_height - bar_height,
                x2,
                top + plot_height,
                fill=color,
                width=0,
            )
            if len(state.values) <= 16:
                canvas.create_text(
                    (x1 + x2) / 2,
                    top + plot_height - bar_height - 3,
                    text=str(value),
                    fill="#cbd5e1",
                    anchor="s",
                    font=("Segoe UI", 7),
                )

        canvas.create_line(0, top + plot_height, width, top + plot_height, fill="#34415c")
        canvas.create_text(
            4,
            height - 3,
            text="0",
            fill="#73819b",
            anchor="sw",
            font=("Segoe UI", 7),
        )
        canvas.create_text(
            width - 4,
            height - 3,
            text=f"max {maximum:,}",
            fill="#73819b",
            anchor="se",
            font=("Segoe UI", 7),
        )


class SortingVisualizerApp:
    BACKGROUND = "#0f172a"
    PANEL = "#172036"
    CHART = "#111a2d"
    TEXT = "#f8fafc"
    MUTED = "#94a3b8"
    ACCENT = "#4f8cff"

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Sorting Visualizer — step by step")
        self.root.geometry("1180x820")
        self.root.minsize(900, 680)
        self.root.configure(bg=self.BACKGROUND)

        self.count_value = tk.StringVar(value="20")
        self.maximum_value = tk.StringVar(value="100")
        self.speed_value = tk.StringVar(value="3")
        self.seed_value = tk.StringVar(value="42")
        self.main_status = tk.StringVar(value="Эхлүүлэхэд бэлэн")
        self.states = {algorithm.name: ChartState([]) for algorithm in ALGORITHMS}
        self.generators: dict[str, StepGenerator] = {}
        self.charts: dict[str, AlgorithmChart] = {}
        self.current_maximum = 100
        self.running = False
        self.run_id = 0

        self._configure_styles()
        self._build_ui()

    def _configure_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("App.TFrame", background=self.BACKGROUND)
        style.configure("Panel.TFrame", background=self.PANEL)
        style.configure("Chart.TFrame", background=self.CHART)
        style.configure(
            "Title.TLabel",
            background=self.BACKGROUND,
            foreground=self.TEXT,
            font=("Segoe UI Semibold", 22),
        )
        style.configure(
            "Subtitle.TLabel",
            background=self.BACKGROUND,
            foreground=self.MUTED,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Field.TLabel",
            background=self.PANEL,
            foreground=self.TEXT,
            font=("Segoe UI Semibold", 9),
        )
        style.configure(
            "Status.TLabel",
            background=self.PANEL,
            foreground=self.MUTED,
            font=("Segoe UI", 9),
        )
        style.configure(
            "ChartTitle.TLabel",
            background=self.CHART,
            foreground=self.TEXT,
            font=("Segoe UI Semibold", 10),
        )
        style.configure(
            "ChartStatus.TLabel",
            background=self.CHART,
            foreground=self.MUTED,
            font=("Segoe UI", 8),
        )
        style.configure(
            "Accent.TButton",
            background=self.ACCENT,
            foreground="white",
            borderwidth=0,
            padding=(18, 9),
            font=("Segoe UI Semibold", 10),
        )
        style.map("Accent.TButton", background=[("active", "#70a2ff")])
        style.configure("Stop.TButton", padding=(14, 9))

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, style="App.TFrame", padding=22)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="Sorting Visualizer", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            outer,
            text="Шар bar = харьцуулж байна · Цагаан bar = байрлал өөрчлөгдсөн",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(1, 14))

        controls = ttk.Frame(outer, style="Panel.TFrame", padding=14)
        controls.pack(fill="x")
        controls.columnconfigure(4, weight=1)
        self._add_entry(controls, "ӨГӨГДЛИЙН ТОО (2–50)", self.count_value, 0, 13)
        self._add_entry(controls, "ХАМГИЙН ИХ УТГА", self.maximum_value, 1, 14)
        self._add_speed_field(controls, 2)
        self._add_entry(controls, "SEED", self.seed_value, 3, 8)

        actions = ttk.Frame(controls, style="Panel.TFrame")
        actions.grid(row=0, column=4, rowspan=2, sticky="e", padx=(16, 0))
        self.start_button = ttk.Button(
            actions,
            text="▶  Random үүсгээд эхлүүлэх",
            command=self.start,
            style="Accent.TButton",
        )
        self.start_button.pack(side="left")
        self.stop_button = ttk.Button(
            actions,
            text="Зогсоох",
            command=self.stop,
            state="disabled",
            style="Stop.TButton",
        )
        self.stop_button.pack(side="left", padx=(8, 0))
        ttk.Label(controls, textvariable=self.main_status, style="Status.TLabel").grid(
            row=2, column=0, columnspan=5, sticky="w", pady=(11, 0)
        )

        grid = ttk.Frame(outer, style="App.TFrame")
        grid.pack(fill="both", expand=True, pady=(14, 0))
        for column in range(6):
            grid.columnconfigure(column, weight=1, uniform="charts")
        grid.rowconfigure(0, weight=1)
        grid.rowconfigure(1, weight=1)

        positions = ((0, 0, 2), (0, 2, 2), (0, 4, 2), (1, 1, 2), (1, 3, 2))
        for algorithm, (row, column, span) in zip(ALGORITHMS, positions):
            chart = AlgorithmChart(grid, algorithm, self.CHART)
            chart.frame.grid(
                row=row,
                column=column,
                columnspan=span,
                sticky="nsew",
                padx=6,
                pady=6,
            )
            chart.canvas.bind("<Configure>", lambda _event: self._draw_all())
            self.charts[algorithm.name] = chart

    def _add_entry(
        self,
        parent: ttk.Frame,
        label: str,
        variable: tk.StringVar,
        column: int,
        width: int,
    ) -> None:
        ttk.Label(parent, text=label, style="Field.TLabel").grid(
            row=0, column=column, sticky="w", padx=(0, 12)
        )
        entry = ttk.Entry(parent, textvariable=variable, width=width, font=("Segoe UI", 10))
        entry.grid(row=1, column=column, sticky="w", padx=(0, 12), pady=(4, 0))
        entry.bind("<Return>", lambda _event: self.start())

    def _add_speed_field(self, parent: ttk.Frame, column: int) -> None:
        ttk.Label(parent, text="АЛХАМ / СЕК", style="Field.TLabel").grid(
            row=0, column=column, sticky="w", padx=(0, 12)
        )
        speed = ttk.Combobox(
            parent,
            textvariable=self.speed_value,
            values=("1", "2", "3", "5", "10", "20", "30", "60"),
            state="readonly",
            width=8,
            font=("Segoe UI", 10),
        )
        speed.grid(row=1, column=column, sticky="w", padx=(0, 12), pady=(4, 0))

    @staticmethod
    def _integer(raw: str, label: str, minimum: int, maximum: int) -> int:
        try:
            value = int(raw.replace(",", "").replace(" ", ""))
        except ValueError as error:
            raise ValueError(f"{label} бүхэл тоо байх ёстой.") from error
        if not minimum <= value <= maximum:
            raise ValueError(f"{label}: {minimum:,}–{maximum:,} хооронд оруулна уу.")
        return value

    def start(self) -> None:
        if self.running:
            return
        try:
            count = self._integer(self.count_value.get(), "Өгөгдлийн тоо", 2, MAX_VALUES)
            maximum = self._integer(
                self.maximum_value.get(), "Хамгийн их утга", 1, 1_000_000
            )
            self._integer(self.speed_value.get(), "Алхам/сек", 1, 60)
            seed = self._integer(self.seed_value.get(), "Seed", 0, 2_147_483_647)
        except ValueError as error:
            messagebox.showwarning("Утгаа шалгана уу", str(error), parent=self.root)
            return

        randomizer = random.Random(seed)
        data = [randomizer.randint(1, maximum) for _ in range(count)]
        self.current_maximum = maximum
        self.generators.clear()
        self.run_id += 1
        current_run = self.run_id
        self.running = True

        for algorithm in ALGORITHMS:
            values = data.copy()
            self.states[algorithm.name] = ChartState(values)
            self.generators[algorithm.name] = algorithm.factory(values)
            self.charts[algorithm.name].status.set("Эхлэх гэж байна")

        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.main_status.set(
            f"Random өгөгдлийг {INITIAL_PAUSE_MS / 1000:.1f} секунд харуулсны дараа эхэлнэ"
        )
        self._draw_all()
        self.root.after(INITIAL_PAUSE_MS, lambda: self._animation_tick(current_run))

    def _animation_tick(self, current_run: int) -> None:
        if not self.running or current_run != self.run_id:
            return

        completed = 0
        for algorithm in ALGORITHMS:
            state = self.states[algorithm.name]
            if state.finished:
                completed += 1
                continue
            try:
                step = next(self.generators[algorithm.name])
                state.highlights = step.highlights
                state.changed = step.changed
                state.steps += 1
                self.charts[algorithm.name].status.set(f"#{state.steps} · {step.action}")
            except StopIteration:
                state.finished = True
                state.highlights = ()
                state.changed = False
                completed += 1
                self.charts[algorithm.name].status.set(f"Дууссан · {state.steps} алхам")

        self._draw_all()
        if completed == len(ALGORITHMS):
            self.running = False
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.main_status.set("Бүх алгоритм эрэмбэлж дууслаа")
            return

        speed = max(1, int(self.speed_value.get()))
        self.main_status.set(f"Алгоритм бүр секундэд {speed} алхам хийж байна")
        self.root.after(max(1, round(1000 / speed)), lambda: self._animation_tick(current_run))

    def stop(self) -> None:
        if not self.running:
            return
        self.running = False
        self.run_id += 1
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.main_status.set("Эрэмбэлэлтийг зогсоолоо")
        for algorithm in ALGORITHMS:
            if not self.states[algorithm.name].finished:
                self.charts[algorithm.name].status.set("Зогссон")

    def _draw_all(self) -> None:
        for algorithm in ALGORITHMS:
            self.charts[algorithm.name].draw(
                self.states[algorithm.name], self.current_maximum
            )


def run_self_test() -> None:
    cases = [
        [],
        [1],
        [2, 1],
        [4, 1, 4, 0, 9, 3],
        list(range(50)),
        list(range(50, 0, -1)),
        [7] * 50,
    ]
    randomizer = random.Random(2026)
    cases.append([randomizer.randint(0, 100) for _ in range(50)])

    for algorithm in ALGORITHMS:
        for original in cases:
            actual = original.copy()
            for _step in algorithm.factory(actual):
                pass
            assert actual == sorted(original), f"{algorithm.name} failed"
    print(f"Self-test passed: {len(ALGORITHMS)} algorithms, {len(cases)} data sets.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="test all algorithms")
    arguments = parser.parse_args()
    if arguments.self_test:
        run_self_test()
        return

    root = tk.Tk()
    SortingVisualizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
