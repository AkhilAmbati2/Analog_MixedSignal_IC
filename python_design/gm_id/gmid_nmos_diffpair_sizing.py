"""
--------------------------------------------------------------------
File: gmid_nmos_diffpair_sizing.py

Purpose:
    gm/ID-based sizing of an NMOS input differential pair using
    multi-dimensional technology lookup tables.

Methodology:
    - Parses 4-D device characterization data (L, VGS, VDS, parameter)
    - Builds continuous gm/ID, gm/gds, JDS, and capacitance surfaces
    - Solves inverse gm/ID problems under gain and GBW constraints
    - Selects channel length using gm/gds targets
    - Computes device widths from current density
    - Iteratively updates parasitic capacitances (cOTA feedback loop)

Notes:
    - This script implements the core gm/ID methodology used in this repository
    - Device data is assumed to be extracted from Spectre simulations
    - Technology data has been sanitized for public release

-------------------------------------------------------------
"""



from numpy import *
from builtins import print
from copy import *
from math import *
from matplotlib.pyplot import *
from scipy.interpolate import *
import timeit

start = timeit.default_timer()

def get4d_array(lines):
    found = 0
    twod_counter = 0
    threed_counter = 0
    fourd_counter = 0
    fourd_array = []
    threed_array = []
    twod_array = []
    for line in lines:
        words = line.split()
        if len(words) == 0:
            found = 0
            continue
        if words[0] == 'length':
            found = 1
        elif found == 1:
            vals = line.split()
            if len(vals) > 2:
                float_vals = [float(x) if not x.isalpha() else x for x in vals]
                twod_array.insert(twod_counter, float_vals)
                twod_counter = twod_counter + 1

        if twod_counter == 74:
            twod_counter = 0
            threed_array.insert(threed_counter, twod_array)
            threed_counter = threed_counter + 1
            twod_array = []

        if threed_counter == 24:
            twod_counter = 0
            threed_counter = 0
            fourd_counter = fourd_counter + 1
            fourd_array.insert(fourd_counter, threed_array)
            fourd_counter = fourd_counter + 1
            twod_array = []
            threed_array = []
    return fourd_array

def read_file(file_name):
    fp = open(file_name)
    try:
        lines = fp.read().split('\n')
        return get4d_array(lines)
    finally:
        fp.close()

def get_threed_individual(fourd_arr, parameter):
    param_array = deepcopy(fourd_arr[parameter][:][:][:])
    req_3d_individual = empty((24, 73, 73), list)
    for i in range(len(param_array)):
        for j in range(1, len(param_array[i])):
            for k in range(1, len(param_array[i][j])):
                req_3d_individual[i][j - 1][k - 1] = param_array[i][j][k]
    return req_3d_individual

def get_threed_combined(fourd_arr, parameter1, parameter2):
    param_array_1 = deepcopy(fourd_arr[parameter1][:][:][:])
    param_array_2 = deepcopy(fourd_arr[parameter2][:][:][:])
    combined_arr = empty((24, 74, 74), list)
    if (parameter1 == 0) and (parameter2 == 7):
        for i in range(len(combined_arr)):
            for j in range(1, len(combined_arr[i])):
                for k in range(1, len(combined_arr[i][j])):
                    combined_arr[i][j][k] = param_array_1[i][j][k] / (2 * pi * param_array_2[i][j][k])
    elif parameter2 == 2:
        for i in range(len(combined_arr)):
            for j in range(1, len(combined_arr[i])):
                for k in range(1, len(combined_arr[i][j])):
                    if param_array_2[i][j][k] == 0:
                        combined_arr[i][j][k] = param_array_1[i][j][k + 1] / param_array_2[i][j][k + 1]
                    else:
                        combined_arr[i][j][k] = param_array_1[i][j][k] / param_array_2[i][j][k]
    else:
        for i in range(len(combined_arr)):
            for j in range(1, len(combined_arr[i])):
                for k in range(1, len(combined_arr[i][j])):
                    combined_arr[i][j][k] = param_array_1[i][j][k] / param_array_2[i][j][k]
    vds_array = param_array_1[0][:][0]
    for i in range(len(combined_arr)):
        for j in range(len(combined_arr[i])):
            if j == 0:
                combined_arr[i][j] = vds_array
            else:
                continue
    vgs_array = param_array_1[0][0][:]
    for i in range(len(combined_arr)):
        for j in range(len(combined_arr[i])):
            for k in range(len(combined_arr[i][j])):
                if k == 0:
                    combined_arr[i][j][k] = vgs_array[j]
                else:
                    continue
    req_3d_combined = empty((24, 73, 73), list)
    for i in range(len(combined_arr)):
        for j in range(1, len(combined_arr[i])):
            for k in range(1, len(combined_arr[i][j])):
                req_3d_combined[i][j-1][k-1] = combined_arr[i][j][k]
    return req_3d_combined

