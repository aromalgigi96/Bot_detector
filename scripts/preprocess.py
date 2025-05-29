# preprocess.py

import os
import glob
import argparse

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


def preprocess_folder(input_dir, output_dir, chunksize=100_000):
    os.makedirs(output_dir, exist_ok=True)

    for csv_path in glob.glob(os.path.join(input_dir, "*.csv")):
        base = os.path.basename(csv_path).replace(".csv", ".parquet")
        out_path = os.path.join(output_dir, base)

        writer = None
        for chunk in pd.read_csv(
            csv_path,
            chunksize=chunksize,
            low_memory=False,
            dtype=str
        ):
            # 1) Parse Timestamp explicitly
            chunk["Timestamp"] = pd.to_datetime(
                chunk["Timestamp"],
                format="%d/%m/%Y %H:%M:%S",
                errors="coerce",
                dayfirst=True
            )

            # 2) Coerce numeric columns and fill zeros (leave Timestamp as datetime)
            non_date = [c for c in chunk.columns if c != "Timestamp"]
            chunk[non_date] = chunk[non_date].apply(pd.to_numeric, errors="coerce")
            chunk[non_date] = chunk[non_date].fillna(0.0)

            # 3) Enforce uniform dtype: all non-date columns as float64
            for col in non_date:
                chunk[col] = chunk[col].astype("float64")

            # 4) Convert to Arrow Table and write out
            table = pa.Table.from_pandas(chunk, preserve_index=False)
            if writer is None:
                writer = pq.ParquetWriter(
                    out_path,
                    table.schema,
                    compression="snappy"
                )
            writer.write_table(table)

        if writer:
            writer.close()
            print(f"✔️  Written {out_path}")
        else:
            print(f"⚠️  No data in {csv_path}, skipped")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir",  required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--chunksize",  type=int, default=100_000)
    args = parser.parse_args()

    preprocess_folder(args.input_dir, args.output_dir, args.chunksize)
