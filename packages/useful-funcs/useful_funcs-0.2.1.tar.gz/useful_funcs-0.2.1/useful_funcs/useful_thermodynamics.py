'''
Rankine Cycle OTEC
'''

import pandas as pd
import numpy as np
from typing import Union


# _properties = [
#     "-1 413,56 639,94 3,3357 0,0015626 0,29979 338,53 1265,77 1604,3 1,4547 6,1058",
#     "0 429,38 638,57 3,4567 0,001566 0,2893 343,15 1262,25 1605,4 1,4716 6,0926",
#     "1 445,68 637,20 3,5811 0,0015694 0,27925 347,78 1258,72 1606,5 1,4884 6,0796",
#     "2 462,46 635,82 3,709 0,0015728 0,26962 352,42 1255,08 1607,5 1,5052 6,0667",
#     "3 479,72 634,44 3,8405 0,0015762 0,26038 357,06 1251,44 1608,5 1,5219 6,0538",
#     "4 497,48 633,06 3,9757 0,0015796 0,25153 361,71 1247,89 1609,6 1,5386 6,041",
#     "5 515,75 631,66 4,1146 0,0015831 0,24304 366,36 1244,14 1610,5 1,5553 6,0284",
#     "6 534,53 630,27 4,2573 0,0015866 0,23489 371,02 1240,48 1611,5 1,5719 6,0158",
#     "7 553,85 628,87 4,4039 0,0015902 0,22707 375,69 1236,81 1612,5 1,5885 6,0033",
#     "8 573,70 627,46 4,5545 0,0015937 0,21956 380,36 1233,04 1613,4 1,605 5,9908",
#     "9 594,09 626,05 4,7092 0,0015973 0,21235 385,04 1229,36 1614,4 1,6215 5,9785",
#     "10 615,05 624,64 4,8679 0,0016009 0,20543 389,72 1225,58 1615,3 1,638 5,9662",
#     "11 636,57 623,22 5,0309 0,0016046 0,19877 394,41 1221,79 1616,2 1,6544 5,954",
#     "12 658,66 621,79 5,1983 0,0016082 0,19237 399,11 1217,89 1617,0 1,6708 5,9419",
#     "13 681,35 620,36 5,37 0,001612 0,18622 403,81 1214,09 1617,9 1,6871 5,9299",
#     "14 704,63 618,93 5,5461 0,0016157 0,18031 408,52 1210,18 1618,7 1,7034 5,9179",
#     "15 728,52 617,49 5,7269 0,0016195 0,17461 413,24 1206,26 1619,5 1,7197 5,906",
#     "16 753,03 616,04 5,9123 0,0016233 0,16914 417,97 1202,33 1620,3 1,7359 5,8941",
#     "17 778,17 614,59 6,1025 0,0016271 0,16387 422,7 1198,40 1621,1 1,7521 5,8824",
#     "18 803,95 613,13 6,2975 0,001631 0,15879 427,44 1194,46 1621,9 1,7682 5,8707",
#     "19 830,38 611,67 6,4975 0,0016349 0,15391 432,18 1190,42 1622,6 1,7844 5,859",
#     "20 857,48 610,20 6,7025 0,0016388 0,1492 436,94 1186,36 1623,3 1,8005 5,85",
#     "21 885,24 608,72 6,9127 0,0016428 0,14466 441,7 1182,30 1624,0 1,8165 5,8359",
#     "22 913,69 607,24 7,1281 0,0016468 0,14029 446,47 1178,23 1624,7 1,8326 5,8245",
#     "23 942,83 605,76 7,3488 0,0016508 0,13608 451,24 1174,06 1625,3 1,8485 5,8131",
#     "24 972,68 604,26 7,5751 0,0016549 0,13201 456,03 1169,97 1626,0 1,8645 5,8017",
#     "25 1003,2 602,76 7,8069 0,001659 0,12809 460,82 1165,78 1626,6 1,8804 5,7904",
#     "26 1034,5 601,26 8,0443 0,0016632 0,12431 465,62 1161,58 1627,2 1,8963 5,7792",
#     "27 1066,6 599,75 8,2876 0,0016674 0,12066 470,43 1157,27 1627,7 1,9122 5,768",
#     "28 1099,3 598,23 8,5368 0,0016716 0,11714 475,25 1153,05 1628,3 1,9281 5,7569",
#     "29 1132,9 596,70 8,792 0,0016759 0,11374 480,08 1148,72 1628,8 1,9439 5,7458",
#     "30 1167,2 595,17 9,0533 0,0016802 0,11046 484,91 1144,39 1629,3 1,9597 5,7347",
#     "31 1202,3 593,63 9,3209 0,0016846 0,10729 489,76 1140,04 1629,8 1,9754 5,7237",
#     "32 1238,2 592,08 9,595 0,001689 0,10422 494,61 1135,69 1630,3 1,9911 5,7128",
#     "33 1274,9 590,53 9,8755 0,0016934 0,10126 499,47 1131,23 1630,7 2,0069 5,7019",
#     "34 1312,4 588,97 10,163 0,0016979 0,098399 504,34 1126,76 1631,1 2,0225 5,691",
#     "35 1350,8 587,40 10,457 0,0017024 0,095632 509,23 1122,27 1631,5 2,0382 5,6801",
#     "36 1390,0 585,82 10,758 0,001707 0,092957 514,12 1117,78 1631,9 2,0538 5,6693",]

