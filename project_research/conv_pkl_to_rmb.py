#from irsl_manip_libs.lib_pkl_to_rmb import make_rmb_data
from irsl_manip_libs.lib_pkl_to_rmb import convert_pickle_to_rmb

##
## convert_pickle_to_rmb('hsrbag000.pkl', 'hsr000.rmb', data_names)
##
if __name__ == "__main__":
    import argparse
    import os
    import glob

    parser = argparse.ArgumentParser(
        description="Convert HSR pickle data (.pkl) to RMB format (.rmb). "
                    "If pkl_path is a directory, all *.pkl under it will be converted."
    )
    parser.add_argument(
        "pkl_path",
        type=str,
        help="input pickle file() OR directory containing pickle files()"
    )
    parser.add_argument(
        "rmb_name",
        type=str,
        nargs="?",
        help="output rmb file (used only when pkl_path is a single pickle file)"
    )
    parser.add_argument(
        "--outdir",
        type=str,
        default=None,
        help="Directory to store output RMB files (directory mode only)"
    )

    args = parser.parse_args()

    # ==========================================================
    #  DIRECTORY MODE
    # ==========================================================
    if os.path.isdir(args.pkl_path):
        input_dir = args.pkl_path
        pkl_files = sorted(
            glob.glob(os.path.join(input_dir, "**", "*.pkl"), recursive=True)
        )

        if not pkl_files:
            print("[WARN] No .pkl files found.")
            raise SystemExit(0)

        if args.outdir is None:
            print("[ERROR] Directory mode requires --outdir OUTPUT_FOLDER")
            print("Example:")
            print("  python convert_pickle_to_rmb.py pkls/ --outdir rmbs/")
            raise SystemExit(1)

        outdir = args.outdir
        os.makedirs(outdir, exist_ok=True)

        print(f"[INFO] Directory mode")
        print(f"[INFO] Input pkls : {input_dir}")
        print(f"[INFO] Output dir : {outdir}")
        print(f"[INFO] Found {len(pkl_files)} pkl files")

        for pkl_file in pkl_files:
            base = os.path.basename(pkl_file)          # xxx.pkl
            rmb_filename = os.path.splitext(base)[0] + ".rmb"
            out_path = os.path.join(outdir, rmb_filename)

            print(f"[INFO] Converting: {pkl_file} -> {out_path}")
            try:
                convert_pickle_to_rmb(
                    pkl_file,
                    out_path,
                )
            except Exception as e:
                print(f"[ERROR] Failed to convert {pkl_file}: {e}")

    # ==========================================================
    #  SINGLE-FILE MODE
    # ==========================================================
    else:
        if args.rmb_name is None:
            print("[ERROR] Single-file mode requires rmb_name.")
            print("Usage:")
            print("  python convert_pickle_to_rmb.py input.pkl output.rmb")
            raise SystemExit(1)

        print("[INFO] File mode")
        print(f"[INFO] input  pkl : {args.pkl_path}")
        print(f"[INFO] output rmb : {args.rmb_name}")

        convert_pickle_to_rmb(
            args.pkl_path,
            args.rmb_name,
        )
