# -*- coding: utf-8 -*-

import argparse
import json
import os
from collections import OrderedDict

parser = argparse.ArgumentParser(description="Alat sederhana untuk memeriksa file konfigurasi JSON Anda.")
parser.add_argument(
    "-m", "--method-jsons", nargs="+", required=True, help="File JSON tentang semua metode."
)
parser.add_argument(
    "-d", "--dataset-jsons", nargs="+", required=True, help="File JSON tentang semua dataset."
)
args = parser.parse_args()

for method_json, dataset_json in zip(args.method_jsons, args.dataset_jsons):
    with open(method_json, encoding="utf-8", mode="r") as f:
        methods_info = json.load(f, object_hook=OrderedDict)  # Memuat dengan urutan
    with open(dataset_json, encoding="utf-8", mode="r") as f:
        datasets_info = json.load(f, object_hook=OrderedDict)  # Memuat dengan urutan

    total_msgs = []
    for method_name, method_info in methods_info.items():
        print(f"Memeriksa {method_name} ...")
        for dataset_name, results_info in method_info.items():
            if results_info is None:
                continue

            dataset_mask_info = datasets_info[dataset_name]["mask"]
            mask_path = dataset_mask_info["path"]
            mask_suffix = dataset_mask_info["suffix"]

            dir_path = results_info["path"]
            file_prefix = results_info.get("prefix", "")
            file_suffix = results_info["suffix"]

            if not os.path.exists(dir_path):
                total_msgs.append(f"{dir_path} tidak ada")
                continue
            elif not os.path.isdir(dir_path):
                total_msgs.append(f"{dir_path} bukan jalur folder yang valid")
                continue
            else:
                pred_names = [
                    name[len(file_prefix) : -len(file_suffix)]
                    for name in os.listdir(dir_path)
                    if name.startswith(file_prefix) and name.endswith(file_suffix)
                ]
                if len(pred_names) == 0:
                    total_msgs.append(f"{dir_path} tidak mengandung file dengan prefix {file_prefix} dan suffix {file_suffix}")
                    continue

            mask_names = [
                name[: -len(mask_suffix)]
                for name in os.listdir(mask_path)
                if name.endswith(mask_suffix)
            ]
            
            # Tambahkan print statement untuk debugging
            print(f"Predicted names: {pred_names}")
            print(f"Ground truth names: {mask_names}")
            
            intersection_names = set(mask_names).intersection(set(pred_names))
            if len(intersection_names) == 0:
                total_msgs.append(f"Nama file di {dir_path} tidak cocok dengan ground truth di {mask_path}")
            elif len(intersection_names) != len(mask_names):
                difference_names = set(mask_names).difference(pred_names)
                total_msgs.append(
                    f"Jumlah data ({len(list(pred_names))}) di {dir_path} tidak sama dengan ground truth ({len(list(mask_names))}) di {mask_path}"
                )

    if total_msgs:
        print(*total_msgs, sep="\n")
    else:
        print(f"{method_json} & {dataset_json} tampak normal")