# properties = np.empty((len(_properties), 11), dtype=float)

# for i in range(len(_properties)):
#     l1 = [float(property.replace(",", ".")) for property in _properties[i].split()]
#     properties[i, :] = l1

# properties_df = pd.DataFrame(columns=['temp', 'pressure', 'density_l', 'density_g', 'sp_vol_l', 'sp_vol_g', 'sp_enthalpy_l', 'sp_enthalpy_lg', 'sp_enthalpy_g', 'sp_entropy_l', 'sp_entropy_g'])

# for i in range(len(_properties)):
#     properties_df.loc[i] = properties[i, :]


def get_properties_p(properties_df: pd.DataFrame, p: Union[int, float, np.ndarray]) -> Union[float, np.ndarray]:
    p1 = properties_df[properties_df['pressure'] <= p].iloc[-1]['pressure']
    p2 = properties_df[properties_df['pressure'] >= p].iloc[0]['pressure']

    if p1 == p2:
        return properties_df[properties_df['pressure'] == p]

    prop1 = properties_df[properties_df['pressure'] <= p].iloc[-1]
    prop2 = properties_df[properties_df['pressure'] >= p].iloc[0]

    df_prop = pd.DataFrame(columns=['temp', 'pressure', 'density_l', 'density_g', 'sp_vol_l', 'sp_vol_g', 'sp_enthalpy_l', 'sp_enthalpy_lg', 'sp_enthalpy_g', 'sp_entropy_l', 'sp_entropy_g'])
    df_prop.loc[0] = (prop1.values +  ((p - p1)/(p2 - p1))* (prop2.values - prop1.values))

    return df_prop


def get_properties_t(properties_df: pd.DataFrame, t):
    t1 = properties_df[properties_df['temp'] <= t].iloc[-1]['temp']
    t2 = properties_df[properties_df['temp'] >= t].iloc[0]['temp']

    if t1 == t2:
        return properties_df[properties_df['temp'] == t]

    prop1 = properties_df[properties_df['temp'] <= t].iloc[-1]
    prop2 = properties_df[properties_df['temp'] >= t].iloc[0]

    df_prop = pd.DataFrame(columns=['temp', 'pressure', 'density_l', 'density_g', 'sp_vol_l', 'sp_vol_g', 'sp_enthalpy_l', 'sp_enthalpy_lg', 'sp_enthalpy_g', 'sp_entropy_l', 'sp_entropy_g'])
    df_prop.loc[0] = (prop1.values +  ((t - t1)/(t2 - t1))* (prop2.values - prop1.values))

    return df_prop


