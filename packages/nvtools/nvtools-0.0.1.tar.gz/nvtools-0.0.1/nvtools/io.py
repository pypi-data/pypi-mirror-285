"""File input/output tools."""

import operator
import pathlib
import sys
from dataclasses import dataclass

import h5py
import numpy as np
import numpy.typing as npt
from colorama import Fore, Style
from prettytable import SINGLE_BORDER, PrettyTable

import nvtools


@dataclass
class MeasurementData:
    """Measurement data."""

    x_data: npt.NDArray
    iterators: list
    observables: dict


class H5Loader:
    """H5 file loader."""

    def __init__(self, file_path=None):
        """H5 file loader."""
        folder = pathlib.Path(sys.argv[0]).parent
        self.file_path = file_path if file_path else pathlib.Path(folder, "raw_data.h5")

    def print_contents(self):
        """Print file contents."""
        with h5py.File(self.file_path, "r") as file:
            iterators = []
            for e in file["Iterators"]:
                iterators.append((e, np.array(file["Iterators"][e])))
            parameters = []
            for e in file["Meta Info"]["Parameters"]:
                parameters.append((e, float(np.array(file["Meta Info"]["Parameters"][e]))))
            observables = []
            for e in file["Observables"]:
                observables.append((e, np.array(file["Observables"][e])))

        print(
            Fore.GREEN
            + Style.BRIGHT
            + "───────────────────────── H5 Loader ─────────────────────────"
            + Style.RESET_ALL
        )
        table = PrettyTable()
        table.set_style(SINGLE_BORDER)
        table.field_names = ["Iterator", "Value"]
        for i in range(len(iterators)):
            table.add_row([f"{iterators[i][0]}", f"{iterators[i][1]}"])
        print(table)
        print("")

        table = PrettyTable()
        table.set_style(SINGLE_BORDER)
        table.field_names = ["Parameter", "Value"]
        for i in range(len(parameters)):
            table.add_row([f"{parameters[i][0]}", f"{parameters[i][1]}"])
        print(table)
        print("")

        table = PrettyTable()
        table.set_style(SINGLE_BORDER)
        table.field_names = ["Observables", "Value"]
        for i in range(len(observables)):
            table.add_row([f"{observables[i][0]}", f"{observables[i][1]}"])
        print(table)

    def load_odmr_lia(self, exclude=None):
        """Load LIA odmr."""
        exclude = [] if exclude is None else exclude

        with h5py.File(self.file_path, "r") as file:
            iterators = {}
            for e in file["Iterators"]:
                iterators[e] = np.array(file["Iterators"][e])
            parameters = {}
            for e in file["Meta Info"]["Parameters"]:
                parameters[e] = float(np.array(file["Meta Info"]["Parameters"][e]))

            mw_start = float(np.array(file["Meta Info"]["Parameters"]["Sweep Start Frequency in MHz"]))
            mw_stop = float(np.array(file["Meta Info"]["Parameters"]["Sweep Stop Frequency in MHz"]))
            samples = int(np.array(file["Meta Info"]["Parameters"]["Samples"]))

            iterators = str(np.array(file["Meta Info"]["Iterators"]))[2:-1].split("\\n")
            iterators_list = []
            for e in iterators:
                e = e.split(": ")
                iterators_list.append((e[0], np.array(file["Iterators"][e[0]])))

            observables = {}
            for obs in file["Observables"]:
                observables[obs] = {}

                for i in range(len(iterators_list[1][1])):
                    arr = np.zeros(samples)
                    n_excluded = 0
                    for j in range(len(iterators_list[0][1])):
                        if f"{i}_{j}" in exclude:
                            n_excluded += 1
                            continue
                        arr += np.array(file["Observables"][obs][f"{i}_{j}"])
                    arr /= len(iterators_list[0][1]) - n_excluded
                    observables[obs][f"{i}"] = arr

        mw_frequency = np.linspace(mw_start, mw_stop, samples)

        if nvtools.VERBOSE:
            print(
                Fore.GREEN
                + Style.BRIGHT
                + "───────────────────────── H5 Loader ─────────────────────────"
                + Style.RESET_ALL
            )
            table = PrettyTable()
            table.set_style(SINGLE_BORDER)
            table.field_names = ["", "Value"]
            table.add_row(["File path", f"{self.file_path}"])
            table.add_row(["Iterators", f"{list(map(operator.itemgetter(0), iterators_list))}"])
            table.add_row(["Observables", f"{list(observables.keys())}"])
            if exclude:
                table.add_row(["Excluding", f"{exclude}"])
            print(table)
            print("\n")

        return MeasurementData(mw_frequency, iterators_list, observables)
