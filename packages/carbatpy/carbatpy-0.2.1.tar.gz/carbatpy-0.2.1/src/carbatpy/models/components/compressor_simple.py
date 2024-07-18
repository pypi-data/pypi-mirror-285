# -*- coding: utf-8 -*-
"""
functions for compressor and expander output state calcultations

so far/here: only for fixed isentropic efficiencies

((Part of carbatpy.))
Created on Sun May 21 08:51:33 2023

@author: atakan
"""

import carbatpy as cb
import numpy as np


def compressor(p_out, eta_s, fluid, m_dot=1.0, calc_type="const_eta",
               name="compressor", plot_info={}):
    """
    compressor or expander output state calculation

    so far only for a constant isentropic efficiency, according to the pressure
    change an expansion or compression is detected and handled.

    Parameters
    ----------

    p_out : float
        output pressure.
    eta_s : float
        isentropic efficiency.
    fluid : fprop.Fluid
        entering fluid, including properties, composition, and model.
    m_dot : float, optional
        mass flow rate (in kg/s). Default is 1
    calc_type : string, optional
        how to calculate, so far, only one implemented. The default is
        "const_eta".
    name : string, optional
        name of the device. The default is "compressor".
    plot_info : dictionary, optional
        if not empty a Figure, an Axes, a list of What shall be plotted,
        a list with the colour/styles and a list with the labels must be
        passed. in "what", the two numbers coincide with the fluid THERMO
        order. The x-shift can be used in cycle calculations, to shift the
        curves, by the value (it will be added).
        The names in the dictionary are: "fig", "ax", "what","col",
        "label", "x-shift". Default is empty.

    Returns
    -------
    state_out : array of float
        compressor output state containing [T,p,h,v,s,q].
    work_specific : float
        work per kg of fluid, positive for compressor; units:J/kg.

    """
    state_in = fluid.properties.state
    expander = False
    if fluid.properties.pressure > p_out:
        expander = True

    if calc_type == "const_eta":
        fluid.set_state(
            [fluid.properties.entropy, p_out], "SP")

        diff_enthalpy_s = fluid.properties.enthalpy-state_in[2]

        if expander:
            work_specific = diff_enthalpy_s * eta_s
        else:
            work_specific = diff_enthalpy_s / eta_s

        state_out = fluid.set_state([state_in[2] + work_specific, p_out], "HP")

    else:
        raise Exception(
            f"The option{calc_type} is not yet implemented for compressors")

    power = m_dot * work_specific
    plot_temp_h_flow(state_in, state_out, m_dot, plot_info)
    #

    return state_out, work_specific, power


def pump(p_out, eta_s, fluid, m_dot=1.0, calc_type="const_eta", name="pump",
         plot_info={}):
    """
    Calculate the exit state of a pump assuming an incompressible fluid.

    Only formulated for constant isentropic efficiency

    Parameters
    ----------
    p_out : float
        output pressure.
    eta_s : float
        isentropic efficiency.
    fluid : fprop.Fluid
        entering fluid, including properties, composition, and model.
    m_dot : float, optional
        mass flow rate (in kg/s). Default is 1
    calc_type : string, optional
        how to calculate, so far, only one implemented. The default is
        "const_eta".
    name : string, optional
        name of the device. The default is "pump".
    plot_info : dictionary, optional
        if not empty a Figure, an Axes, a list of What shall be plotted,
        a list with the colour/styles and a list with the labels must be
        passed. in "what", the two numbers coincide with the fluid THERMO
        order. The x-shift can be used in cycle calculations, to shift the
        curves, by the value (it will be added).
        The names in the dictionary are: "fig", "ax", "what","col",
        "label", "x-shift". Default is empty.

    Returns
    -------
    state_out : array of float
        compressor output state containing [T,p,h,v,s,q].
    work_specific : float
        work per kg of fluid, positive for compressor; units:J/kg.

    """
    state_in = fluid.properties.state
    if calc_type == "const_eta":

        work_is = state_in[3] * (p_out - state_in[1])
        if work > 0:
            work_specific = work_is / eta_s
        else:
            work_specific = work_is * eta_s
        h_out = state_in[2] + work_specific
        state_out = fluid.set_state([h_out, p_out], "HP")
    else:
        raise Exception(
            f"The option{calc_type} is not yet implemented for pumps")
    power = m_dot * work_specific

    plot_temp_h_flow(state_in, state_out, m_dot, plot_info)


    return state_out, work_specific, power

