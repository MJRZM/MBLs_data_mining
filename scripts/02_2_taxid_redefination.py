# coding=utf-8
import argparse
import datetime


def main():
    parser = argparse.ArgumentParser(description="Map taxonomy using taxidlineage and merged databases.")
    parser.add_argument("-tl", "--taxidlineage_db", required=True, help="Path to taxidlineage.dmp database")
    parser.add_argument("-m", "--merged_db", required=True, help="Path to merged.dmp database")
    parser.add_argument("-tc", "--taxcat_db", required=True, help="Path to categories.dmp database")
    parser.add_argument("-a", "--a2t_db", required=True, help="Path to prot.accession2taxid.FULL database")
    parser.add_argument("-d", "--a2t_dead_db", required=True, help="Path to dead_prot.accession2taxid database")
    parser.add_argument("-i", "--input", required=True, help="Input file containing proteins (e.g., tax_not_found.txt)")

    parser.add_argument("-ob", "--out_bacteria", default="protein_found_bacteria.txt",
                        help="Output file for bacteria proteins")
    parser.add_argument("-onb", "--out_non_bacteria", default="protein_found_non_bacteria.txt",
                        help="Output file for non-bacteria proteins")
    parser.add_argument("-onf", "--out_not_found", default="protein_not_found.txt",
                        help="Output file for not found proteins")

    args = parser.parse_args()

    output_found_bacteria = open(args.out_bacteria, 'w')
    output_found_non_bacteria = open(args.out_non_bacteria, 'w')
    output_not_found = open(args.out_not_found, 'w')

    print(datetime.datetime.now())
    print('starting preparing taxcat dictionary')
    taxcat_dic = {}
    with open(args.taxcat_db, 'r') as taxcat:
        for line in taxcat:
            line_list = line.split('\t')
            taxcat_dic[line_list[-1].strip()] = line_list[0].strip()

    print(datetime.datetime.now())
    print('start preparing merged taxid dictionary')
    merged_dic = {}
    with open(args.merged_db, 'r') as merged:
        for line_merged in merged:
            line_merged_list = line_merged.split('\t')
            merged_dic[line_merged_list[0].strip()] = line_merged_list[2].strip()

    print(datetime.datetime.now())
    print('starting preparing taxidlineage dictionary')
    taxidlineage_dic = {}
    with open(args.taxidlineage_db, 'r') as taxidlineage:
        for line_taxidlineage in taxidlineage:
            line_taxidlineage_list = line_taxidlineage.split()
            if len(line_taxidlineage_list) >= 5:
                taxidlineage_dic[line_taxidlineage_list[0].strip()] = line_taxidlineage_list[3].strip()

    print(datetime.datetime.now())
    print('starting preparing accession2taxid dictionary')
    a2t_dic = {}
    counter_a2t = 0
    with open(args.a2t_db, 'r') as a2t:
        for line in a2t:
            counter_a2t += 1
            line_list = line.split('\t')
            a2t_dic[line_list[0].split('.')[0].strip()] = line_list[1].strip()
            if counter_a2t % 100000000 == 0:
                print(str(counter_a2t) + ' sequences passed')
                print(datetime.datetime.now())

    print(datetime.datetime.now())
    print('starting preparing dead accession2taxid dictionary')
    a2t_dead_dic = {}
    with open(args.a2t_dead_db, 'r') as a2t_dead:
        for line2 in a2t_dead:
            line_list2 = line2.split('\t')
            a2t_dead_dic[line_list2[0].split('.')[0].strip()] = line_list2[2].strip()

    input_data = open(args.input, 'r').readlines()
    for item in input_data:
        prot = item.strip()
        if not prot:  # 跳过空行
            continue

        tax = 'placeholder'
        if prot in a2t_dic.keys():
            tax = a2t_dic[prot]
        elif prot in a2t_dead_dic.keys():
            tax = a2t_dead_dic[prot]

        if tax in merged_dic.keys():
            new_tax = merged_dic[tax]
            if new_tax in taxcat_dic.keys():  # 这里修复了之前的逻辑 Bug
                if taxcat_dic[new_tax] == 'B':
                    output_found_bacteria.write(prot + '\n')
                else:
                    output_found_non_bacteria.write(prot + '\n')
            else:
                output_not_found.write(prot + '\n')
        elif tax in taxidlineage_dic.keys():
            if str(taxidlineage_dic[tax]) == str(2):
                output_found_bacteria.write(prot + '\n')
            else:
                output_found_non_bacteria.write(prot + '\n')
        else:
            output_not_found.write(prot + '\n')


if __name__ == "__main__":
    main()