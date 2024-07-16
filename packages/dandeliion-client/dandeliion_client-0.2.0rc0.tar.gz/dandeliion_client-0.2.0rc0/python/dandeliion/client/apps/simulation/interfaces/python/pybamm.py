import numpy as np
from dataclasses import dataclass

from pybamm import Experiment
from pybamm.experiment.step.steps import Current
import json

from .connection import connect
from .simulation import Simulation
from dandeliion.client.apps.simulation.core.models.export import BPX
from dandeliion.client.tools.misc import unflatten_dict, update_dict


models = {
    'DFN': 'Battery_Pouch_1D',
}

discretizations = {
}

initial_condition_fields = {
    'Initial temperature [K]': 'params.cell.T0',
    'Initial concentration in electrolyte [mol.m-3]': 'params.cell.c0',
    'Initial state of charge': 'params.cell.Z0',
}

sim_params = {
    'x_n': 'params.anode.N',
    'x_s': 'params.separator.N',
    'x_p': 'params.cathode.N',
    'r_n': 'params.anode.M',
    'r_p': 'params.cathode.M',
}


@dataclass
class Simulator:
    # server: str
    credential: tuple[str, str]


@dataclass
class DandeliionExperiment:
    current: dict
    t_output: list
    t_max: float
    V_min: float


def convertExperiment(
        experiment: Experiment,  # pybamm Experiment
        dt_eval: float,  # sets minimum step size for discretisation
) -> DandeliionExperiment:

    # check for termination condition (max time, min voltage opt., others fail)
    V_min = experiment.termination.get('voltage', None)

    t_max = None
    t_output = None
    if 'time' in experiment.termination:
        t_max = experiment.termination['time']  # seconds
        t_output = np.arange(0., t_max, experiment.period)

    # check for unsupported termination conditions
    if set(experiment.termination.keys()) - {'time', 'voltage'}:
        raise NotImplementedError("Only supported termination conditions are 'time' and 'voltage'")

    # build current input based on Current steps
    current = {'x': [], 'y': []}   # x -> t[s], y -> I[A]
    for step in experiment.steps:
        if step.start_time:
            raise NotImplementedError('Dandeliion does not support experiment steps with start times yet.')
        if not isinstance(step, Current):
            raise NotImplementedError('Dandeliion only supports Current steps for experiments so far.')
        if not step.duration:
            raise NotImplementedError('Dandeliion only supports steps with explicity defined durations.')
        if current['x']:
            last_final = current['x'][-1]
            current['x'].append(last_final + dt_eval)
            current['x'].append(last_final + step.duration)
            current['y'].append(-1. * step.value)
            current['y'].append(-1. * step.value)
        else:
            current['x'].append(0)
            current['x'].append(step.duration - dt_eval)
            current['y'].append(-1. * step.value)
            current['y'].append(-1. * step.value)

    # TODO should we /do we need to extrapolate current to t_max?

    return DandeliionExperiment(
        current=current,
        t_output=t_output,
        V_min=V_min,
        t_max=t_max,
    )


class Solution:
    def __init__(self, sim: Simulation):
        self._results = sim.results

    def __getitem__(self, key: str):
        if key == "Time [s]":
            return self._results.total_voltage['t(s)']
        elif key == "Voltage [V]":
            return self._results.total_voltage['total_voltage(V)']
        elif key == "Current [A]":
            return self._results.total_current['total_current(A)']
        else:
            raise KeyError(f'The following key is not (yet) found in the provided results: {key}')


def solve(
        simulator: Simulator,
        params: str,
        model: str,
        experiment: Experiment,
        initial_condition: dict,
        var_pts: dict,
        t_output: dict = None,
        dt_eval: float = 0.1,
) -> Solution:

    connect(
        username=simulator.credential[0],
        password=simulator.credential[1],
        # endpoint=f'{simulator.server}/accounts/',  # TODO
    )

    with open(params) as f:
        data = BPX.import_(data=json.load(f), model=models[model])
    # add/overwrite initial conditions
    update_dict(data, unflatten_dict(
        {initial_condition_fields[field]: value
         for field, value in initial_condition.items()}
    ))

    # add/overwrite simulation params
    update_dict(data, unflatten_dict(
        {sim_params[field]: value
         for field, value in var_pts.items()}
    ))

    # fix discretisation to FECV (default)
    data['params']['discretisation'] = 'FECV'

    # convert Experiment into something Dandeliion can use
    experiment = convertExperiment(experiment, dt_eval)

    # set V_min if provided in Experiment
    if experiment.V_min is not None:
        data['params']['cell']['V_min'] = experiment.V_min

    # set charge/discharge current
    data['params']['cell']['current'] = experiment.current

    # set output times and t_max
    if t_output is None and experiment.t_output is None:
        raise ValueError('Either Experiment has to provide time termination condition'
                         + ' or output list t_output has to be exlicitly provided to this function')

    if t_output is None:
        # set output times
        data['params']['cell']['t_output'] = experiment.t_output.tolist()
        # set maximum discharge time
        data['params']['cell']['t_max'] = experiment.t_max
    else:
        data['params']['cell']['t_output'] = t_output.tolist()
        if experiment.t_max is not None:
            data['params']['cell']['t_max'] = experiment.t_max
        else:
            data['params']['cell']['t_max'] = t_output[-1]

    data['agree'] = True

    # run simulation
    sim = Simulation(
        data=data,
        # endpoint_results=f'{simulator.server}/results/',  # TODO
    )
    sim.compute()

    return Solution(sim)
