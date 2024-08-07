from __future__ import annotations

from typing import Final, TypeAlias
import matplotlib.pyplot as plt

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Center, VerticalScroll
from textual.widgets import Header, Static, Input, Footer, Button

PUT_VALUE_PLACEHOLDER: Final[str] = "podaj wartosc"

CoordinatesType: TypeAlias = tuple[float, float]


class InputsContainer(Horizontal):
    DEFAULT_CSS = """
    InputsContainer {
        height: auto;
        margin-top: 1;
    }
    """


class PassPointsHeader(Static):
    DEFAULT_CSS = """
    PassPointsHeader {
        width: 1fr;
        text-align: center;
        background: $primary-lighten-1;
    }
    """


class CoordinateInput(Input):
    def __init__(self, coordinate_kind: str):
        super().__init__(
            placeholder=PUT_VALUE_PLACEHOLDER + f" {coordinate_kind}",
            type="number",
            max_length=4,
        )


class LastCalculationDisplay(Static):
    DEFAULT_CSS = """
    LastCalculationDisplay {
        width: 1fr;
        height: auto;
        text-align: center;
        background: $success-darken-2;
        border: $primary;
    }
    """

    def __init__(
        self,
        first_point: CoordinatesType,
        second_point: CoordinatesType,
        third_point: CoordinatesType,
        fourth_point: CoordinatesType,
        result: CoordinatesType | None = None,
        *,
        is_parallely: bool = False,
    ):
        display_text: str = ""
        if result is not None:
            display_text = f"Odcinek {first_point} - {second_point} i {third_point} - {fourth_point} przecinaja sie w -> ({result[0] :.2f} {result[1] :.2f})"

        if is_parallely and result is None:
            display_text = f"Odcinek {first_point} - {second_point} i {third_point} - {fourth_point} są rownolegle lub wspolliniowe"
        elif result is None and not is_parallely:
            f"Odcinek {first_point} - {second_point} i {third_point} - {fourth_point} nie przecinaja sie"

        super().__init__(renderable=display_text)


