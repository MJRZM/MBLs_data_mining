# coding:utf-8
import argparse
import datetime
import json


def main():
    parser = argparse.ArgumentParser(description="Map protein accessions to taxonomy categories.")
    parser.add_argument("-t", "--taxcat_db", required=True, help="Path to taxcat categories.dmp database")
    parser.add_argument("-a", "--a2t_db", required=True, help="Path to prot.accession2taxid.FULL database")
    parser.add_argument("-d", "--a2t_dead_db", required=True, help="Path to dead_prot.accession2taxid database")
    parser.add_argument("-i", "--input", required=True, help="Input file containing protein IDs (e.g., input_id.txt)")

    parser.add_argument("-of", "--out_found", default="found_proteins.txt",
                        help="Output file for found bacterial proteins")
    parser.add_argument("-om", "--out_missing", default="missing_proteins.txt", help="Output file for missing proteins")
    parser.add_argument("-on", "--out_non_bacterial", default="non_bactrial.txt",
                        help="Output file for non-bacterial proteins")
    parser.add_argument("-ot", "--out_tax_not_found", default="tax_not_found.txt",
                        help="Output file for taxonomy not found")

    args = parser.parse_args()

    print(datetime.datetime.now())
    print('starting prepareing taxcat dictionary')
    taxcat_dic = {}
    with open(args.taxcat_db, 'r') as taxcat:
        for line in taxcat:
            line_list = line.split('\t')
            taxcat_dic[line_list[-1].strip()] = line_list[0].strip()

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

    INPUT = open(args.input, 'r').readlines()
    proteins = []
    for item in INPUT:
        proteins.append(item.strip().split('.')[0])

    OUTPUT_FOUND = open(args.out_found, 'w')
    OUTPUT_MISSING = open(args.out_missing, 'w')
    OUTPUT_NON_BACTERIAL = open(args.out_non_bacterial, 'w')
    TAX_NOT_FOUND = open(args.out_tax_not_found, 'w')

    total_protein_number = len(proteins)
    counter = 1
    for protein in proteins:
        tax = 'N'
        print(datetime.datetime.now())
        print(protein)
        print(str(counter) + ' of ' + str(total_protein_number))
        counter += 1
        if (protein not in a2t_dic.keys()) and (protein not in a2t_dead_dic.keys()):
            OUTPUT_MISSING.write(protein + '\n')
        elif protein in a2t_dic.keys():
            if a2t_dic[protein] not in taxcat_dic.keys():
                TAX_NOT_FOUND.write(protein + '\n')
            else:
                tax = taxcat_dic[a2t_dic[protein]]
        else:
            if a2t_dead_dic[protein] not in taxcat_dic.keys():
                TAX_NOT_FOUND.write(protein + '\n')
            else:
                tax = taxcat_dic[a2t_dead_dic[protein]]

        if tax == 'B':
            OUTPUT_FOUND.write(protein + '\n')
        elif tax == 'N':
            continue
        else:
            OUTPUT_NON_BACTERIAL.write(protein + '\n')


if __name__ == "__main__":
    main()