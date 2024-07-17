"""
Model module to create the MATER class.
"""

import logging
from tqdm import trange

from mater.core._non_physical import _MaterProcessNonPhysical

# from mater.core.utils import profile


class Mater(_MaterProcessNonPhysical):

    def __init__(self):
        super().__init__()

    # @profile
    def run(
        self,
        scenario_name: str,
        simulation_start_time: int = 1901,
        simulation_end_time: int = 2100,
        input_file: str = "MATER_v0-1-2.xls",
    ):
        """Run the MATER model.

        Execute a run of the MATER model from `simulation_start_time` to `simulation_end_time` using the input frome the `input_file`.
        The outputs are then stored in a `scenario_name` directory in Parquet files.

        :param scenario_name: Name of the scenario to run. It will create a new directory in your working directory containing all the output data in Parquet files.
        :type scenario_name: str
        :param simulation_start_time: The simulation initial time. It needs to be at least one step above the minimal time value of the input data, defaults to 1901
        :type simulation_start_time: int, optional
        :param simulation_end_time: The simulation final time, defaults to 2100
        :type simulation_end_time: int, optional
        :param input_file: The name of the input Excel file. It has to be in the directory of your project, defaults to "MATER_demonstrator.xls"
        :type input_file: str, optional
        """
        # Run parameters setup

        self.simulation_start_time = simulation_start_time
        self.simulation_end_time = simulation_end_time
        self.sampling_period = 1  # in time
        if self.dir_path == "":
            self.set_dir_path()
        self.run_name = scenario_name

        # Inputs loading

        logging.info("Inputs loading...")
        self._inputs_setup(input_file)

        # Model simulation

        logging.info("Model simulation...")
        self._outputs_setup()
        pbar = trange(
            self.simulation_start_time,
            self.simulation_end_time + 1,
            self.sampling_period,
            disable=False,
        )
        for k in pbar:
            pbar.set_description(str(k))
            self._self_disposal_recycling_control_flows_computation(k)
            self._processes_computation(k)
            self._extraneous_flows_computation(k)
            self._objects_computation(k)
            self._outputs_update(k)
            self._outputs_save(k)
        pbar.close()

    # Sub-methods of the run method

    def _outputs_setup(self):
        r"""
        Set up and initialize all necessary outputs for the MATER simulation model.

        This method orchestrates the initialization and configuration of various model outputs and parameters that can be computed outside the for loop for performance issues.

        Summary of Operations
        ---------------------
        - :meth:`_outputs_initialization`: Prepares the outputs dictionary and sets initial conditions based on historical data. This involves initializing dictionaries to store simulation results across different time steps.
        - :meth:`_lifetime_computation`: Transforms raw lifetime data into log-normal distribution parameters suitable for the modeling of lifetime distributions for the objects.
        - :meth:`_process_reference_capacity_computation`: Calculates reference capacities of process by objects based on their maximum capacities, adjusting for data availability.
        - :meth:`_reference_intensity_of_use_coputation`: Calculates the reference intensity of use of each object per time period.
        - :meth:`_exogenously_controlled_process_computation`: Calculates the reference processes of the exogenously controlled objects such as cars or residential buildings.
        - :meth:`_control_flow_trade_inverse_computation`: Computes the inverse of the control flow trade matrix.
        """
        self._outputs_initialization()
        self._lifetime_computation()
        self._process_reference_capacity_computation()
        self._reference_intensity_of_use_coputation()
        self._exogenously_controlled_process_computation()
        self._control_flow_trade_inverse_computation()

    def _self_disposal_recycling_control_flows_computation(self, k: int):
        r"""
        Manage the computation of self-disposal, recycling, and control flows at a specific simulation time point :math:`k`.

        First the self-disposal flow is calculated as a log-normal delay of the control flow. The recycling flow is a share of the self-disposal flow, the control flow is calculated as the state feedback command to track the reference in stock.
        Finally these control flows are spread between location for production.

        :param k: the current simulation `time`
        :type k: int

        Operations Summary
        ------------------
        - :meth:`_log_normal_distribution_computation`: Initializes the calculation of log-normal distribution parameters, which are essential for modeling variable lifetime distributions.
        - :meth:`_self_disposal_flow_computation`: Utilizes the log-normal distributions to estimate the rate of cohort arriving at their end of life.
        - :meth:`_recycling_flow_computation`: Calculates how much of the disposed material is successfully recycled, based on current collection rates and the efficiency of recycling processes.
        - :meth:`_control_flow_computation`: Adjusts resource usage and disposal based on predefined control strategies aimed at achieving stock targets.
        - :meth:`_traded_control_flow_computation`: Modifies control flows to account for trade and exchange of resources between different production locations, ensuring the model captures economic interactions and dependencies.
        """
        self._log_normal_distribution_computation(k)
        self._self_disposal_flow_computation(k)
        self._recycling_flow_computation(k)
        self._control_flow_computation(k)
        self._traded_control_flow_computation(k)

    def _processes_computation(self, k: int):
        r"""
        Coordinate the computation of various types of processes within the MATER model at a specific time point :math:`k`.

        This method orchestrates the calculation of endogenously controlled, controlled, free, and total processes to accurately simulate the interactions and dependencies within the model's ecosystem. These calculations reflect both internally controlled adjustments and naturally occurring flows.

        :param k: the current simulation `time`
        :type k: int

        Operations Summary
        ------------------
        - :meth:`_endogenously_controlled_process_computation`: Determines the processes influenced by internal management strategies that account for traded control flows and recycling outputs.
        - :meth:`_controlled_process_computation`: Integrates both endogenously controlled processes and exogenous interventions, providing a holistic view of controlled environmental impacts.
        - :meth:`_free_process_computation`: Computes the unmanaged or free-flowing processes driven by previous time stock levels and current usage intensities.
        - :meth:`_process_computation`: Aggregates controlled and free processes to generate a comprehensive output that reflects total system flows.

        Key Calculations
        ----------------
        The model uses the following formula to aggregate these computations:

        .. math::
            P_{l,p}(k) = \sum_{e}[(P^{endo}_{l,o,p}(k) + P^{exo}_{l,o,p}(k)) + P^{free}_{l,o,p}(k)]
            :label: total_process_aggregation

        Where:

        - :math:`P_{l,p}(k)` represents the total processes.
        - :math:`P^{endo}_{l,o,p}(k)` and :math:`P^{exo}_{l,o,p}(k)` are outputs from endogenously and exogenously controlled processes respectively.
        - :math:`P^{free}_{l,o,p}(k)` denotes the contribution from free processes.
        - indices are the :ref:`variables dimensions <dimensions>`.

        Notes
        -----
        This method relies on accurate data from both control and free flow processes. Errors in upstream data can significantly impact the reliability and accuracy of the model's outputs. Additionally, this method integrates several complex calculations, each requiring careful consideration of temporal dynamics and operational scales.
        """
        self._endogenously_controlled_process_computation(k)
        self._controlled_process_computation(k)
        self._free_process_computation(k)
        self._process_computation(k)

    def _extraneous_flows_computation(self, k: int):
        r"""
        Compute and integrate various flows contributing to extraneous system outputs at a specific time point :math:`k`.

        This method coordinates the computation of control flow compositions, secondary production flows, thermodynamic process flows, and extraneous flows. These components reflect complex interactions and efficiency considerations within the model's production systems, emphasizing how controlled, recycled, and thermodynamic processes impact the overall system efficiency and output.

        :param k: the current simulation `time`
        :type k: int

        Overview of Operations
        ----------------------
        - :meth:`_control_flow_composition_computation`: Determines the distribution of control flows across objects, adjusted for trade and object compositions.
        - :meth:`_secondary_production_flow_computation`: Calculates the contributions of recycled materials to secondary production, integrating object composition impacts.
        - :meth:`_thermodynamic_process_flow_computation`: Assesses energy and material flows within the system's processes, adjusting for both control and secondary production influences.
        - :meth:`_extraneous_flow_computation`: Enhances the system's output calculations by integrating object-specific efficiencies with thermodynamic flows.

        Key Formulas and Concepts
        -------------------------
        The method integrates these computations to assess the overall extraneous flows through a series of matrix operations, which balance production dynamics against recycling and control strategies. The primary equation used to aggregate these flows is:

        .. math::
            A^e_{l}(k) = A^{thP}_{l}(k) + \sum_{e_s}[E^{eff}_{l,o_s}(k) \odot A^{thP}_{l,o_s}(k)]
            :label: extraneous_flow_aggregation

        Where:

        - :math:`A^e_{l}(k)` represents the total extraneous flows at time `k`.
        - :math:`A^{thP}_{l}(k)` is the aggregated thermodynamic process flows.
        - :math:`E^{eff}_{l,o_s}(k)` and :math:`A^{thP}_{l,o_s}(k)` are the efficiency and thermodynamic flows adjusted for specific objects and scenarios, illustrating how efficiencies modulate the system's outputs.
        - indices are the :ref:`variables dimensions <dimensions>`.
        """
        self._control_flow_composition_computation(k)
        self._secondary_production_flow_computation(k)
        self._thermodynamic_process_flow_computation(k)
        self._extraneous_flow_computation(k)

    def _objects_computation(self, k: int):
        r"""
        Calculate the object stock dynamics within the MATER model at a specific time point :math:`k`.

        This method manages the computation of three core stock types within the system: reference, old, and in-use stocks. These calculations are pivotal for maintaining accurate material flow accounts and ensuring the integrity of the model's state at each simulation step.

        :param k: the current simulation `time`
        :type k: int

        Overview of Operations
        ----------------------
        - :meth:`_reference_stock_computation`: Computes the reference stocks for endogenously controlled objects based on their controlled processes and usage intensities.
        - :meth:`_old_stock_computation`: Adjusts old stocks by considering the material that has either been disposed of or recycled.
        - :meth:`_in_use_stock_computation`: Updates in-use stocks by integrating net changes due to control flows, extraneous influences, and self-disposal.
        """
        self._reference_stock_computation(k)
        self._old_stock_computation(k)
        self._in_use_stock_computation(k)
