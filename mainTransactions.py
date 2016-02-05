import os
import os.path
import re
import sys

from reportHTMLTransactions import ReportHTMLWriterTransactions
from findTransactions import ParseSourceFile

"""
Ideas/TODOs:
- Transaction count dropped by about 50. Need to find if normal. Up to now it is, it was matching
things like EndTransactionOptions().
"""

def parse_file(file_path):
    parser = ParseSourceFile()
    res_list_dict = parser.parse(file_path)
    return res_list_dict


def parse_files(dist_dir, txt_file_path):
    set_of_files = set()
    for root, dirs, files in os.walk(txt_file_path):
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext == ".txt" and not file == "results.txt":
                full_txt_file_path = os.path.join(root, file)
                with open(full_txt_file_path) as fh:
                    lines = fh.readlines()
                    for line in lines:
                        first_ws = line.find("fulls")
                        path = line[:first_ws]
                        path = path.strip()
                        set_of_files.add(path)

    list_of_list_of_dicts = list()
    for file in set_of_files:
        print(file)
        a_list = parse_file(file)
        list_of_list_of_dicts.append((file, a_list))

    with open(os.path.join(dist_dir, "transactions.html"), "w") as fh:
        writer = ReportHTMLWriterTransactions(fh)
        writer.write(list_of_list_of_dicts)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("not enough args.")
    else:
        the_path = sys.argv[1]
        dir_cwd = os.getcwd()
        final_dir = os.path.join(dir_cwd, "dist")
        parse_files(final_dir, the_path)
