import argparse
import datetime
import sys


def main():
    parser = argparse.ArgumentParser(description="Process and filter large BLAST result files.")
    parser.add_argument("-i", "--input", required=True, help="Input BLAST result file (e.g., 40GB txt file)")
    parser.add_argument("-od", "--output_data", required=True, help="Filtered output data file")
    parser.add_argument("-oi", "--output_ids", required=True, help="Extracted IDs output file")

    args = parser.parse_args()

    print(f"Start time: {datetime.datetime.now()}")

    with open(args.output_data, 'a', buffering=1024 * 1024) as out_numbers, \
            open(args.output_ids, 'w', buffering=1024 * 1024) as out_id, \
            open(args.input, 'r', buffering=1024 * 1024) as infile:

        seen_ids = set()
        counter = 0

        for line in infile:
            line_stripped = line.strip()
            if not line_stripped:
                continue

            if line_stripped.startswith('#'):
                if len(line_stripped) > 2 and line_stripped[2] not in ('D', 'B', 'Q', 'F'):
                    out_numbers.write(line)
                    counter += 1
                    if counter % 500000 == 0:
                        print(f"Processed {counter} lines... {datetime.datetime.now()}")

            else:
                parts = line_stripped.split('\t', 3)

                if len(parts) > 2:
                    prot_id = parts[1]
                    try:
                        if float(parts[2]) >= 25.0:
                            if prot_id not in seen_ids:
                                seen_ids.add(prot_id)
                                out_id.write(prot_id + '\n')
                    except ValueError:
                        continue

    print(f"Finished. Total lines processed: {counter}")
    print(f"End time: {datetime.datetime.now()}")


if __name__ == "__main__":
    main()