def get_enthalpy_t(properties_df: pd.DataFrame, t, q):
    t1 = properties_df[properties_df['temp'] <= t].iloc[-1]['temp']
    t2 = properties_df[properties_df['temp'] >= t].iloc[0]['temp']

    if t1 == t2:
        return properties_df[properties_df['temp'] == t1].iloc[0]['sp_enthalpy_l'] + q * properties_df[properties_df['temp'] == t1].iloc[0]['sp_enthalpy_lg']

    prop1 = properties_df[properties_df['temp'] <= t].iloc[-1]
    prop2 = properties_df[properties_df['temp'] >= t].iloc[0]

    df_prop = pd.DataFrame(columns=['temp', 'pressure', 'density_l', 'density_g', 'sp_vol_l', 'sp_vol_g', 'sp_enthalpy_l', 'sp_enthalpy_lg', 'sp_enthalpy_g', 'sp_entropy_l', 'sp_entropy_g'])
    df_prop.loc[0] = (prop1.values +  ((t - t1)/(t2 - t1))* (prop2.values - prop1.values))

    return df_prop.loc[0]['sp_enthalpy_l'] + q * df_prop.loc[0]['sp_enthalpy_lg']


def get_enthalpy_lg_t(properties_df: pd.DataFrame, t):
    t1 = properties_df[properties_df['temp'] <= t].iloc[-1]['temp']
    t2 = properties_df[properties_df['temp'] >= t].iloc[0]['temp']

    prop1 = properties_df[properties_df['temp'] <= t].iloc[-1]
    prop2 = properties_df[properties_df['temp'] >= t].iloc[0]

    df_prop = pd.DataFrame(columns=['temp', 'pressure', 'density_l', 'density_g', 'sp_vol_l', 'sp_vol_g', 'sp_enthalpy_l', 'sp_enthalpy_lg', 'sp_enthalpy_g', 'sp_entropy_l', 'sp_entropy_g'])
    df_prop.loc[0] = (prop1.values +  ((t - t1)/(t2 - t1))* (prop2.values - prop1.values))

    return df_prop.loc[0]['sp_enthalpy_lg']


def get_avg_sp_heat_l(properties_df: pd.DataFrame, t):
    if np.ceil(t) == np.floor(t):
        t += 0.01

    return get_enthalpy_t(t=np.ceil(t), q=0) - get_enthalpy_t(t=np.floor(t), q=0)


def get_avg_density_l(properties_df: pd.DataFrame, t):
    if np.ceil(t) == np.floor(t):
        t += 0.01

    t1 = properties_df[properties_df['temp'] == np.floor(t)].iloc[-1]['temp']
    t2 = properties_df[properties_df['temp'] == np.ceil(t)].iloc[0]['temp']

    prop1 = properties_df[properties_df['temp'] <= t].iloc[-1]
    prop2 = properties_df[properties_df['temp'] >= t].iloc[0]

    return (prop2['density_l'] + prop1['density_l'])/2


def get_avg_sp_vol_l(properties_df: pd.DataFrame, t):
    if np.ceil(t) == np.floor(t):
        t += 0.01

    t1 = properties_df[properties_df['temp'] == np.floor(t)].iloc[-1]['temp']
    t2 = properties_df[properties_df['temp'] == np.ceil(t)].iloc[0]['temp']

    prop1 = properties_df[properties_df['temp'] <= t].iloc[-1]
    prop2 = properties_df[properties_df['temp'] >= t].iloc[0]

    return (prop2['sp_vol_l'] + prop1['sp_vol_l'])/2


def get_entropy_t(properties_df: pd.DataFrame, t, q):
    t1 = properties_df[properties_df['temp'] <= t].iloc[-1]['temp']
    t2 = properties_df[properties_df['temp'] >= t].iloc[0]['temp']

    if t1 == t2:
        return properties_df[properties_df['temp'] == t1].iloc[0]['sp_entropy_l'] + q * (properties_df[properties_df['temp'] == t1].loc[0]['sp_entropy_g'] - properties_df[properties_df['temp'] == t1].loc[0]['sp_entropy_l'])

    prop1 = properties_df[properties_df['temp'] <= t].iloc[-1]
    prop2 = properties_df[properties_df['temp'] >= t].iloc[0]

    df_prop = pd.DataFrame(columns=['temp', 'pressure', 'density_l', 'density_g', 'sp_vol_l', 'sp_vol_g', 'sp_enthalpy_l', 'sp_enthalpy_lg', 'sp_enthalpy_g', 'sp_entropy_l', 'sp_entropy_g'])
    df_prop.loc[0] = (prop1.values +  ((t - t1)/(t2 - t1)) * (prop2.values - prop1.values))

    return df_prop.loc[0]['sp_entropy_l'] + q * (df_prop.loc[0]['sp_entropy_g'] - df_prop.loc[0]['sp_entropy_l'])