def plot_temp_h_flow(_state_in, _state_out, _m_dot, _plot_info):
    """
    plotting a T-H-dot diagram for simple flows (compressor, throttle etc.)

    Parameters
    ----------
    _state_in : np.array
        entering state [T,p,h,v,s,...].
    _state_out : np.array
        exiting state.
    _m_dot : float
        mass flow rate (kg/s).
    _plot_info : dictionary
        if not empty a Figure, an Axes, a list of What shall be plotted,
        a list with the colour/styles and a list with the labels must be
        passed. in "what", the two numbers coincide with the fluid THERMO
        order. The x-shift can be used in cycle calculations, to shift the
        curves, by the value (it will be added).
        The names in the dictionary are: "fig", "ax", "what","col",
        "label", "x-shift".

    Returns
    -------
    None.

    """
    if len(_plot_info) > 0:
        if _plot_info["what"][0] ==2:
            data = np.array([_state_in[_plot_info["what"][0]] ,
                                  _state_out[_plot_info["what"][0]]]) * _m_dot \
                + _plot_info["x-shift"][0]
            _plot_info["ax"].plot(data,
                                 [_state_in[_plot_info["what"][1]],
                                  _state_out[_plot_info["what"][1]]],
                                 _plot_info["col"][0],
                                 label=_plot_info["label"][0])
        else:
            print(f"Pump: plotting only implemented fot T-H_dot [2,0]. You requested{_plot_info['what']}")




if __name__ == "__main__":
    import matplotlib.pyplot as plt

    FLUID = "Propane * Pentane"
    comp = [.80, 0.2]
    flm = cb.fprop.FluidModel(FLUID)
    myFluid = cb.fprop.Fluid(flm, comp)
    P_LOW = 1e5
    T_IN = 310.
    DT_IN_LIQ = -5
    state_in_act = myFluid.set_state([T_IN, P_LOW], "TP")
    P_OUT = 10e5
    ETA_S = .7
    M_DOT = 1e-3
    fig0, ax0 = plt.subplots()
    PLOT_INFO ={"fig":fig0, "ax":ax0, "what":[2,0],"col":["r:","k"],
    "label":["compressor","xx"], "x-shift":[0,0]}

    # Compressor-------------
    state_o, work, power_c = compressor(P_OUT, ETA_S, myFluid, m_dot=M_DOT,
                                      plot_info=PLOT_INFO)
    print(myFluid.properties.temperature, work)
    print("\nCompressor", state_in_act, "\n", state_o, "\n", state_o-state_in_act)
    PLOT_INFO["col"]=["k",""]
    PLOT_INFO["label"]=["expander",""]
    state_in_c = state_o
    state_o, work, power_e = compressor(P_LOW, ETA_S, myFluid, m_dot=M_DOT,
                                      plot_info=PLOT_INFO)
    print("\nExpander:", state_in_c, "\n", state_o, "\n", state_o-state_in_c, work)

    # Pump, incompressible:

    state_in_p = myFluid.set_state([P_LOW, 0], "PQ")
    state_in_p = myFluid.set_state([P_LOW, state_in_p[0]+DT_IN_LIQ], "PT")
    PLOT_INFO["col"]=["bv:",""]
    PLOT_INFO["label"]=["pump",""]
    state_o, work, power = pump(P_OUT, ETA_S, myFluid, m_dot=M_DOT,
                                plot_info=PLOT_INFO)
    print(f"pump work: {work:.3f} J/kg, state:{state_o}")
    ax0.legend()
    ax0.set_ylabel("T/K")
    ax0.set_xlabel("$\dot h$/ kW")
