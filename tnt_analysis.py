# Created by joecool890
# Data organization in python using pandas
# Version 0.2.2
# minor fixes (commented out stuff)

import glob
import time
import getpass
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# function to determine confidence interval corrected for within-participants
def cm_standard_error(dataframe):
    # Get # of conditions (number of columns)
    num_conditions = dataframe.shape[1]

    # Morey portion of Cousineau-Morey method
    morey_correction = np.sqrt(float(num_conditions) / (num_conditions - 1))

    # Calculate mean of each participant and the grand mean
    parMean = dataframe.mean(axis=1)
    grandMean = parMean.mean()

    # Get standard error & add to original dataframe (subtract parMean, add grandMean)
    normMean = dataframe.sub(parMean, axis=0) + grandMean

    dataframe.loc["mean"] = normMean.mean()

    dataframe.loc["ste_c-m-corr"] = normMean.std() / np.sqrt(len(normMean) - 1)

    forexcel_dataframe = pd.concat(
        [dataframe.loc["mean"], dataframe.loc["ste_c-m-corr"]], axis=1).unstack()
    return (forexcel_dataframe)


# Main Data Directory
userName = getpass.getuser()
project_name = "taxonomic-thematic"

# exp_ver (v1 = Exp 1, v3 = mTurk Exp 2)
exp_ver = "v1"
exp_num = "_exp01"
# exp_iter: 1 = 750 ms, 2 = 500 ms, 3 = 250 ms
exp_iter = 3
data_dir = "/Users/" + userName + "/Dropbox/UC-Davis/projects/" + \
    project_name + "/raw-data/" + exp_ver + exp_num + "/tnt*.csv"

# Extract all data files into single np array
data_files = glob.glob(data_dir)
participants = len(data_files)

# Get Demographics data if mTurk
if exp_ver == "v3":
    demo_dir = "/Users/" + userName + "/PycharmProjects/" + \
        project_name + "/data/" + exp_ver + "/demogr/" + "/tnt*.csv"
    demographics_file = glob.glob(demo_dir)
    demo_data = []

# Data Threshold
RT_thres = 1  # Typically 0 for Exp 2
acc_thresh = .80

# Load all data files into single panda data frame
x = time.time()
raw_data = []
for file in range(participants):
    if exp_ver == "v3":
        data = pd.read_csv(data_files[file], index_col="uniqueid", header=0)
        # demographics = pd.read_csv(demographics_file[file], index_col="uniqueid", header=0)
        # demo_data.append(demographics)
    else:
        data = pd.read_csv(data_files[file], index_col="par_num", header=0)
    raw_data.append(data)
# shove all data into a single data frame, and point to specific iteration
data_frame_raw = pd.concat(raw_data)

# possibly delete
# if exp_ver != "v3":
#     data_frame_raw = data_frame_raw[(data_frame_raw["exp_iter"] == exp_iter)]