def get_entropy_p(properties_df: pd.DataFrame, p, q):
    p1 = properties_df[properties_df['pressure'] <= p].iloc[-1]['pressure']
    p2 = properties_df[properties_df['pressure'] >= p].iloc[0]['pressure']

    if p1 == p2:
        return properties_df[properties_df['pressure'] == p1].iloc[0]['sp_entropy_l'] + q * (properties_df[properties_df['temp'] == p1].loc[0]['sp_entropy_g'] - properties_df[properties_df['temp'] == p1].loc[0]['sp_entropy_l'])

    prop1 = properties_df[properties_df['pressure'] <= p].iloc[-1]
    prop2 = properties_df[properties_df['pressure'] >= p].iloc[0]

    df_prop = pd.DataFrame(columns=['temp', 'pressure', 'density_l', 'density_g', 'sp_vol_l', 'sp_vol_g', 'sp_enthalpy_l', 'sp_enthalpy_lg', 'sp_enthalpy_g', 'sp_entropy_l', 'sp_entropy_g'])
    df_prop.loc[0] = (prop1.values +  ((p - p1)/(p2 - p1))* (prop2.values - prop1.values))

    return df_prop.loc[0]['sp_entropy_l'] + q * (df_prop.loc[0]['sp_entropy_g'] - df_prop.loc[0]['sp_entropy_l'])


def get_quality_prop(prop, prop_l, prop_g):
    return (prop - prop_l)/(prop_g - prop_l)


def get_temp_s_g(properties_df: pd.DataFrame, s):
    s1 = properties_df[properties_df['sp_entropy_g'] <= s].iloc[0]['sp_entropy_g']
    s2 = properties_df[properties_df['sp_entropy_g'] >= s].iloc[-1]['sp_entropy_g']

    if s1 == s2:
        return properties_df[properties_df['sp_entropy_g'] == s1].iloc[0]['sp_entropy_g']

    prop1 = properties_df[properties_df['sp_entropy_g'] <= s].iloc[0]
    prop2 = properties_df[properties_df['sp_entropy_g'] >= s].iloc[-1]

    df_prop = pd.DataFrame(columns=['temp', 'pressure', 'density_l', 'density_g', 'sp_vol_l', 'sp_vol_g', 'sp_enthalpy_l', 'sp_enthalpy_lg', 'sp_enthalpy_g', 'sp_entropy_l', 'sp_entropy_g'])
    df_prop.loc[0] = (prop1.values +  ((s - s1)/(s2 - s1))* (prop2.values - prop1.values))

    return df_prop.loc[0]['temp']


def get_enthalpy_p(properties_df: pd.DataFrame, p, q):
    p1 = properties_df[properties_df['pressure'] <= p].iloc[-1]['pressure']
    p2 = properties_df[properties_df['pressure'] >= p].iloc[0]['pressure']

    prop1 = properties_df[properties_df['pressure'] <= p].iloc[-1]
    prop2 = properties_df[properties_df['pressure'] >= p].iloc[0]

    df_prop = pd.DataFrame(columns=['temp', 'pressure', 'density_l', 'density_g', 'sp_vol_l', 'sp_vol_g', 'sp_enthalpy_l', 'sp_enthalpy_lg', 'sp_enthalpy_g', 'sp_entropy_l', 'sp_entropy_g'])
    df_prop.loc[0] = (prop1.values +  ((p - p1)/(p2 - p1))* (prop2.values - prop1.values))

    return df_prop.loc[0]['sp_enthalpy_l'] + q * df_prop.loc[0]['sp_enthalpy_lg']


