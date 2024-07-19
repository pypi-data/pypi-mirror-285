#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define SPO2_MIN_VALUE 110.0  // Adjusted to float

typedef struct {
    int *onset;
    int *duration;
    float *level;  // Changed level to float to match spo2_arr changes
    int size;
} DesaturationResult;

DesaturationResult detect_oxygen_desaturation(float *spo2_arr, int arr_size, int duration_max, float spo2_des_min_thre);

DesaturationResult detect_oxygen_desaturation(float *spo2_arr, int arr_size, int duration_max, float spo2_des_min_thre) {
    float spo2_max = spo2_arr[0];
    int spo2_max_index = 1;
    float spo2_min = SPO2_MIN_VALUE;
    int *des_onset_pred_set = (int *)malloc(arr_size * sizeof(int));
    int *des_duration_pred_set = (int *)malloc(arr_size * sizeof(int));
    float *des_level_set = (float *)malloc(arr_size * sizeof(float));  // Adjusted to float
    int des_onset_pred_point = 0;
    int des_flag = 0;
    int ma_flag = 0;
    float spo2_des_max_thre = 50.0;  // Adjusted to float
    int duration_min = 5;
    int *prob_end = (int *)malloc(arr_size * sizeof(int));
    int prob_end_size = 0;
    int des_onset_pred_set_size = 0;
    int des_duration_pred_set_size = 0;
    int des_level_set_size = 0;

    for (int i = 0; i < arr_size; i++) {
        float current_value = spo2_arr[i];
        float des_percent = spo2_max - current_value;

        if (ma_flag && (des_percent < spo2_des_max_thre)) {
            if (des_flag && prob_end_size > 0) {
                des_onset_pred_set[des_onset_pred_set_size++] = des_onset_pred_point;
                des_duration_pred_set[des_duration_pred_set_size++] = prob_end[prob_end_size - 1] - des_onset_pred_point;
                float des_level_point = spo2_max - spo2_min;
                des_level_set[des_level_set_size++] = des_level_point;
            }
            spo2_max = current_value;
            spo2_max_index = i;
            ma_flag = 0;
            des_flag = 0;
            spo2_min = SPO2_MIN_VALUE;
            prob_end_size = 0;
            continue;
        }

        if (des_percent >= spo2_des_min_thre) {
            if (des_percent > spo2_des_max_thre) {
                ma_flag = 1;
            } else {
                des_onset_pred_point = spo2_max_index;
                des_flag = 1;
                if (current_value < spo2_min) {
                    spo2_min = current_value;
                }
            }
        }

        if (current_value >= spo2_max && !des_flag) {
            spo2_max = current_value;
            spo2_max_index = i;
        } else if (des_flag) {
            if (current_value > spo2_min) {
                if (current_value > spo2_arr[i - 1]) {
                    prob_end[prob_end_size++] = i;
                }

                if (current_value <= spo2_arr[i - 1] && spo2_arr[i - 1] < spo2_arr[i - 2]) {
                    int spo2_des_duration = prob_end[prob_end_size - 1] - spo2_max_index;
                    if (spo2_des_duration < duration_min) {
                        spo2_max = spo2_arr[i - 2];
                        spo2_max_index = i - 2;
                        spo2_min = SPO2_MIN_VALUE;
                        des_flag = 0;
                        prob_end_size = 0;
                        continue;
                    } else {
                        if (duration_min <= spo2_des_duration && spo2_des_duration <= duration_max) {
                            des_onset_pred_set[des_onset_pred_set_size++] = des_onset_pred_point;
                            des_duration_pred_set[des_duration_pred_set_size++] = spo2_des_duration;
                            float des_level_point = spo2_max - spo2_min;
                            des_level_set[des_level_set_size++] = des_level_point;
                        } else {
                            des_onset_pred_set[des_onset_pred_set_size++] = des_onset_pred_point;
                            des_duration_pred_set[des_duration_pred_set_size++] = prob_end[0] - des_onset_pred_point;
                            float des_level_point = spo2_max - spo2_min;
                            des_level_set[des_level_set_size++] = des_level_point;
                            int remain_spo2_arr_size = i + 1 - prob_end[0];
                            float *remain_spo2_arr = (float *)malloc(remain_spo2_arr_size * sizeof(float));
                            memcpy(remain_spo2_arr, &spo2_arr[prob_end[0]], remain_spo2_arr_size * sizeof(float));
                            DesaturationResult result = detect_oxygen_desaturation(remain_spo2_arr, remain_spo2_arr_size, duration_max, spo2_des_min_thre);
                            for (int j = 0; j < result.size; j++) {
                                des_onset_pred_set[des_onset_pred_set_size++] = prob_end[0] + result.onset[j];
                                des_duration_pred_set[des_duration_pred_set_size++] = result.duration[j];
                                des_level_set[des_level_set_size++] = result.level[j];
                            }
                            free(remain_spo2_arr);
                            free(result.onset);
                            free(result.duration);
                            free(result.level);
                        }
                        spo2_max = spo2_arr[i - 2];
                        spo2_max_index = i - 2;
                        spo2_min = SPO2_MIN_VALUE;
                        des_flag = 0;
                        prob_end_size = 0;
                    }
                }
            }
        }
    }

    DesaturationResult result;
    result.onset = (int *)malloc(des_onset_pred_set_size * sizeof(int));
    result.duration = (int *)malloc(des_duration_pred_set_size * sizeof(int));
    result.level = (float *)malloc(des_level_set_size * sizeof(float));
    result.size = des_onset_pred_set_size;

    memcpy(result.onset, des_onset_pred_set, des_onset_pred_set_size * sizeof(int));
    memcpy(result.duration, des_duration_pred_set, des_duration_pred_set_size * sizeof(int));
    memcpy(result.level, des_level_set, des_level_set_size * sizeof(float));

    free(des_onset_pred_set);
    free(des_duration_pred_set);
    free(des_level_set);
    free(prob_end);

    return result;
}

void free_memory(void* ptr) {
    free(ptr);
}