import argparse
from pathlib import Path
import pandas as pd

def process_file(csv_path: Path, out_dir: Path, chunksize: int):
    out_path = out_dir / f"{csv_path.stem}.parquet"
    for chunk in pd.read_csv(csv_path, chunksize=chunksize):
        if "Timestamp" in chunk:
            chunk["Timestamp"] = pd.to_datetime(chunk["Timestamp"], errors="coerce")
        for col in chunk.select_dtypes(include="object").columns.difference(["Label"]):
            chunk[col] = pd.to_numeric(chunk[col], errors="coerce")
        chunk.to_parquet(
            out_path,
            index=False,
            engine="fastparquet",
            compression="snappy",
            append=out_path.exists()
        )
    print(f"Written {out_path}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input-dir",  type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--chunksize",  type=int,   default=200000)
    args = p.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for f in sorted(args.input_dir.glob("*.csv")):
        process_file(f, args.output_dir, args.chunksize)

if __name__ == "__main__":
    main()