def get_sat_liq_temp_h(properties_df: pd.DataFrame, h):
    h1 = properties_df[properties_df['sp_enthalpy_l'] <= h].iloc[-1]['sp_enthalpy_l']
    h2 = properties_df[properties_df['sp_enthalpy_l'] >= h].iloc[0]['sp_enthalpy_l']

    prop1 = properties_df[properties_df['sp_enthalpy_l'] <= h].iloc[-1]
    prop2 = properties_df[properties_df['sp_enthalpy_l'] >= h].iloc[0]

    df_prop = pd.DataFrame(columns=['temp', 'pressure', 'density_l', 'density_g', 'sp_vol_l', 'sp_vol_g', 'sp_enthalpy_l', 'sp_enthalpy_lg', 'sp_enthalpy_g', 'sp_entropy_l', 'sp_entropy_g'])
    df_prop.loc[0] = (prop1.values +  ((h - h1)/(h2 - h1))* (prop2.values - prop1.values))

    return df_prop.loc[0]['temp']


def get_lmtd(t_warm_in, t_warm_out, t_cold_in, t_cold_out):
    return np.abs(((t_warm_in - t_cold_out) - (t_warm_out - t_cold_in))/np.log((t_warm_in - t_cold_out)/(t_warm_out - t_cold_in)))


def pumping_power(properties_df, pres_entry, pres_exit, t):
    """
    Pump is operating with an efficiency of 75%
    """
    return ((pres_exit - pres_entry) * get_avg_sp_vol_l(properties_df, t))/0.75


def turbine_enthalpy_power(h4, h5_isentropic, eff_turbine):
    h5 = h4 - (eff_turbine * (h4 - h5_isentropic))
    return h5, (h4 - h5)


def entropy_change_incompressible(cp_avg, t_before, t_after):
    return (cp_avg * np.log(t_after/t_before))


def turbine_power_highly_inefficient(properties_df, t5):
    """
    Turbine is operating with an efficiency of 87%
    Turbine Entry Quality: 1 - Fixed and Actual
    Turbine Exit Quality: 0.9759 - Fixed and Actual
    """

    eff_turb = 0.8711356085583247

    turb_exit_actual_enthalpy = get_enthalpy_t(properties_df, t5, q=0.9759)
    turb_exit_actual_entropy = get_entropy_t(properties_df, t5, q=0.9759)
    turb_exit_temp_prop = get_properties_t(properties_df, t5)
    turb_exit_actual_quality = get_quality_prop(turb_exit_actual_entropy, turb_exit_temp_prop['sp_entropy_l'].values[0], turb_exit_temp_prop['sp_entropy_g'].values[0])

    no_of_runs = len(np.arange(start=t5+0.01, stop=t5+20, step=0.005))
    # print(no_of_runs)
    effs = np.empty(no_of_runs, dtype=float)
    temps = np.empty(no_of_runs, dtype=float)
    actuals = np.empty(no_of_runs, dtype=float)
    isens = np.empty(no_of_runs, dtype=float)

    for ind, tem_tur_in in enumerate(np.arange(start=t5+0.01, stop=t5+20, step=0.005)):
        turb_entry_enthalpy = get_enthalpy_t(tem_tur_in, 1)
        turb_entry_entropy = get_entropy_t(tem_tur_in, 1)

        # Quality/Dryness fraction for which the process is isentropic
        turb_exit_x_isen = get_quality_prop(turb_entry_entropy, turb_exit_temp_prop['sp_entropy_l'].values[0], turb_exit_temp_prop['sp_entropy_g'].values[0])

        # Enthalpy corresponding to this entropy at the temperature of exit
        turb_exit_isen_enthalpy = get_enthalpy_t(t5, q=turb_exit_x_isen)

        actual_turb_w_out = turb_entry_enthalpy - turb_exit_actual_enthalpy
        isen_turb_w_out = turb_entry_enthalpy - turb_exit_isen_enthalpy

        eff_t = actual_turb_w_out/isen_turb_w_out

        effs[ind] = np.abs(eff_t - eff_turb)
        temps[ind] = tem_tur_in
        actuals[ind] = actual_turb_w_out
        isens[ind] = isen_turb_w_out

    ind_with_min_eff_error = np.argmin(effs)
    return temps[ind_with_min_eff_error], actuals[ind_with_min_eff_error]


