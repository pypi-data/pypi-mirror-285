"""
This module creates the MATER processing class.
"""

import pandas as pd

pd.options.mode.chained_assignment = None  # default='warn'

import numpy as np
from mater.core._bio_physical import _MaterProcessBioPhysical

### Main model


class _MaterProcessNonPhysical(_MaterProcessBioPhysical):
    """The MATER processing class."""

    def __init__(self):
        super().__init__()

    def _recycling_flow_computation(self, k: int):
        r"""
        Compute the recycling flow for each product based on the self-disposal flow and the collection rate at a given time point.

        This method calculates the recycling flow by multiplying the self-disposal flow at time :math:`k` with the collection rate at the same time. The result provides an estimation of the actual amount of material that is recycled, considering how much of the disposed material is effectively collected for recycling.

        :param k: the current simulation `time`.
        :type k: int

        Calculation
        -----------
        The recycling flow is computed as:

        .. math::
            A^r_{l,o,d}(k) = A^d_{l,o,d}(k) \odot \tau^c_{l,o}(k)
            :label: recycling_flow_calc

        Where:

        - :math:`A^r_{l,o,d}(k)` is the `recycling_flow` output at `time` :math:`k`.
        - :math:`A^d_{l,o,d}(k)` is the `self_disposal_flow` output :eq:`self_disposal_flow_calc` at `time` :math:`k`.
        - :math:`\tau^c_{l,o}(k)` is the :ref:`collection_rate <input>` input at `time` :math:`k`, which determines the proportion of disposed material that is collected for recycling.
        - :math:`\odot` the `Hadamard product <https://en.wikipedia.org/wiki/Hadamard_product_(matrices)#:~:text=In%20mathematics%2C%20the%20Hadamard%20product,of%20the%20multiplied%20corresponding%20objects.>`_ of two matrices or vectors. In the case where the dimensions of both matrices or vectors are different, the missing dimensions are added with replicate values before performing the product.
        - indices are the :ref:`variables dimensions <dimensions>`.
        """
        self.outputs["recycling_flow"] = (
            self.outputs["self_disposal_flow"][k].mul(self.inputs["collection_rate"][k]).dropna(axis=0, how="all")
        )  # .dropna(axis=0, how="all")

    def _control_flow_computation(self, k: int):
        r"""
        Compute the control flow for a specific time point :math:`k` based on reference stocks, in-use stocks, and self-disposal flows.

        This method calculates the control flow using a feedforward control strategy that considers the current state of the stocks and the expected disposal flows to adjust for deviations from desired stock levels. The control is adjusted to maintain non-negative values, reflecting feasible operational flows.

        :param k: the current simulation `time`.
        :type k: int

        Calculation
        -----------
        The control flow is computed as follows:

        .. math::
            A^c_{l,o}(k) = \max\left(\left(S^{\text{exo}}_{l,o}(k) + S^{\text{ref}}_{l,o}(k-1) - \sum_{d}[S^u_{l,o,d}(k-1) + A^d_{l,o,d}(k)]\right), 0\right)
            :label: control_flow_calc

        Where:

        - :math:`A^c_{l,o}(k)` is the `control_flow` output at `time` :math:`k`.
        - :math:`S^{\text{exo}}_{l,o}(k)` is the :ref:`exogenous_stock <input>` input at `time` :math:`k`.
        - :math:`S^{\text{ref}}_{l,o}(k-1)` is the `reference_stock` output :eq:`reference_stock_computation` at `time` :math:`k-1`.
        - :math:`S^u_{l,o,d}(k-1)` is the `in_use_stock` output :eq:`in_use_stock_computation` at `time` :math:`k-1`.
        - :math:`A^d_{l,o,d}(k)` represents the `self_disposal_flow` output :eq:`self_disposal_flow_calc` at `time` :math:`k`.
        - indices are the :ref:`variables dimensions <dimensions>`.
        """
        # control flow with a feedforward
        reference_stock = (
            self.inputs["exogenous_stock"][k]
            .add(
                self.outputs1["reference_stock"],
                fill_value=0,
            )
            .reorder_levels(["location", "object"])
        )
        full_state_feedback = reference_stock.sub(
            self.outputs1["in_use_stock"].groupby(level=["location", "object"]).sum().loc[reference_stock.index],
            fill_value=0,
        )
        feedforward = full_state_feedback.add(
            self.outputs["self_disposal_flow"][k].groupby(level=["location", "object"]).sum(),
            fill_value=0,
        ).loc[:, self.vector["controlled_object"]]
        # positivity of control_flow
        self.outputs["control_flow"] = feedforward.loc[feedforward.index[feedforward > 0]]

    def _reference_stock_computation(self, k: int):
        r"""
        Compute the reference stock for the endogenously controlled objects at time point :math:`k`.

        This method calculates the reference stock levels by dividing the endogenously controlled reference process by the reference intensity of use at time :math:`k`.

        :param k: the current simulation `time`.
        :type k: int

        Calculation
        -----------
        The reference stock is computed as follows:

        .. math::
            S^{ref}_{l,o}(k) = \sum_{p}[\frac{P^{endo}_{l,p}(k)}{u^{\text{ref}}_{l,o,p}(k)}]
            :label: reference_stock_computation

        Where:

        - :math:`S^{ref}_{l,o}(k)` is the `reference_stock` output at `time` :math:`k`.
        - :math:`P^{endo}_{l,p}(k)` is the `endogenously_controlled_process` output :eq:`endo_controlled_process` at `time` :math:`k`.
        - :math:`u^{\text{ref}}_{l,o,p}(k)` corresponds to `reference_intensity_of_use` output :eq:`ref_intensity_of_use_calc` at `time` :math:`k`.
        - indices are the :ref:`variables dimensions <dimensions>`.
        """
        # reference stock as the sum of exogenous stock and the control reference process
        self.outputs["reference_stock"] = (
            self.endogenously_controlled_reference_process.div(self.outputs["reference_intensity_of_use"][k])
            .dropna(axis=0, how="all")
            .groupby(level=["location", "object"])
            .sum()
        )

    def _outputs_save(self, k: int):
        r"""
        Save the model's outputs to durable storage, segregating between frequently saved outputs and those saved only at the end of the simulation.

        This method selectively saves outputs based on their specified storage timing. Most outputs are saved periodically throughout the simulation, except for a designated set of 'long_outputs' which are saved only once at the end of the simulation to optimize storage usage and performance.

        :param k: the current simulation `time`.
        :type k: int

        Method Operation
        ----------------
        - Outputs not listed in `long_outputs` are saved at each call of the method.
        - Outputs listed in `long_outputs` are saved only at the final simulation step (`self.simulation_end_time`).

        Notes
        -----
        The method leverages the helper function `_to_mater` to perform the actual saving process.
        """
        long_outputs = ["self_disposal_flow", "reference_intensity_of_use"]
        for output in np.setdiff1d(list(self.outputs.keys()), long_outputs):
            self._to_mater(output, k)
        if k == self.simulation_end_time:
            for output in long_outputs:
                self._to_mater(output)