# --- Main Execution Block ---

print("Reading NMOS file.\n")
N_4D_arr = read_file('130nmos_VSB_0.dat')
print("Reading PMOS file. \n")
P_4D_arr = read_file('130pmos_VBS_0.dat')

lengths = [2.000e-07, 4.000e-07, 6.000e-07, 8.000e-07, 1.000e-06, 2.000e-06, 3.000e-06, 4.000e-06,
           5.000e-06, 6.000e-06, 7.000e-06, 8.000e-06, 9.000e-06, 1.000e-05, 1.100e-05, 1.200e-05,
           1.300e-05, 1.400e-05, 1.500e-05, 1.600e-05, 1.700e-05, 1.800e-05, 1.900e-05, 2.000e-05]

VDS_ARRAY = N_4D_arr[0][0][:][0]
VDS_ARRAY = VDS_ARRAY[1:]
VGS_ARRAY = N_4D_arr[0][0][0][:]
VGS_ARRAY = VGS_ARRAY[1:]

i_lengths = [2.000e-07, 2.500e-07, 3.000e-07, 3.500e-07, 4.000e-07, 4.500e-07, 5.000e-07, 5.500e-07,
             6.000e-07, 6.500e-07, 7.000e-07, 7.500e-07, 8.000e-07, 8.500e-07, 9.000e-07, 9.500e-07,
             1.000e-06, 1.500e-06, 2.000e-06, 2.500e-06, 3.000e-06, 3.500e-06, 4.000e-06, 4.500e-06,
             5.000e-06, 5.500e-06, 6.000e-06, 6.500e-06, 7.000e-06, 7.500e-06, 8.000e-06, 8.500e-06,
             9.000e-06, 9.500e-06, 1.000e-05, 1.100e-05, 1.200e-05, 1.300e-05, 1.400e-05, 1.500e-05,
             1.600e-05, 1.700e-05, 1.800e-05, 1.900e-05, 2.000e-05]
i_VGS = arange(0, 1.805, 0.005)
i_VGS = [round(elem, 3) for elem in i_VGS]
i_VDS = arange(0, 1.805, 0.005)
i_VDS = [round(elem, 3) for elem in i_VDS]

points = (lengths,  VGS_ARRAY, VDS_ARRAY)
len_i_lengths = len(i_lengths)
len_i_VGS = len(i_VGS)
len_i_VDS = len(i_VDS)