if exp_ver == "v1":
    # RT threshold
    if RT_thres == 1:
        RT_min = 150
        RT_max = 1500
        all_data_count = 600
        data_frame = data_frame_raw[(data_frame_raw["RT"] > RT_min) & (data_frame_raw["RT"] <= RT_max)]
        excluded_data_count = [all_data_count - data_frame.groupby(["par_num"])["RT"].count(),
                               (all_data_count - data_frame.groupby(["par_num"])["RT"].count()) / all_data_count * 100]
        # concat trial count + % into one
        excluded_data_count = pd.concat(excluded_data_count, axis=1)
        excluded_data_count.columns = ["dropped_trials", "drop_rate"]

    # Grab overall accuracy for participants
    acc_overall = data_frame.groupby(["par_num"])["accuracy"].mean()

    age = data_frame.groupby(["par_num"])["par_age"].mean()

    # Only save those who are worthy
    include_list = acc_overall.index[acc_overall >= acc_thresh]
    data_frame = data_frame.loc[include_list]

    # dataframe for first 2 blocks
    first2_blk = data_frame[data_frame['block_num'] <= 2]

    # concat excluded trials w/ overall accuracy
    excluded_data_count = pd.concat([excluded_data_count, acc_overall], axis=1)
    excluded_data_count = excluded_data_count.loc[include_list]

    # Get accuracy data by whatever you need
    acc_condition = data_frame.groupby(["par_num", "condition"])[
        "accuracy"].mean().unstack(["condition"])
    acc_condition_blk = data_frame.groupby(["par_num", "condition", "block_num"])[
        "accuracy"].mean().unstack(["condition", "block_num"])
    acc_condition_objs = data_frame.groupby(["par_num", "condition", "object_pair"])[
        "accuracy"].agg(["mean"]).unstack(["condition", "object_pair"])

    # Get only correct trials (for RT)
    corr_data = data_frame[(data_frame["accuracy"] == 1)]

    # RT by conditions
    RT_condition = corr_data.groupby(["par_num", "condition"])[
        "RT"].agg(["mean"]).unstack(["condition"])
    RT_condition_blk = corr_data.groupby(["par_num", "condition", "block_num"])[
        "RT"].agg(["mean"]).unstack(["condition", "block_num"])
    RT_condition_objs = corr_data.groupby(["par_num", "condition", "object_pair"])[
        "RT"].agg(["mean"]).unstack(["condition", "object_pair"])

    # column headers (need to figure out how to loop somehow)
    acc_condition.columns = ["acc_neu", "acc_tax", "acc_thm"]
    acc_condition_blk.columns = ["acc_neu_blk1", "acc_neu_blk2", "acc_neu_blk3", "acc_neu_blk4", "acc_neu_blk5", "acc_neu_blk6",
                                 "acc_neu_blk7", "acc_neu_blk8", "acc_neu_blk9", "acc_neu_blk10", "acc_tax_blk1", "acc_tax_blk2",
                                 "acc_tax_blk3", "acc_tax_blk4", "acc_tax_blk5", "acc_tax_blk6", "acc_tax_blk7", "acc_tax_blk8",
                                 "acc_tax_blk9", "acc_tax_blk10", "acc_thm_blk1", "acc_thm_blk2", "acc_thm_blk3", "acc_thm_blk4",
                                 "acc_thm_blk5", "acc_thm_blk6", "acc_thm_blk7", "acc_thm_blk8", "acc_thm_blk9", "acc_thm_blk10"]
    acc_condition_objs.columns = ["acc_neu_pair1", "acc_neu_pair2", "acc_neu_pair3", "acc_neu_pair4", "acc_neu_pair5",
                                  "acc_neu_pair6", "acc_neu_pair7", "acc_neu_pair8", "acc_neu_pair9", "acc_neu_pair10",
                                  "acc_tax_pair1", "acc_tax_pair2", "acc_tax_pair3", "acc_tax_pair4", "acc_tax_pair5",
                                  "acc_tax_pair6", "acc_tax_pair7", "acc_tax_pair8", "acc_tax_pair9", "acc_tax_pair10",
                                  "acc_thm_pair1", "acc_thm_pair2", "acc_thm_pair3", "acc_thm_pair4", "acc_thm_pair5",
                                  "acc_thm_pair6", "acc_thm_pair7", "acc_thm_pair8", "acc_thm_pair9", "acc_thm_pair10"]

    RT_condition.columns = ["RT_neu", "RT_tax", "RT_thm"]
    RT_condition_blk.columns = ["RT_neu_blk1", "RT_neu_blk2", "RT_neu_blk3", "RT_neu_blk4", "RT_neu_blk5", "RT_neu_blk6",
                                "RT_neu_blk7", "RT_neu_blk8", "RT_neu_blk9", "RT_neu_blk10", "RT_tax_blk1", "RT_tax_blk2",
                                "RT_tax_blk3", "RT_tax_blk4", "RT_tax_blk5", "RT_tax_blk6", "RT_tax_blk7", "RT_tax_blk8",
                                "RT_tax_blk9", "RT_tax_blk10", "RT_thm_blk1", "RT_thm_blk2", "RT_thm_blk3", "RT_thm_blk4",
                                "RT_thm_blk5", "RT_thm_blk6", "RT_thm_blk7", "RT_thm_blk8", "RT_thm_blk9", "RT_thm_blk10"]

    RT_condition_objs.columns = ["RT_neu_pair1", "RT_neu_pair2", "RT_neu_pair3", "RT_neu_pair4", "RT_neu_pair5",
                                 "RT_neu_pair6", "RT_neu_pair7", "RT_neu_pair8", "RT_neu_pair9", "RT_neu_pair10",
                                 "RT_tax_pair1", "RT_tax_pair2", "RT_tax_pair3", "RT_tax_pair4", "RT_tax_pair5",
                                 "RT_tax_pair6", "RT_tax_pair7", "RT_tax_pair8", "RT_tax_pair9", "RT_tax_pair10",
                                 "RT_thm_pair1", "RT_thm_pair2", "RT_thm_pair3", "RT_thm_pair4", "RT_thm_pair5",
                                 "RT_thm_pair6", "RT_thm_pair7", "RT_thm_pair8", "RT_thm_pair9", "RT_thm_pair10"]

    # concat all data into single data frame, update when necessary
    all_data = pd.concat([excluded_data_count, acc_condition, RT_condition, acc_condition_blk, RT_condition_blk,
                          acc_condition_objs, RT_condition_objs], axis=1)