class PointsApp(App):
    DEFAULT_CSS = """
    PointsApp {
        Input {
            width: 1fr;
        }

        Button {
            margin-top: 1;
            align: center middle;
        }

        #last-calculations-header {
            width: 1fr;
            text-align: center;
            background: $primary;
            margin-top: 1;
        }
    }

    """

    def __init__(self):
        super().__init__()
        self._x1_1_input = CoordinateInput("X1")
        self._y1_1_input = CoordinateInput("Y1")
        self._x2_1_input = CoordinateInput("X2")
        self._y2_1_input = CoordinateInput("Y2")

        self._x1_2_input = CoordinateInput("X1")
        self._y1_2_input = CoordinateInput("Y1")
        self._x2_2_input = CoordinateInput("X2")
        self._y2_2_input = CoordinateInput("Y2")

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield PassPointsHeader("Podaj wspolrzedne pierwszegeo odcinka:")
        with InputsContainer():
            yield self._x1_1_input
            yield self._y1_1_input
        with InputsContainer():
            yield self._x2_1_input
            yield self._y2_1_input
        yield PassPointsHeader("Podaj wspolrzedne drugiego odcinka:")
        with InputsContainer():
            yield self._x1_2_input
            yield self._y1_2_input
        with InputsContainer():
            yield self._x2_2_input
            yield self._y2_2_input
        with Center():
            yield Button(
                "Oblicz punkt przeciecia",
                id="calculate-point-button",
                variant="success",
            )
            yield Button(
                "Wyczysc wartosci wejsciowe", id="clear-inputs-button", variant="error"
            )
        yield Static("Ostatnie wyniki:", id="last-calculations-header")
        yield VerticalScroll(id="last-calculations-container")
        yield Footer()

    def _orientation(
        self,
        coordinates_1: CoordinatesType,
        coordinates_2: CoordinatesType,
        coordinates_3: CoordinatesType,
    ) -> int:
        """Sprawdzanie orientacji."""

        determinant = (coordinates_2[1] - coordinates_1[1]) * (
            coordinates_3[0] - coordinates_2[0]
        ) - (coordinates_2[0] - coordinates_1[0]) * (
            coordinates_3[1] - coordinates_2[1]
        )
        if determinant == 0:
            return 0
        elif determinant > 0:
            return 1
        else:
            return 2

    def _on_segment(
        self,
        coordinates_1: CoordinatesType,
        coordinates_2: CoordinatesType,
        coordinates_3: CoordinatesType,
    ) -> bool:
        """Sprawdza czy punkt leży na odcinku."""

        if max(coordinates_1[0], coordinates_3[0]) >= coordinates_2[0] >= min(
            coordinates_1[0], coordinates_3[0]
        ) and max(coordinates_1[1], coordinates_3[1]) >= coordinates_2[1] >= min(
            coordinates_1[1], coordinates_3[1]
        ):
            return True
        return False

    def _do_intersect(
        self,
        p1: CoordinatesType,
        q1: CoordinatesType,
        p2: CoordinatesType,
        q2: CoordinatesType,
    ) -> bool:
        """Sprawdza czy odcinki się przecinają."""
        o1 = self._orientation(p1, q1, p2)
        o2 = self._orientation(p1, q1, q2)
        o3 = self._orientation(p2, q2, p1)
        o4 = self._orientation(p2, q2, q1)

        if o1 != o2 and o3 != o4:
            return True

        if o1 == 0 and self._on_segment(p1, p2, q1):
            return True
        if o2 == 0 and self._on_segment(p1, q2, q1):
            return True
        if o3 == 0 and self._on_segment(p2, p1, q2):
            return True
        if o4 == 0 and self._on_segment(p2, q1, q2):
            return True
        return False

    def _create_coordinate(self, x: str, y: str) -> CoordinatesType:
        return float(x), float(y)

    def _clear_inputs(self) -> None:
        inputs = self.query(Input)
        for input_ in inputs:
            input_.clear()

    def find_overlap_segment(
        self,
        p1: CoordinatesType,
        q1: CoordinatesType,
        p2: CoordinatesType,
        q2: CoordinatesType,
    ) -> tuple[CoordinatesType, CoordinatesType] | None:
        # Ensure p1 is the leftmost endpoint for the first segment
        if p1[0] > q1[0] or (p1[0] == q1[0] and p1[1] > q1[1]):
            p1, q1 = q1, p1
        # Ensure p2 is the leftmost endpoint for the second segment
        if p2[0] > q2[0] or (p2[0] == q2[0] and p2[1] > q2[1]):
            p2, q2 = q2, p2

        # Check if segments are overlapping
        if self._on_segment(p1, p2, q1):
            start = max(p1, p2)
            end = min(q1, q2)
            return start, end
        return

    @on(Button.Pressed, "#calculate-point-button")
    def intersection_point(self) -> None:
        """
        Funkcja wykonuje:
        -----------------
        1. Potwierdzenie przecięcia
        2. Sprawdzanie czy odcinki są równoległe lub współniniowe
        3. Wyznaczenie punktu przecięcia
        """

        x1_1, y1_1 = self._x1_1_input.value, self._y1_1_input.value
        x2_1, y2_1 = self._x2_1_input.value, self._y2_1_input.value

        x1_2, y1_2 = self._x1_2_input.value, self._y1_2_input.value
        x2_2, y2_2 = self._x2_2_input.value, self._y2_2_input.value

        if not all([x1_1, y1_1, x2_1, y2_1, x1_2, y1_2, x2_2, y2_2]):
            self.notify(
                "Nie podales wszystkich wspolrzednych! Wypelnij wszystkie",
                severity="warning",
            )
            return

        p1 = self._create_coordinate(x1_1, y1_1)
        q1 = self._create_coordinate(x2_1, y2_1)
        p2 = self._create_coordinate(x1_2, y1_2)
        q2 = self._create_coordinate(x2_2, y2_2)

        if not self._do_intersect(p1, q1, p2, q2):
            self.notify("Brak przeciecia")
            self.query_one("#last-calculations-container").mount(
                LastCalculationDisplay(p1, q1, p2, q2)
            )
            self._clear_inputs()
            plt.plot(
                [float(x1_1), float(x2_1)],
                [float(y1_1), float(y2_1)],
                label="odcinek 1",
                color="b",
            )
            plt.plot(
                [float(x1_2), float(x2_2)],
                [float(y1_2), float(y2_2)],
                label="odcinek 2",
                color="r",
            )
            plt.show()
            return

        a1 = q1[1] - p1[1]
        b1 = p1[0] - q1[0]
        c1 = a1 * p1[0] + b1 * p1[1]

        a2 = q2[1] - p2[1]
        b2 = p2[0] - q2[0]
        c2 = a2 * p2[0] + b2 * p2[1]

        determinant = a1 * b2 - a2 * b1

        if determinant == 0:
            self.notify("Odcinki są współiniowe")
            first, second = self.find_overlap_segment(p1, q1, p2, q2)
            plt.plot(
                [float(x1_1), float(x2_1)],
                [float(y1_1), float(y2_1)],
                label="odcinek 1",
                color="b",
            )
            plt.plot(
                [float(x1_2), float(x2_2)],
                [float(y1_2), float(y2_2)],
                label="odcinek 2",
                color="r",
            )
            plt.plot(
                [float(first[0]), float(second[0])],
                [float(first[1]), float(second[1])],
                label="odcinek wspólny",
                color="g",
            )

            plt.scatter(first[0], first[1], color="b", zorder=5)
            plt.text(first[0], first[1], f"{first[0]} {first[1]}", ha="right")
            plt.scatter(second[0], second[1], color="r", zorder=5)
            plt.text(second[0], second[1], f"{second[0]} {second[1]}", ha="right")
            plt.show()
            self._clear_inputs()
            return

        x = (b2 * c1 - b1 * c2) / determinant
        y = (a1 * c2 - a2 * c1) / determinant

        self.notify(
            f"Przecinaja sie w punkcie K o wspolrzednych: X: {x :.2f} Y: {y :.2f}"
        )
        self.query_one("#last-calculations-container").mount(
            LastCalculationDisplay(p1, q1, p2, q2, (x, y))
        )
        self._clear_inputs()
        plt.plot(
            [float(x1_1), float(x2_1)],
            [float(y1_1), float(y2_1)],
            label="odcinek 1",
            color="b",
        )
        plt.plot(
            [float(x1_2), float(x2_2)],
            [float(y1_2), float(y2_2)],
            label="odcinek 2",
            color="r",
        )
        plt.scatter(x, y, color="g")
        plt.show()

    @on(Button.Pressed, "#clear-inputs-button")
    def clear_inputs_by_button(self) -> None:
        self._clear_inputs()


if __name__ == "__main__":
    PointsApp().run()