xi_mesh = array(meshgrid(i_lengths, i_VGS, i_VDS))
xi = rollaxis(xi_mesh, 0, 4)
xi = rollaxis(xi, 1, 0)
xi = xi.reshape(xi_mesh.size//3, 3)

# Interpolations
i_N_GM_IDS = interpn(points, get_threed_combined(N_4D_arr, 0, 2), xi, method='linear').reshape(len_i_lengths, len_i_VGS, len_i_VDS)
i_N_GM_GDS = interpn(points, get_threed_combined(N_4D_arr, 0, 1), xi, method='linear').reshape(len_i_lengths, len_i_VGS, len_i_VDS)
i_N_JDS = interpn(points, get_threed_combined(N_4D_arr, 2, 3), xi, method='linear').reshape(len_i_lengths, len_i_VGS, len_i_VDS)
i_N_CGD_W = interpn(points, get_threed_combined(N_4D_arr, 11, 3), xi, method='linear').reshape(len_i_lengths, len_i_VGS, len_i_VDS)
i_N_CGS_W = interpn(points, get_threed_combined(N_4D_arr, 9, 3), xi, method='linear').reshape(len_i_lengths, len_i_VGS, len_i_VDS)
i_N_VTH = interpn(points, get_threed_individual(N_4D_arr, 5), xi, method='linear').reshape(len_i_lengths, len_i_VGS, len_i_VDS)
i_N_VDSAT = interpn(points, get_threed_individual(N_4D_arr, 4), xi, method='linear').reshape(len_i_lengths, len_i_VGS, len_i_VDS)

i_P_GM_IDS = interpn(points, get_threed_combined(P_4D_arr, 0, 2), xi, method='linear').reshape(len_i_lengths, len_i_VGS, len_i_VDS)
i_P_GM_GDS = interpn(points, get_threed_combined(P_4D_arr, 0, 1), xi, method='linear').reshape(len_i_lengths, len_i_VGS, len_i_VDS)
i_P_JDS = interpn(points, get_threed_combined(P_4D_arr, 2, 3), xi, method='linear').reshape(len_i_lengths, len_i_VGS, len_i_VDS)
i_P_CDD_W = interpn(points, get_threed_combined(P_4D_arr, 8, 3), xi, method='linear').reshape(len_i_lengths, len_i_VGS, len_i_VDS)

length_to_find = i_lengths
cL = 5e-12
cOTA = 0
gbw = 5e+6
Adc = 100
ids1 = 10e-6

# Optimization Loop
for x in range(0, 20):
    gm1 = 2*pi*gbw*(cL+cOTA)
    gds1 = gm1/(2*Adc)
    gm_gds_1 = gm1/gds1
    gm_ids_1 = gm1/ids1
    
    # --- M1 Sizing ---
    gmgds1_req = 200 # Target Gain for M1
    
    # Create a small dynamic range around the target gain for contour plot
    val_2_be_found = linspace(gmgds1_req - 10, gmgds1_req + 10, 5) 
    
    vds_fixed = 0.6
    vds_index = i_VDS.index(vds_fixed)
    
    # Build 2D array of GmId vs (Length, GmGds)
    arr_2d_GmId = []
    for j in range(len(val_2_be_found)):
        ARR_1d_GmId = []
        for i in range(len(length_to_find)):
            p_s1 = interp1d(i_N_GM_GDS[i, :, vds_index], i_N_GM_IDS[i, :, vds_index], 
                           fill_value="extrapolate", kind='linear')
            ARR_1d_GmId.insert(i, p_s1(val_2_be_found[j]))
        arr_2d_GmId.append(ARR_1d_GmId)
    
    arr_2d_GmId = transpose(asarray(arr_2d_GmId))
    
    # Solve for Length using Contour
    cs2 = contour(val_2_be_found, length_to_find, arr_2d_GmId, [gm_ids_1])
    
    if len(cs2.allsegs[0]) == 0:
        print(f"Warning: No solution found for M1 at iteration {x}")
        continue
        
    gmgds_L_array = squeeze(cs2.allsegs[0])
    # Handle case where contour returns single point vs array
    if gmgds_L_array.ndim == 1: 
        gmgds_array, L_array = array([gmgds_L_array[0]]), array([gmgds_L_array[1]])
    else:
        gmgds_array, L_array = gmgds_L_array[:, 0], gmgds_L_array[:, 1]

    # Find L where Gm/Gds is closest to requirement
    idx_closest = (abs(gmgds_array - gmgds1_req)).argmin()
    L_solution = L_array[idx_closest]
    
    # Snap to nearest grid point (Vectorized replacement for the 30-line loop)
    c_L_index_1 = (abs(array(i_lengths) - L_solution)).argmin()

    # Calculate Widths and Parasitics for M1
    i_jds = interp1d(i_N_GM_IDS[c_L_index_1, :, vds_index], i_N_JDS[c_L_index_1, :, vds_index], fill_value="extrapolate", kind='linear')
    jds1 = i_jds(gm_ids_1)
    w1 = ids1/jds1
    
    i_cgdw = interp1d(i_N_GM_IDS[c_L_index_1, :, vds_index], i_N_CGD_W[c_L_index_1, :, vds_index], fill_value="extrapolate", kind='linear')
    cgdw1 = w1*i_cgdw(gm_ids_1)
    
    i_cgsw = interp1d(i_N_GM_IDS[c_L_index_1, :, vds_index], i_N_CGS_W[c_L_index_1, :, vds_index], fill_value="extrapolate", kind='linear')
    cgsw1 = w1 * i_cgsw(gm_ids_1)

    # --- M3 Sizing ---
    gm_ids_3 = 15
    gmgds3_req = 150
    val_2_be_found = linspace(gmgds3_req - 10, gmgds3_req + 10, 5)

    arr_2d_GmId = []
    for j in range(len(val_2_be_found)):
        ARR_1d_GmId = []
        for i in range(len(length_to_find)):
            p_s3 = interp1d(i_P_GM_GDS[i, :, vds_index], i_P_GM_IDS[i, :, vds_index], fill_value="extrapolate", kind='linear')
            ARR_1d_GmId.insert(i, p_s3(val_2_be_found[j]))
        arr_2d_GmId.append(ARR_1d_GmId)
    arr_2d_GmId = transpose(asarray(arr_2d_GmId))

    cs2 = contour(val_2_be_found, length_to_find, arr_2d_GmId, [gm_ids_3])
    
    if len(cs2.allsegs[0]) == 0: continue
    gmgds_L_array = squeeze(cs2.allsegs[0])
    if gmgds_L_array.ndim == 1: 
        gmgds_array, L_array = array([gmgds_L_array[0]]), array([gmgds_L_array[1]])
    else:
        gmgds_array, L_array = gmgds_L_array[:, 0], gmgds_L_array[:, 1]

    idx_closest = (abs(gmgds_array - gmgds3_req)).argmin()
    L_solution = L_array[idx_closest]
    c_L_index3 = (abs(array(i_lengths) - L_solution)).argmin()

    ip_vth = interp1d(i_N_GM_IDS[c_L_index_1, :, vds_index], i_N_VTH[c_L_index_1, :, vds_index], fill_value="extrapolate", kind='linear')
    ip_vth_ans = ip_vth(gm_ids_1)
    vgs3 = 1.8 - 1.6 + ip_vth_ans
    ip_gmid = interp1d(i_VGS, i_P_GM_IDS[c_L_index3, :, vds_index], fill_value="extrapolate", kind='linear')
    gm_id3_ans = ip_gmid(vgs3)
    gm_id3_final = gm_id3_ans + 2 

    i_jds3 = interp1d(i_P_GM_IDS[c_L_index3, :, vds_index], i_P_JDS[c_L_index3, :, vds_index], fill_value="extrapolate", kind='linear')
    jds3 = i_jds3(gm_id3_final)
    w3 = ids1/jds3
    i_cddw = interp1d(i_P_GM_IDS[c_L_index3, :, vds_index], i_P_CDD_W[c_L_index3, :, vds_index], fill_value="extrapolate", kind='linear')
    cddw3 = w3 * i_cddw(gm_id3_final)
    
    # Update cOTA (Parasitic Loop)
    cOTA = cddw3 + cgdw1 + (cgsw1/2)

    # --- M5 Sizing ---
    gm5 = 2*ids1*gm_ids_3
    gm3 = ids1 * gm_id3_final
    gds5 = (2*gm1)/((gm1/(0.013*gm3))-1)
    gm_gds5 = gm5 / gds5
    gmgds5_req = 60
    val_2_be_found = linspace(gmgds5_req - 10, gmgds5_req + 10, 5)

    arr_2d_GmId = []
    for j in range(len(val_2_be_found)):
        ARR_1d_GmId = []
        for i in range(len(length_to_find)):
            p_s5 = interp1d(i_N_GM_GDS[i, :, vds_index], i_N_GM_IDS[i, :, vds_index], fill_value="extrapolate", kind='linear')
            ARR_1d_GmId.insert(i, p_s5(val_2_be_found[j]))
        arr_2d_GmId.append(ARR_1d_GmId)
    arr_2d_GmId = transpose(asarray(arr_2d_GmId))

    cs2 = contour(val_2_be_found, length_to_find, arr_2d_GmId, [gm_ids_3]) # Note: Original code used gm_ids_3 here for contour level
    
    if len(cs2.allsegs[0]) == 0: continue
    gmgds_L_array = squeeze(cs2.allsegs[0])
    if gmgds_L_array.ndim == 1: 
        gmgds_array, L_array = array([gmgds_L_array[0]]), array([gmgds_L_array[1]])
    else:
        gmgds_array, L_array = gmgds_L_array[:, 0], gmgds_L_array[:, 1]
    
    idx_closest = (abs(gmgds_array - gmgds5_req)).argmin()
    L_solution = L_array[idx_closest]
    c_L_index5 = (abs(array(i_lengths) - L_solution)).argmin()

    ip_vgs = interp1d(i_N_GM_IDS[c_L_index_1, :, vds_index], i_VGS, fill_value="extrapolate", kind='linear')
    ip_vgs_ans = ip_vgs(gm_ids_1)
    vdsat5 = 0.8 - ip_vgs_ans
    ip_gmid = interp1d(i_N_VDSAT[c_L_index5, :, vds_index], i_N_GM_IDS[c_L_index5, :, vds_index], fill_value="extrapolate", kind='linear')
    gmid5_ans = ip_gmid(vdsat5)
    gmid5_final = gmid5_ans + 2 
    i_jds5 = interp1d(i_N_GM_IDS[c_L_index5, :, vds_index], i_N_JDS[c_L_index5, :, vds_index], fill_value="extrapolate", kind='linear')
    jds5 = i_jds5(gmid5_final)
    w5 = (2 * ids1) / jds5

print("L1:", i_lengths[c_L_index_1], "W1:", w1)
print("L3:", i_lengths[c_L_index3], "W3:", w3)
print("L5:", i_lengths[c_L_index5], "W5:", w5)
print("Gm/Id targets:", gm_ids_1, gm_id3_final, gmid5_final)
stop = timeit.default_timer()

print('Time: ', stop - start)