elif exp_ver == "v2":

    misc_data = data_frame_raw.groupby(["par_num"])["mask_opacity"].mean()
    acc_overall = data_frame_raw.groupby(["par_num"])["accuracy"].mean() * 100
    acc_condition = data_frame_raw.groupby(["par_num", "condition"])[
        "accuracy"].mean().unstack(["condition"]) * 100
    acc_objectness = data_frame_raw.groupby(["par_num", "objectness"])[
        "accuracy"].mean().unstack(["objectness"]) * 100
    acc_condition_objectness = data_frame_raw.groupby(["par_num", "condition", "objectness"])[
        "accuracy"].mean().unstack(["condition", "objectness"]) * 100
    all_data = pd.concat([misc_data, acc_overall, acc_condition,
                          acc_objectness, acc_condition_objectness], axis=1)
    all_data.columns = ["mask_opacity", "acc_overall", "acc_neu", "acc_tax", "acc_thm", "acc_obj", "ac   c_non", "acc_neu_obj",
                        "acc_neu_non", "acc_tax_obj", "acc_tax_non", "acc_thm_obj", "acc_thm_non"]
elif exp_ver == "v3":
    # demo_frame = pd.concat(demo_data, sort=False)
    # demo_data = demo_frame[["gender", "hand", "engagement", "difficulty", "age", "qualtrics_session_id"]]

    corr_data = data_frame_raw[(data_frame_raw["accuracy"] == 1)]

    date = data_frame_raw.groupby(["uniqueid"])["date"].unique()

    acc_overall = data_frame_raw.groupby(["uniqueid"])["accuracy"].mean() * 100
    acc_condition = data_frame_raw.groupby(["uniqueid", "condition"])[
        "accuracy"].mean().unstack(["condition"]) * 100
    pressed_key = data_frame_raw.groupby(["uniqueid"])["pressedKey"].mean()
    acc_condition.columns = ["acc_neu", "acc_tax", "acc_thm"]

    acc_detailed = data_frame_raw.groupby(["uniqueid", "condition", "objectness"])[
        "accuracy"].mean().unstack(["condition", "objectness"]) * 100
    acc_detailed.columns = ["acc_neu_obj", "acc_neu_scr",
                            "acc_tax_obj", "acc_tax_scr", "acc_thm_obj", "acc_thm_scr"]

    RT_overall = data_frame_raw.groupby(["uniqueid"])["RT"].mean()
    # RT_condition = corr_data.groupby(["uniqueid", "condition"])["RT"].mean().unstack(["condition"])
    RT_condition = data_frame_raw.groupby(["uniqueid", "condition"])[
        "RT"].mean().unstack(["condition"])

    all_data = pd.concat([date, acc_overall, acc_condition,
                          acc_detailed, RT_overall], axis=1, sort=False)
    all_data = all_data.sort_values(by=["date"])
# Data for graphing
# graph_RT = cm_standard_error(RT_condition)
# graph_RT.to_clipboard(excel=True, sep="\t")
time_elapsed = time.time() - x
RT_condition_blk.to_clipboard(excel=True, sep="\t")
print("success! time elapsed: " + str(round(time_elapsed, 5) * 1000) + " ms")