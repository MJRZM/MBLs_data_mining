import argparse
import datetime
import sys

def main():
    # 使用 argparse 设置命令行参数，隐去自己原有的特定文件名
    parser = argparse.ArgumentParser(description="Process and filter large BLAST result files.")
    parser.add_argument("-i", "--input", required=True, help="Input BLAST result file (e.g., 40GB txt file)")
    parser.add_argument("-od", "--output_data", required=True, help="Filtered output data file")
    parser.add_argument("-oi", "--output_ids", required=True, help="Extracted IDs output file")
    
    args = parser.parse_args()

    print(f"Start time: {datetime.datetime.now()}")

    # 使用 buffer 缓冲区加速写入
    with open(args.output_data, 'a', buffering=1024 * 1024) as out_numbers, \
         open(args.output_ids, 'w', buffering=1024 * 1024) as out_id, \
         open(args.input, 'r', buffering=1024 * 1024) as infile:
        
        seen_ids = set()  # 仅保留 Set 用于快速查重
        counter = 0

        for line in infile:
            # 极简预处理，追求速度
            line_stripped = line.strip()
            if not line_stripped:
                continue

            # 处理 Header (# 开头的行)
            if line_stripped.startswith('#'):
                # 快速检查特定字符，避免复杂的 split
                # 假设我们要检查的是这行里的某些特定标记
                if len(line_stripped) > 2 and line_stripped[2] not in ('D', 'B', 'Q', 'F'):
                    out_numbers.write(line)  # 直接写入原行，保留换行符（如果原行有）
                    counter += 1
                    if counter % 500000 == 0:  # 数据量大，每50万行打印一次即可
                        print(f"Processed {counter} lines... {datetime.datetime.now()}")

            # 处理数据行
            else:
                # 使用 maxsplit=2 限制分割次数，大幅提升速度
                # 因为我们只需要前三列：[0]空/其他, [1]ID, [2]Score
                parts = line_stripped.split('\t', 3)

                if len(parts) > 2:
                    prot_id = parts[1]
                    try:
                        # 快速转换并比较
                        if float(parts[2]) >= 25.0:
                            if prot_id not in seen_ids:
                                seen_ids.add(prot_id)
                                # 【关键优化】立即写入 ID 文件，不再存入列表
                                out_id.write(prot_id + '\n')
                    except ValueError:
                        continue

    print(f"Finished. Total lines processed: {counter}")
    print(f"End time: {datetime.datetime.now()}")

if __name__ == "__main__":
    main()