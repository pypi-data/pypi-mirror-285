"""
This module creates the class to compute the pre processing of the MATER model.
"""

import os

import numpy as np
import pandas as pd
from tkinter import filedialog

from mater.core._utils import _compute_pseudoinverse, _exponential_decay


class _MaterPreProcess:
    """Pre processing of the MATER model."""

    def __init__(self):
        self.dir_path = ""

    def _to_mater(self, variable: str, k=None):
        r"""
        Save a specified variable to durable storage in the Parquet format, optionally at a specific time point.

        This method handles the saving of model outputs to a file system, organizing the files within directories corresponding to the simulation run and scenario. It can save data either for a specific time point or for the entire set of outputs depending on the presence of the `k` parameter.

        **Parameters:**

        - `variable`: The name of the variable (output) to be saved.
        - `k`: Optional; an integer representing the time step at which the data should be saved. If not provided, the entire data set for the variable is saved.

        Method Operation
        ----------------
        - Directories are created for the variable if they do not exist.
        - If `k` is not specified, the entire data set for the variable is saved.
        - If `k` is specified, only the data corresponding to that time step is saved.
        - The data is saved in the Parquet format using the PyArrow engine with snappy compression.

        Examples
        --------
        .. code-block:: python

            instance._to_mater('self_disposal_flow', k=5)

        This would save the 'self_disposal_flow' output at time step 5 to the appropriate directory structure.

        Notes
        -----
        It is important to ensure that `self.outputs[variable]` contains data that can be successfully saved. This might involve handling different data structures (e.g., DataFrames, Series) appropriately. The method handles exceptions related to data saving by falling back to alternative saving procedures if the primary method fails (e.g., due to missing indices).
        """
        # Directory creation for saving the outputs
        os.makedirs(
            os.path.join(self.dir_path, self.run_name, variable),
            exist_ok=True,
        )
        # Save logic depending on the presence of k
        if k == None:
            self.outputs[variable].stack(dropna=False).to_frame("value").to_parquet(
                os.path.join(
                    self.dir_path,
                    self.run_name,
                    variable,
                    variable + ".mater",
                ),
                engine="pyarrow",
                compression="snappy",
            )
        else:
            try:
                self.outputs[variable].to_frame(k).rename_axis("time", axis=1).stack(dropna=False).to_frame(
                    "value"
                ).to_parquet(
                    os.path.join(
                        self.dir_path,
                        self.run_name,
                        variable,
                        str(k) + ".mater",
                    ),
                    engine="pyarrow",
                    compression="snappy",
                )
            except AttributeError:
                # Fallback for different data structures
                self.outputs[variable].stack(dropna=False).to_frame("value").to_parquet(
                    os.path.join(
                        self.dir_path,
                        self.run_name,
                        variable,
                        str(k) + ".mater",
                    ),
                    engine="pyarrow",
                    compression="snappy",
                )

    def set_dir_path(self):
        r"""Update the project directory path by opening an ask directory window.

        This directory must contain the input data Excel file to be able to run the model.
        It will also contain a directory named as the scenario name of the run with the output data Parquet files.

        You can also set the directory directly:

        .. code-block:: python

            model = Mater()
            model.dir_path = PATH\TO\YOUR\PROJECT
        """
        self.dir_path = filedialog.askdirectory()

    def set_run_name(self, run_name: str):
        """Sets the name of the run folder to access (self.run_name). It has to be inside the project folder (self.dir_path).

        :param run_name: the name of the run folder to access
        :type run_name: str
        """
        self.run_name = run_name

    def get(self, variable: str, t: int = None, scenarios: list = None):
        r"""
        Retrieve data for a specified variable from durable storage in Parquet format, potentially filtered by simulation time or scenario.

        This method reads data from the file system where simulation outputs and inputs are stored. It can retrieve data for a specific variable across all scenarios, at a particular time step, or for the entire duration of a scenario depending on the parameters provided.

        :param variable: The name of the output variable to be read from storage.
        :type variable: str
        :param t: an integer representing the time step for which data should be retrieved. If not provided, data across all time steps is retrieved, defaults to None
        :type t: int, optional
        :param scenarios: a list or array of scenario names to be specifically read. If not provided, data is read for the current scenario unless `t` is specified, defaults to None
        :type scenarios: list, optional
        :return: A pandas DataFrame containing the requested data, structured according to the variable and time or scenario specifications.
        :rtype: pd.DataFrame

        Method Operation
        ----------------
        - If `scenarios` is provided, the method retrieves data for the specified variable across all listed scenarios.
        - If `t` is provided, the method retrieves data for the specified variable at the given time step.
        - If neither `t` nor `scenarios` is provided, data for the specified variable across all time steps is retrieved for the current scenario.

        Examples
        --------
        .. code-block:: python

            # Create a Mater instance
            model = Mater()

            # Retrieve data for 'YOUR_VARIABLE' variable across all time steps in the current scenario
            data = model.get('YOUR_VARIABLE')

            # Retrieve data for 'YOUR_VARIABLE' at time step 2015
            data_k5 = model.get('YOUR_VARIABLE', t=2015)

            # Retrieve 'YOUR_VARIABLE' data across multiple scenarios
            data_scenarios = model.get('YOUR_VARIABLE', scenarios=['baseline', 'alternative']).


        Ensure that the file paths and structures are correctly set up and that data integrity is maintained to prevent errors during data retrieval.
        """
        # Implementation of data retrieval logic
        if self.dir_path == "":
            self.set_dir_path()
        if scenarios != None:
            list_scenarios = np.setdiff1d(os.listdir(self.dir_path), ["input"])
            list_df = [
                pd.read_parquet(os.path.join(self.dir_path, scenario, variable))["value"].unstack("time")
                for scenario in list_scenarios
            ]
            return pd.concat(list_df, keys=list_scenarios, names=["Scenario"])
        if t == None:
            return pd.read_parquet(os.path.join(self.dir_path, self.run_name, variable))["value"].unstack("time")
        else:
            return pd.read_parquet(
                os.path.join(
                    self.dir_path,
                    self.run_name,
                    variable,
                    str(t) + ".mater",
                )
            )[
                "value"
            ].unstack("time")[t]

    def _inputs_setup(self, input_file: str):
        r"""
        Initialize the model inputs by loading and processing data from an Excel file.

        This method reads an :ref:`Excel file <input>` containing various sheets that correspond to different components
        of the model's input data. It processes each sheet to format and interpolate the data for use in
        simulations, and then saves the processed data in a structured format.

        :param input_file: A string specifying the path to the Excel file relative to the "mater" directory.
                           This file should contain all necessary sheets for the model inputs.
        :type input_file: str

        Procedure
        ---------
        1. **Reading the Excel File:**
           The file is loaded with all sheets being read into a dictionary of DataFrames, where each key
           represents a sheet name corresponding to a specific input.

        2. **Processing Vector Data:**
           Extracts vector data from the 'vectors' sheet, which includes the items of each dimension (location, object).
           These are stored in a dictionary attribute `self.vector` used for pandas.DataFrame.index mapping in the rest of the model.

        3. **Processing Other Inputs:**
           For other sheets, the method sets appropriate indices based on common dimensions found across the
           dataset, performs linear interpolation to fill gaps in the timeline, and extrapolates where necessary
           to cover the entire model timeframe from 1900 to 2100.

        4. **Saving Processed Data:**
           Each processed DataFrame is saved in a Parquet file for efficient storage and retrieval. The files
           are organized by creating directories named after the run and scenario names, and the input type.

        Notes
        -----
        It is essential that the Excel file is correctly formatted with the expected sheets and that directory
        paths for saving outputs are accessible and writable.
        """
        # read the input Excel file
        path = os.path.join(self.dir_path, input_file)
        input_dict = pd.read_excel(path, sheet_name=None)

        # create input and vector dictionnaries
        self.inputs = {}
        self.vector = {}
        # extracting inputs from the Excel file by sheets
        for input in input_dict:
            # specific process for the "vectors" sheet
            if input == "vectors":
                df = input_dict[input]
                for vector in df.columns.values:
                    self.vector[vector] = list(df[vector].dropna().values)
                self.vector["controlled_object"] = (
                    self.vector["exogenous_controlled_object"] + self.vector["endogenous_controlled_object"]
                )
                self.vector["object"] = self.vector["controlled_object"] + self.vector["free_object"]
            else:
                df = input_dict[input]
                df.set_index(
                    list(
                        set(df.columns).intersection(
                            [
                                "object",
                                "object_composition",
                                "object_downgrading",
                                "object_Su",
                                "object_efficiency",
                                "location",
                                "production_location",
                                "process",
                                "unit",
                            ]
                        )
                    ),  # list of all the possible dimensions of the inputs
                    inplace=True,
                )
                # reindex the dataframe with the adequate timeframe
                df2 = pd.DataFrame(
                    data=np.nan,
                    index=df.index,
                    columns=np.arange(1900, 2101, 1),
                )
                df2 = df2.add(df, fill_value=0)  # to do panda.reindex

                # linear interpolation and extrapolation on the full timeframe
                df2.interpolate(axis=1, limit_direction="both", inplace=True)
                df2.columns.name = "time"
                os.makedirs(
                    os.path.join(self.dir_path, self.run_name, input),
                    exist_ok=True,
                )

                # save the inputs into parquet format
                df2.stack(dropna=False).to_frame("value").to_parquet(
                    os.path.join(self.dir_path, self.run_name, input, input + ".mater"),
                    engine="pyarrow",
                    compression="snappy",
                )

                # update inputs dictionnary
                self.inputs[input] = df2.droplevel("unit")

    def _outputs_initialization(self):
        r"""
        Initialize the dictionaries for storing simulation outputs and set up initial conditions for the simulation model.

        This method prepares initial states and operational structures for the simulation, focusing on key attributes stored in the outputs dictionaries. It processes historical data to set initial conditions for various simulation scenarios.

        Attributes and calculation
        --------------------------
        - `outputs`: Dictionary to store overall outputs of the simulation.
        - `outputs1`: Dictionary to store outputs at the time :math:`k-1`.
        - `Time`: DataFrame to track the simulation time and apply decay functions.

        - **In-use Stock Initialization**:
            Sets up the in-use stock to the historical stock initial value

            .. math::
                S^u_{l,o}(k_0-1,k_0-1) = S^h_{l,o}(k_0-1)
                :label: in_use_stock_init

            Where:

            - :math:`S^u_{l,o}(k_0-1,k_0-1)` is the `in_use_stock` output at `time` :math:`k_0-1` and `production_date` :math:`k_0-1`.
            - :math:`S^h_{l,o}(k_0-1)` is the :ref:`historical_in_use_stock <input>` input at `time` :math:`k_0-1`.
            - :math:`k_0` is the `simulation_start_time` input.
            - indices are the :ref:`variables dimensions <dimensions>`.

        - **Self-disposal flow**:
            Initializes the self-disposal flow at production date :math:`k_0` using the decay function :eq:`exponential_decay` :

            .. math::
                A^d_{l,o,t}(k_0-1) = d^{l,o}_{l,o}[t,L^m_{l,o,t},k_0-1] \, S^u_{l,o}(k_0-1,k_0-1)
                :label: self_disposal_flow_calc

            Where:

            - :math:`A^d_{l,o,t}(k_0-1)` is the `self_disposal_flow` output at `production_date` :math:`k_0-1`.
            - :math:`d^e_{l,o}` is the `exponential_decay` function :eq:`exponential_decay`.
            - :math:`S^u_{l,o}(k_0-1,k_0-1)` is the `in_use_stock` output :eq:`in_use_stock_init` at `time` :math:`k_0-1` and `production_date` :math:`k_0-1`.
            - :math:`k_0` is the `simulation_start_time` input.
            - :math:`t` is the `Time` input.
            - :math:`L^m_{l,o,t}` is the `lifetime_mean_value` input.
            - indices are the :ref:`variables dimensions <dimensions>`.
        """
        # outputs (dictionnary of all the outputs)
        self.outputs = {}
        # outputs1 (outputs dictionnary at time k-1)
        self.outputs1 = {}
        # in-use stock
        df = (
            self.inputs["historical_in_use_stock"]
            .reorder_levels(["location", "object"])[self.simulation_start_time - 1]
            .copy()
        )
        self.outputs1["in_use_stock"] = (
            pd.concat([df], keys=[self.simulation_start_time - 1], names=["production_date"])
            .reorder_levels(["location", "object", "production_date"])
            .replace(0, np.nan)
        )
        # old stock
        self.outputs1["old_stock"] = pd.Series(data=np.nan, index=self.outputs1["in_use_stock"].index)
        # reference_stock
        self.outputs1["reference_stock"] = df.loc[:, self.vector["endogenous_controlled_object"]]
        # control_flow
        self.outputs1["control_flow"] = pd.Series(data=np.nan, index=self.inputs["historical_in_use_stock"].index)
        # self-disposal flow
        time = np.arange(self.simulation_start_time, self.simulation_end_time + 1, 1)
        self.time = pd.DataFrame(
            data=[time] * len(self.inputs["lifetime_mean_value"].index),
            index=self.inputs["lifetime_mean_value"].index,
            columns=time,
        )
        self.time.columns.name = "time"
        df = _exponential_decay(
            self.time,
            self.inputs["lifetime_mean_value"],
            self.simulation_start_time - 1,
        )
        self.outputs["self_disposal_flow"] = (
            df.mul(self.outputs1["in_use_stock"], axis=0)
            .dropna(axis=0, how="all")
            .reorder_levels(["location", "object", "production_date"])
        )  # create the first data in self-disposal flow with in-use stock of simulation start time being exponentially depreciated over the futur times

    def _process_reference_capacity_computation(self):
        r"""
        Compute the reference capacity for processes based on maximum capacity values.

        This method updates the :ref:`process_reference_capacity <input>` by scaling it with the :ref:`process_max_capacity <input>`. It multiplies these values, using a fill value of 1 where data is missing, and drops any rows that result in all NaNs.

        Calculation
        -----------
        .. math::
            c^{\text{ref}}_{l,p,o,t} = c^{\text{refs}}_{l,p,o,t} \odot c^{\text{max}}_{l,p,o,t}
            :label: process_reference_capacity_calc

        Where:

        - :math:`c^{\text{ref}}_{l,p,o,t}` is the `process_reference_capacity` output.
        - :math:`c^{\text{refs}}_{l,p,o,t}` is the :ref:`process_reference_capacity <input>` input. It is a share of the :ref:`process_max_capacity <input>` input.
        - :math:`c^{\text{max}}_{l,p,o,t}` is the :ref:`process_max_capacity <input>` input.
        - :math:`\odot` the `Hadamard product <https://en.wikipedia.org/wiki/Hadamard_product_(matrices)#:~:text=In%20mathematics%2C%20the%20Hadamard%20product,of%20the%20multiplied%20corresponding%20objects.>`_ of two matrices or vectors.
        - indices are the :ref:`variables dimensions <dimensions>`.
        """
        self.process_reference_capacity = (
            self.inputs["process_reference_capacity"]
            .mul(self.inputs["process_max_capacity"], fill_value=1)
            .dropna(axis=0, how="all")
        )

    def _reference_intensity_of_use_coputation(self):
        r"""
        Compute the reference intensity of use for each process.

        This method calculates the `reference_intensity_of_use` :math:`u_{\text{ref}}` by multiplying the process shares by the reference capacities. It then ensures that the resulting DataFrame has no rows filled entirely with NaNs and reorders the DataFrame levels to ["location", "object", "process"] for consistent access and manipulation.

        Calculation
        -----------
        .. math::
            u^{\text{ref}}_{l,p,o,t} = s^p_{l,p,o,t} \odot c^{\text{ref}}_{l,p,o,t}
            :label: ref_intensity_of_use_calc

        Where:

        - :math:`u^{\text{ref}}_{l,p,o,t}` is the `reference_intensity_of_use` output.
        - :math:`s^p_{l,p,o,t}` is the :ref:`process_share <input>` input, representing the distribution of each process across different productive objects.
        - :math:`c^{\text{ref}}_{l,p,o,t}` is the :ref:`process_reference_capacity <input>` input, representing the production capacity of each process.
        - :math:`\odot` the `Hadamard product <https://en.wikipedia.org/wiki/Hadamard_product_(matrices)#:~:text=In%20mathematics%2C%20the%20Hadamard%20product,of%20the%20multiplied%20corresponding%20objects.>`_ of two matrices or vectors.
        - indices are the :ref:`variables dimensions <dimensions>`.
        """
        self.outputs["reference_intensity_of_use"] = (
            self.inputs["process_shares"].mul(self.process_reference_capacity).dropna(axis=0, how="all")
        ).reorder_levels(["location", "object", "process"])

    def _exogenously_controlled_process_computation(self):
        r"""
        Compute the processes for exogenously controlled objects.

        This method calculates the `exogenously_controlled_process` :math:`P^{\text{exo}}` attribute by multiplying the exogenous stock values by the reference intensity of use, calculated previously in :eq:`ref_intensity_of_use_calc`. The method ensures that the resulting DataFrame is free from rows entirely filled with NaNs and reorders the DataFrame levels to ["location", "object", "process"] for consistent access.

        Calculation
        -----------
        .. math::
            P^{\text{exo}}_{l,p,o,t} = S^{\text{exo}}_{l,p,o,t} \odot u^{\text{ref}}_{l,p,o,t}
            :label: exogenously_controlled_process_calc

        Where:

        - :math:`P^{\text{exo}}_{l,p,o,t}` is the `exogenously_controlled_process` output.
        - :math:`S^{\text{exo}}_{l,p,o,t}` is the :ref:`exogenous_stock <input>` input.
        - :math:`u^{\text{ref}}_{l,p,o,t}` is the `reference_intensity_of_use` output :eq:`ref_intensity_of_use_calc`.
        - :math:`\odot` the `Hadamard product <https://en.wikipedia.org/wiki/Hadamard_product_(matrices)#:~:text=In%20mathematics%2C%20the%20Hadamard%20product,of%20the%20multiplied%20corresponding%20objects.>`_ of two matrices or vectors.
        - indices are the :ref:`variables dimensions <dimensions>`.
        """
        self.exogenously_controlled_process = (
            self.inputs["exogenous_stock"].mul(self.outputs["reference_intensity_of_use"]).dropna(axis=0, how="all")
        ).reorder_levels(["location", "object", "process"])

    def _control_flow_trade_inverse_computation(self):
        r"""
        Compute the inverse of the control flow trade matrix.

        This method calculates the inverse (pseudoinverse) of the `control_flow_trade` matrix. The inverse is used to model the reverse dynamics of trade flows between production locations over time.

        Calculation
        -----------
        The pseudoinverse of the control flow trade matrix :math:`T^{c^{-1}}` is computed.

        .. math::
            T^{c^{-1}}_{l_p,o,l,t} = \text{pseudoinverse}_{l_p,o,l,t}[T^c_{l,o,l_p,t}]
            :label: trade_inverse_calc

        Where:

        - :math:`T^{c^{-1}}_{l_p,o,l,t}` is the `control_flow_trade_inverse_matrix` output.
        - :math:`T^c_{l,o,l_p,t}` is the :ref:`control_flow_trade <input>` input.
        - :math:`\text{pseudoinverse}_{l_p,o,l,t}` is the :ref:`pseudoinverse function <pseudoinverse_computation>`.
        - indices are the :ref:`variables dimensions <dimensions>`.

        Notes
        -----
        It is assumed that `self.inputs` contains a complete and appropriately structured `control_flow_trade` matrix before this method is called. Missing values or incorrect data structures can affect the accuracy and feasibility of the pseudoinverse computation.
        """
        to_inverse = self.inputs["control_flow_trade"].unstack("production_location").stack("time").fillna(0)
        grouped = to_inverse.groupby(level=["object", "time"])
        pseudoinverses = grouped.apply(_compute_pseudoinverse).reset_index()
        pseudoinverses["production_location"] = [self.vector["location"]] * len(pseudoinverses)
        pseudoinverses = pseudoinverses.explode(["production_location", 0])
        pseudoinverses["location"] = [self.vector["location"]] * len(pseudoinverses)
        pseudoinverses = pseudoinverses.explode(["location", 0])
        self.control_flow_trade_inverse_matrix = pseudoinverses.set_index(
            ["production_location", "object", "location", "time"]
        )[0].unstack("time")

    def _lifetime_computation(self):
        r"""
        Compute the log-normal parameters for lifetime data based on the mean values and standard deviations provided.

        This method transforms the raw lifetime mean values and standard deviations into log-normal distribution parameters (logarithmic mean and standard deviation). These parameters are used for probabilistic modeling of lifetime distributions within the system, facilitating more accurate and statistically relevant computations.

        Calculation
        -----------
        1. **Standard Deviation Transformation:**
            The standard deviation input is a share of the lifetime mean value. The first step is to multiply both inputs to calculate the real extensive value of the lifetime standard deviation:

            .. math::
                L^{sd}_{l,o,t} = L^{sds}_{l,o,t} \odot L^m_{l,o,t}
                :label: lifetime_standard_deviation

            Where:

            - :math:`L^{sd}_{l,o,t}` is the `lifetime_standard_deviation` output.
            - :math:`L^{sds}_{l,o,t}` is the :ref:`lifetime_standard_deviation <input>` input.
            - :math:`L^m_{l,o,t}` is the :ref:`lifetime_mean_value <input>` input.
            - :math:`\odot` the `Hadamard product <https://en.wikipedia.org/wiki/Hadamard_product_(matrices)#:~:text=In%20mathematics%2C%20the%20Hadamard%20product,of%20the%20multiplied%20corresponding%20objects.>`_ of two matrices or vectors.
            - indices are the :ref:`variables dimensions <dimensions>`.

        2. **Log-normal Standard Deviation Computation:**
            Calculates the log-normal standard deviation :math:`\sigma`: by applying the following formula:

            .. math::
                \sigma_{l,o,t} = \sqrt{\ln(1+(\frac{L^{sd}_{l,o,t}}{L^m_{l,o,t}})^{2})}
                :label: lifetime_standard_deviation_log

            Where:

            - :math:`\sigma_{l,o,t}` is the `lifetime_standard_deviation_log` output.
            - :math:`L^{sd}_{l,o,t}` is the `lifetime_standard_deviation` output :eq:`lifetime_standard_deviation`.
            - :math:`L^m_{l,o,t}` is the :ref:`lifetime_mean_value <input>` input.
            - indices are the :ref:`variables dimensions <dimensions>`.

        3. **Logarithmic Mean Computation:**
            Computes the log-normal mean value :math:`\mu` :

            .. math::
                \mu_{l,o,t} = \ln(L^m_{l,o,t}) - \frac{1}{2(\sigma_{l,o,t})^{2}}
                :label: lifetime_mean_value_log

            Where :

            - :math:`\mu_{l,o,t}` is the `lifetime_mean_value_log` output.
            - :math:`L^m_{l,o,t}` is the :ref:`lifetime_mean_value <input>` input.
            - :math:`\sigma_{l,o,t}` represents the `lifetime_standard_deviation_log` output :eq:`lifetime_standard_deviation_log`.
            - indices are the :ref:`variables dimensions <dimensions>`.
        """
        lifetime_standard_deviation = self.inputs["lifetime_mean_value"].mul(self.inputs["lifetime_standard_deviation"])

        self.lifetime_standard_deviation_log = np.sqrt(
            np.log(1 + (lifetime_standard_deviation / self.inputs["lifetime_mean_value"]) ** 2)
        ).dropna(axis=0, how="all")

        self.lifetime_mean_value_log = (
            np.log(self.inputs["lifetime_mean_value"]) - 1 / 2 * self.lifetime_standard_deviation_log**2
        ).dropna(axis=0, how="all")
