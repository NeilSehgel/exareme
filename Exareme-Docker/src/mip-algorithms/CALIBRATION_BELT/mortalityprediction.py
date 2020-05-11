import numpy as np
import pandas as pd
import argparse
from scipy.special import expit


def predict_6month_mortality(record, model="core"):
    msg = f"model parameter should be core, extended or lab."
    assert model in {"core", "extended", "lab"}, msg
    if model == "core":
        total_score = sum_score_core(record)
        lp = -2.55 + 0.275 * total_score
    if model == "extended":
        total_score = sum_score_core(record) + subscore_ct(record)
        lp = -2.98 + 0.256 * total_score
    elif model == "lab":
        total_score = (
            sum_score_core(record) + subscore_ct(record) + subscore_lab(record)
        )
        lp = -3.42 + 0.216 * total_score
    return expit(lp)


def sum_score_core(record):
    return age_score(record) + motor_score(record) + pupillary_reactivity_score(record)


def subscore_ct(record):
    return (
        hypoxia_score(record)
        + hypotension_score(record)
        + ct_classification_score(record)
        + epidural_hematoma_score(record)
    )


def subscore_lab(record):
    return glucose_score(record) + hemoglobin_score(record)


def age_score(record):
    age_value = record.age_value
    if age_value <= 30:
        return 0
    elif 30 < age_value <= 39:
        return 1
    elif 40 < age_value <= 49:
        return 2
    elif 50 < age_value <= 59:
        return 3
    elif 60 < age_value <= 69:
        return 4
    elif 70 < age_value:
        return 5


def motor_score(record):
    gcs_motor_response_scale = record.gcs_motor_response_scale
    if gcs_motor_response_scale in {"1", "2"}:
        return 6
    elif gcs_motor_response_scale == "3":
        return 4
    elif gcs_motor_response_scale == "4":
        return 2
    elif gcs_motor_response_scale in {"5", "6"}:
        return 0
    elif gcs_motor_response_scale in {"Untestable", "Unknown"}:
        return 3
    else:
        msg = (
            f"Unknown category {gcs_motor_response_scale} "
            f"for gcs_motor_response_scale."
        )
        raise ValueError(msg)


def pupillary_reactivity_score(record):
    pupil_reactivity_right_eye_result = record.pupil_reactivity_right_eye_result
    pupil_reactivity_left_eye_result = record.pupil_reactivity_left_eye_result
    score = 0
    if pupil_reactivity_right_eye_result == "Nonreactive":
        score += 2
    elif pupil_reactivity_right_eye_result in {"Sluggish", "Brisk"}:
        pass
    else:
        msg = (
            f"Unknown category {pupil_reactivity_right_eye_result} "
            f"for pupil_reactivity_right_eye_result."
        )
        raise ValueError(msg)
    if pupil_reactivity_left_eye_result == "Nonreactive":
        score += 2
    elif pupil_reactivity_left_eye_result in {"Sluggish", "Brisk"}:
        pass
    else:
        msg = (
            f"Unknown category {pupil_reactivity_left_eye_result} "
            f"for pupil_reactivity_left_eye_result."
        )
        raise ValueError(msg)
    return score


def hypoxia_score(record):
    hypoxic_episode_indicator = record.hypoxic_episode_indicator
    if hypoxic_episode_indicator in {"Yes", "Suspected"}:
        return 1
    elif hypoxic_episode_indicator == "No":
        return 0
    else:
        msg = (
            f"Unknown category {hypoxic_episode_indicator} "
            f"for hypoxic_episode_indicator."
        )
        raise ValueError(msg)


def hypotension_score(hypotensive_episode_indicator):
    hypotensive_episode_indicator = bad_record.hypotensive_episode_indicator
    if hypotensive_episode_indicator in {"Yes", "Suspected"}:
        return 2
    elif hypotensive_episode_indicator == "No":
        return 0
    else:
        msg = (
            f"Unknown category {hypotensive_episode_indicator} "
            f"for hypotensive_episode_indicator."
        )
        raise ValueError(msg)


def ct_classification_score(record):
    marshall_ct_classification_code = record.marshall_ct_classification_code
    if marshall_ct_classification_code == "1":
        return -2
    elif marshall_ct_classification_code == "2":
        return 0
    elif marshall_ct_classification_code in {"3", "4"}:
        return 2
    elif marshall_ct_classification_code in {"5", "6"}:
        return 2
    else:
        msg = (
            f"Unknown category {marshall_ct_classification_code} "
            f"for marshall_ct_classification_code."
        )
        raise ValueError(msg)


def epidural_hematoma_score(record):
    epidural_hematoma_anatomic_status = record.epidural_hematoma_anatomic_status
    if epidural_hematoma_anatomic_status == "Present":
        return -2
    elif epidural_hematoma_anatomic_status == "Absent":
        return 0
    else:
        msg = (
            f"Unknown category {epidural_hematoma_anatomic_status} "
            f"for epidural_hematoma_anatomic_status."
        )
        raise ValueError(msg)


def glucose_score(record):
    laboratory_procedure_glucose_value = record.laboratory_procedure_glucose_value
    if laboratory_procedure_glucose_value < 6:
        return 0
    elif 6 <= laboratory_procedure_glucose_value < 9:
        return 1
    elif 9 <= laboratory_procedure_glucose_value < 12:
        return 2
    elif 12 <= laboratory_procedure_glucose_value < 15:
        return 3
    elif 15 <= laboratory_procedure_glucose_value:
        return 4


def hemoglobin_score(record):
    laboratory_procedure_hemoglobin_value = record.laboratory_procedure_hemoglobin_value
    if laboratory_procedure_hemoglobin_value < 9:
        return 3
    elif 9 <= laboratory_procedure_hemoglobin_value < 12:
        return 2
    elif 12 <= laboratory_procedure_hemoglobin_value < 15:
        return 1
    elif 15 <= laboratory_procedure_hemoglobin_value:
        return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source_csv", required=True, help="File path for original csv."
    )
    parser.add_argument(
        "--destination_csv", required=True, help="File path for new " "csv."
    )
    args = parser.parse_args()
    source_csv = args.source_csv
    destination_csv = args.destination_csv

    df = pd.read_csv(source_csv)
    df["mortality"] = pd.Series(np.zeros(len(df)), index=df.index)
    for idx, record in df.iterrows():
        mortality = predict_6month_mortality(record)
        df.at[idx, "mortality"] = mortality
    df.to_csv(destination_csv)