def surface_water_cooling(warm_water_temp_in, cold_water_temp_in, rch):
    dT = warm_water_temp_in - cold_water_temp_in
    surf_seawater_cool_evap = (3 * dT)/(8 * (1 + rch))
    return surf_seawater_cool_evap


def temp_ladder(warm_water_temp_in, cold_water_temp_in, rch):
    dT = warm_water_temp_in - cold_water_temp_in
    surf_seawater_cool_evap = (3 * dT)/(8 * (1 + rch))
    evap_pinch_point = (dT/16)
    work_fluid_temp_drop = dT/2
    cond_pinch_point = (dT/16)
    deep_sea_water_warm = (3 * rch * dT)/(8 * (1 + rch))

    working_fluid_boil_temp = warm_water_temp_in - (surf_seawater_cool_evap + evap_pinch_point)
    working_fluid_cond_temp = cold_water_temp_in + (deep_sea_water_warm + cond_pinch_point)
    
    return working_fluid_boil_temp, working_fluid_cond_temp


def rankine_cycle_otec(warm_water_temp_in, cold_water_temp_in, **kwargs):
    if np.isnan(warm_water_temp_in):
        return [np.nan, np.nan, np.nan, np.nan]
    
    if np.isnan(cold_water_temp_in):
        return [np.nan, np.nan, np.nan, np.nan]
    
    ## ORIGINALLY USED THIS. NOW SHIFTED TO TEMPERATURE LADDER METHOD
    # working_fluid_boil_temp = warm_water_temp_in - 5.10
    # working_fluid_cond_temp = cold_water_temp_in + 5.54

    # ratio of cold water to hot water
    rch = 0.5
    working_fluid_boil_temp, working_fluid_cond_temp = temp_ladder(warm_water_temp_in, cold_water_temp_in, rch)
    
    if working_fluid_boil_temp <= working_fluid_cond_temp:
        return np.array([0, 0, 0, 0])

    mass = kwargs.get("mass_rate", 4060)
    
    t3 = working_fluid_boil_temp
    q3 = 1
    state3_prop = get_properties_t(t3)
    p3 = state3_prop['pressure'].values[0]
    h3 = state3_prop['sp_enthalpy_g'].values[0]
    s3 = state3_prop['sp_entropy_g'].values[0]



    p4 = p3 - 9.993600000000129
    q4 = 1
    state4_prop = get_properties_p(p4)
    t4 = state4_prop['temp'].values[0]
    h4 = state4_prop['sp_enthalpy_g'].values[0]
    s4 = state4_prop['sp_entropy_g'].values[0]



    t5 = working_fluid_cond_temp
    state5_prop = get_properties_t(t5)
    p5 = state5_prop['pressure'].values[0]
    s5_isentropic = s4
    q5_isentropic = get_quality_prop(s5_isentropic, state5_prop['sp_entropy_l'].values[0], state5_prop['sp_entropy_g'].values[0])
    h5_isentropic = get_enthalpy_t(t=t5, q=q5_isentropic)
    eff_turbine = 0.8711356085583247
    h5, w_out = turbine_enthalpy_power(h4, h5_isentropic, eff_turbine=eff_turbine)
    q5 = get_quality_prop(h5, state5_prop['sp_enthalpy_l'].values[0], state5_prop['sp_enthalpy_g'].values[0])
    s5 = get_entropy_t(t=t5, q=q5)



    t6 = working_fluid_cond_temp
    q6 = 0
    state6_prop = get_properties_t(t6)
    p6 = state6_prop['pressure'].values[0]
    h6 = state6_prop['sp_enthalpy_l'].values[0]
    s6 = state6_prop['sp_entropy_l'].values[0]



    q1 = 0
    p1 = get_properties_t(working_fluid_boil_temp)['pressure'].values[0]
    avg_pump_temp = working_fluid_cond_temp
    pump_work = pumping_power(p6, p1, avg_pump_temp)
    h1 = h6 + pump_work
    cp1 = get_avg_sp_heat_l(working_fluid_cond_temp)
    t1 = t6 + ((h1 -h6)/cp1)
    s1 = s6 + entropy_change_incompressible(cp_avg=cp1, t_before=t6, t_after=t1)

    t2 = working_fluid_boil_temp
    state2_prop = get_properties_t(t2)
    p2 = state2_prop['pressure'].values[0]
    q2 = 0
    h2 = state2_prop['sp_enthalpy_l'].values[0]
    s2 = state2_prop['sp_entropy_l'].values[0]


    h1_evap_entry = h1
    h2_evap_boiling = h2
    h3_evap_exit = h3
    e_in = h3_evap_exit - h1_evap_entry

    h4_turbine_entry = h4
    h5_turbine_exit_isen = h5_isentropic
    h5_turbine_exit = h5
    w_out = h4_turbine_entry - h5_turbine_exit

    h5_cond_entry = h5
    h6_cond_exit = h6
    e_out = h5_turbine_exit - h6_cond_exit

    h6_pump_entry = h6
    h1_pump_exit = h1
    w_in = h1_pump_exit - h6_pump_entry

    w_net = w_out - w_in

    pump_work = pump_work

    gross_turb_output = (w_out * mass/1000)
    gross_power_gen = (w_out * mass/1000) * 0.975

    rankine_efficiency = w_net/e_in * 100
    plant_carnot_efficiency = (1 - ((t5 + 273.15)/(t3 + 273.15)))*100
    available_carnot_efficiency = (1 - ((cold_water_temp_in + 273.15)/(warm_water_temp_in + 273.15)))*100

    # warm_water_mass = 460000
    # cold_water_mass = 366000

    # evaporator_UA = 1410
    # condenser_UA = 1350

    # sp_heat_sea_water = 3.993

    # warm_water_temp_out = (warm_water_temp_in - ((e_in * mass)/(warm_water_mass * sp_heat_sea_water)))
    # cold_water_temp_out = (cold_water_temp_in + ((e_out * mass)/(cold_water_mass * sp_heat_sea_water)))

    # evaporator_load = warm_water_mass * sp_heat_sea_water * (warm_water_temp_in - warm_water_temp_out)/1000
    # condensor_load = cold_water_mass * sp_heat_sea_water * (cold_water_temp_out - cold_water_temp_in)/1000

    # evap_heat_in = mass * (get_avg_sp_heat_l((t1+t2)/2) * (t2 - t1) + get_enthalpy_lg_t(t2))/1000
    # cond_heat_out = mass * (get_enthalpy_lg_t(t5) * q5)/1000

    print_out = kwargs.get('print_out', False)
    if print_out:
        print(f"State 1: Pump Exit - Evaporator Entry")
        print(f"Temp = {t1:.3f}°C, Pressure = {p1:.2f} kPa, Quality = {q1:.2f}, Enthalpy = {h1:.2f} kJ/kg, Entropy = {s1:.2f} kJ/kg K\n")

        print(f"State 2: Saturated Liquid State in Evaporator")
        print(f"Temp = {t2:.2f}°C, Pressure = {p2:.2f} kPa, Quality = {q2:.2f}, Enthalpy = {h2:.2f} kJ/kg, Entropy = {s2:.2f} kJ/kg K\n")

        print(f"State 3: Evaporator Exit")
        print(f"Temp = {t3:.2f}°C, Pressure = {p3:.2f} kPa, Quality = {q3:.2f}, Enthalpy = {h3:.2f} kJ/kg, Entropy = {s3:.2f} kJ/kg K\n")

        print(f"State 4: Turbine Entry")
        print(f"Temp = {t4:.2f}°C, Pressure = {p4:.2f} kPa, Quality = {q4:.2f}, Enthalpy = {h4:.2f} kJ/kg, Entropy = {s4:.2f} kJ/kg K\n")

        print(f"State 5: Turbine Exit")
        print(f"Temp = {t5:.2f}°C, Pressure = {p5:.2f} kPa, Quality_isen = {q5_isentropic:.2f}, Enthalpy_isen = {h5_isentropic:.2f} kJ/kg, Entropy_isen = {s5_isentropic:.2f} kJ/kg K")
        print(f"Temp = {t5:.2f}°C, Pressure = {p5:.2f} kPa, Quality = {q5:.2f}, Enthalpy = {h5:.2f} kJ/kg, Entropy = {s5:.2f} kJ/kg K\n")

        print(f"State 6: Condenser Exit - Pump Entry")
        print(f"Temp = {t6:.2f}°C, Pressure = {p6:.2f} kPa, Quality = {q6:.2f}, Enthalpy = {h6:.2f} kJ/kg, Entropy = {s6:.2f} kJ/kg K\n")

        

        print(f"Pump work: {pump_work:.4f} kJ/kg\n")

        print(f"Evaporator Entry: {h1_evap_entry:.3f} kJ/kg")
        print(f"Evaporator Before Boiling: {h2_evap_boiling:.3f} kJ/kg")
        print(f"Evaporator Exit: {h3_evap_exit:.3f} kJ/kg")
        print(f"Energy Added in Evaporator, E_in = {e_in:.3f} kJ/kg\n")

        print(f"Turbine Entry Properties")
        print(f"t = {t4}°C, p = {p4:.3f}kPa, quality = {q4:.4f}")
        print(f"Turbine Entry: {h4_turbine_entry:.3f} kJ/kg\n")
        print(f"Turbine Exit Properties")
        print(f"t = {t5}°C, p = {p5:.3f}kPa, quality = {q5:.4f}")
        print(f"Turbine Exit: {h5_turbine_exit:.3f} kJ/kg")
        print(f"Energy Extracted from Turbine, W_out = {w_out:.3f} kJ/kg\n")

        print(f"Condenser Entry: {h5_cond_entry:.3f} kJ/kg")
        print(f"Condenser Exit: {h6_cond_exit:.3f} kJ/kg")
        print(f"Energy Exhausted from Condenser, E_out = {e_out:.3f} kJ/kg\n")

        print(f"Pump Entry: {h6_pump_entry:.3f} kJ/kg")
        print(f"Pump Exit: {h1_pump_exit:.3f} kJ/kg")
        print(f"Energy Added Pumping, W_in = {w_in:.3f} kJ/kg\n")

        print(f"W = W_out - W_in = {w_out:.3f} kJ/kg - {w_in:.3f} kJ/kg = {w_net:.3f} kJ/kg")
        print(f"Gross Turbine Output: m * W_out = {mass} kg/s * {w_out:.3f} kJ/kg = {gross_turb_output:.3f} MW")
        print(f"Gross Power Generated with 97.5% Generator Efficiency: {gross_power_gen:.3f} MW")

        print(f"Rankine Efficiency = W / E_in = {w_net:.3f} / {e_in:.3f} = {rankine_efficiency:.3f} %\n")

        print(f"Plant Carnot Efficiency = {plant_carnot_efficiency:.3f} %")
        print(f"Available Carnot Efficiency = {available_carnot_efficiency:.3f} %\n")

        # print(f"Warm Water Temp In: {warm_water_temp_in:.2f}°C")
        # print(f"Warm Water Temp Out: {warm_water_temp_out:.2f}°C")
        # print(f"Cold Water Temp In: {cold_water_temp_in:.2f}°C")
        # print(f"Cold Water Temp Out: {cold_water_temp_out:.2f}°C\n")

        # print(f"Evaporator Heat: {evap_heat_in:.2f} MW")
        # print(f"Evaporator Load: {evaporator_load:.2f} MW\n")

        # print(f"Condenser Heat: {cond_heat_out:.2f} MW")
        # print(f"Condenser Load: {condensor_load:.2f} MW\n")

    return gross_power_gen, rankine_efficiency, plant_carnot_efficiency, available_carnot_efficiency



