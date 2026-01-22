#!/usr/bin/env python3

# %autoindent
#
# under ROS environment
#
from lib_bag_to_pkl import mainFunction
import argparse
import os
import glob

if __name__ == "__main__":


    parser = argparse.ArgumentParser(
        description="Convert HSR rosbag(s) to pickle. "
                    "If bag_path is a directory, all *.bag under it will be converted."
    )
    parser.add_argument("bag_path", type=str,
                        help="input rosbag file(single-file mode) OR directory containing rosbag files(directory mode)")
    parser.add_argument("pkl_name", type=str, nargs="?",
                        help="output pickle file (required at single-file mode only)")
    parser.add_argument("--outdir", type=str, default=None,
                        help="Directory to store output pickle files (directory mode only)")
    args = parser.parse_args()

    # ==========================================================
    #  DIRECTORY MODE
    # ==========================================================
    if os.path.isdir(args.bag_path):
        input_dir = args.bag_path
        bag_files = sorted(glob.glob(os.path.join(input_dir, "**", "*.bag"), recursive=True))

        if not bag_files:
            print("[WARN] No .bag files found.")
            raise SystemExit(0)

        # 出力フォルダ必須
        if args.outdir is None:
            print("[ERROR] Directory mode requires --outdir OUTPUT_FOLDER")
            print("Example:")
            print("  python convert_bag_to_pickle.py data/ --outdir output_pkl/")
            raise SystemExit(1)

        outdir = args.outdir
        os.makedirs(outdir, exist_ok=True)

        print(f"[INFO] Directory mode")
        print(f"[INFO] Input bags : {input_dir}")
        print(f"[INFO] Output dir : {outdir}")
        print(f"[INFO] Found {len(bag_files)} bag files")

        for bag_file in bag_files:
            base = os.path.basename(bag_file)          # xxx.bag
            pkl_name = os.path.splitext(base)[0] + ".pkl"
            out_path = os.path.join(outdir, pkl_name)

            print(f"[INFO] Converting: {bag_file} -> {out_path}")
            try:
                mainFunction(bag_file, out_path)
            except Exception as e:
                print(f"[ERROR] Failed to convert {bag_file}: {e}")

    # ==========================================================
    #  SINGLE-FILE MODE
    # ==========================================================
    else:
        if args.pkl_name is None:
            print("[ERROR] Single-file mode requires pkl_name.")
            print("Usage:")
            print("  python convert_bag_to_pickle.py input.bag output.pkl")
            raise SystemExit(1)

        print(f"[INFO] File mode")
        print(f"[INFO] Input bag : {args.bag_path}")
        print(f"[INFO] Output pkl: {args.pkl_name}")

        mainFunction(args.bag_path, args.pkl_name)
