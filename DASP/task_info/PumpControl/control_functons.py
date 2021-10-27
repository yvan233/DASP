import numpy as np

def pump_control_cooling(f_last, tw_re_list, tw_sup_list):
    # Cal average values
    #avg_outdoor_temp = np.mean(outdoor_temp_list)
    #avg_p_sup = np.mean(p_sup_list)
    #avg_p_re = np.mean(p_re_list)
    avg_tw_re = np.mean(tw_re_list)
    avg_tw_sup = np.mean(tw_sup_list)
    avg_dtw = avg_tw_re - avg_tw_sup
    #avg_dp = avg_p_sup - avg_p_re

    # Control frequency according to avg dtw
    if avg_dtw <= 2.0:
        f_con = f_last - 5.0
    elif avg_dtw > 2.0 and avg_dtw <= 3.0:
        f_con = f_last - 3.0
    elif avg_dtw > 3.0 and avg_dtw <= 4.0:
        f_con = f_last - 2.0
    elif avg_dtw > 4.0 and avg_dtw <= 4.5:
        f_con = f_last - 1.0                
    elif avg_dtw > 4.5 and avg_dtw < 5.5:
        f_con = f_last
    elif avg_dtw > 5.5 and avg_dtw <= 6.0:
        f_con = f_last + 1.0
    elif avg_dtw > 6.0 and avg_dtw <= 7.0:
        f_con = f_last + 2.0
    elif avg_dtw > 7.0 and avg_dtw <= 8.0:
        f_con = f_last + 3.0
    else:
        f_con = f_last + 5.0
    
    if f_con < 30.0:
        f_con = 30.0
    elif f_con > 50.0:
        f_con = 50.0
    else:
        pass

    return f_con