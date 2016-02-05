import os
import os.path
import sys

import parseUtil
from parseHeader import *
from parseSource import *
from detailedHTMLReportWriter import *

from pathlib import Path

"""
Ideas:
- Missing some Partial UpdateAllViews because they pass 0 for the Canvas first param. (this is done I believe)
- Report errors as UpdateAllViews calls might be hidden in those files.
- Better regex definition for partial and full. (Full is only a couple of hints, the rest is partial)
- Search for class declarations in source files.

Bugs:
- Transaction bug with file LinkedFilesDialog.cpp, updAllViews line number doesn't match commit number and ctor is missing.

Refactorings:
- Clean up main.
- Extract specific patterns RE from parsers. Allow to search for different Keywords. Max 2 REs (for diff param lists)
"""


def add_category_to_file_dict(file_dict, catstr, file_info):
    if not file_dict.get(catstr):
        file_dict[catstr] = list()
    file_dict[catstr].append(file_info)


def make_file_for_category(file_dict, catstr, dir_path, file_name):
    file_path = os.path.join(dir_path, file_name)

    with open(file_path, "w") as fh:
        for file_info in file_dict[catstr]:
            the_file_path = file_info[0]
            counts = file_info[1:]
            fh.write("{file_path}     fulls={full} partials={partial}".format(
                file_path=the_file_path, full=counts[0], partial=counts[1]))
            fh.write("\n")


def create_html_head(fh):
    fh.write("<html>\n")
    fh.write("<head>\n")
    fh.write("<link rel='stylesheet' type='text/css' href='style.css'>\n")
    fh.write("</head>\n")


def end_html(fh):
    fh.write("</html>\n")


def create_html_body(fh):
    fh.write("<body>\n")


def end_html_body(fh):
    fh.write("</body>\n")


def create_table_header(fh):
    fh.write("<tr>\n")
    fh.write("<th>File</th>\n")
    fh.write("<th>Full</th>\n")
    fh.write("<th>Partial</th>\n")
    fh.write("</tr>\n")


def make_htmlfile_for_category(file_dict, catstr, dir_path, file_name):
    file_path = os.path.join(dir_path, file_name)
    with open(file_path, "w") as fh:
        create_html_head(fh)
        create_html_body(fh)
        fh.write("<table>\n")
        create_table_header(fh)
        for file_info in file_dict[catstr]:
            the_file_path = file_info[0]
            counts = file_info[1:]

            fh.write("<tr>\n")
            fh.write("<td>{file_path}</td>\n<td style='text-align:center'>{full}</td>\n<td style='text-align:center'>{partial}</td>".format(
                file_path=the_file_path, full=counts[0], partial=counts[1]))
            fh.write("\n")
            fh.write("</tr>\n")

        fh.write("</table>\n")
        end_html_body(fh)
        end_html(fh)


def make_html_detailed_report_for_categories(final_dir, file_dict, categories):
    for cat in categories:
        cat_key = cat[0]
        cat_file_name = cat[1]
        with open(os.path.join(final_dir, cat_file_name), "w") as fh:
            writer = DetailedHTMLReportWriter(fh)
            writer.write(file_dict, cat_key)


def parse(path_to_search, dir_for_output):
    file_list = list()
    file_dict = dict()

    patt_editmodemgr = re.compile("EditModeMgr")
    patt_editor = re.compile("Editor")
    patt_handler = re.compile("Handler")
    patt_dialog = re.compile("Dialog")
    patt_element = re.compile("Elem")

    EDITMODEMGR_KEY = "EditModeMgr"
    EDITORS_KEY = "Editors"
    HANDLERS_KEY = "Handlers"
    DIALOGS_KEY = "Dialogs"
    ELEMENT_KEY = "Element"
    OTHERS_KEY = "Others"
    for root, dirs, files in os.walk(path_to_search):
        for file in files:
            ext = os.path.splitext(file)[1]
            file_path = os.path.join(root, file)
            if ext == ".cpp":
                result = parse_file(file_path)
                if result[0]:
                    header_dict = parse_header(file_path)
                    line_counts = result[1:]
                    file_list.append((file_path, line_counts))

                    result_editmode_mgr = patt_editmodemgr.search(file_path)
                    result_editor = patt_editor.search(file_path)
                    result_handler = patt_handler.search(file_path)
                    result_dialog = patt_dialog.search(file_path)
                    result_elem = patt_element.search(file_path)

                    # see parse_file for what is in result.
                    file_info = (file_path, result[1], result[2], result[3], result[4], header_dict)
                    if result_editmode_mgr:
                        add_category_to_file_dict(file_dict, EDITMODEMGR_KEY, file_info)

                    if result_editor:
                        add_category_to_file_dict(file_dict, EDITORS_KEY, file_info)
                    elif result_handler:
                        add_category_to_file_dict(file_dict, HANDLERS_KEY, file_info)
                    elif result_dialog:
                        add_category_to_file_dict(file_dict, DIALOGS_KEY, file_info)
                    elif result_elem:
                        add_category_to_file_dict(file_dict, ELEMENT_KEY, file_info)
                    else:
                        add_category_to_file_dict(file_dict, OTHERS_KEY, file_info)

    full = 0
    partial = 0
    for info in file_list:
        print("Found in {file_path}".format(file_path=info[0]))
        counts = info[1]
        full = full + counts[0]
        partial = partial + counts[1]

    total = full + partial
    print("-------------------------------")
    final_line = "Found {count} files for {full} fulls and {partial} partials for a total of {total}".format(
        count=len(file_list), full=full, partial=partial, total=total)
    print(final_line)

    final_dir = os.path.join(dir_for_output, "dist")
    with open(os.path.join(final_dir, "results.txt"), "w") as final_fh:
        final_fh.write(final_line)
        final_fh.write("\n")

    make_htmlfile_for_category(file_dict, EDITMODEMGR_KEY, final_dir, "editmodemgr.html")
    make_htmlfile_for_category(file_dict, EDITORS_KEY, final_dir, "editors.html")
    make_htmlfile_for_category(file_dict, HANDLERS_KEY, final_dir, "handlers.html")
    make_htmlfile_for_category(file_dict, DIALOGS_KEY, final_dir, "dialogs.html")
    make_htmlfile_for_category(file_dict, ELEMENT_KEY, final_dir, "element.html")
    make_htmlfile_for_category(file_dict, OTHERS_KEY, final_dir, "others.html")

    make_file_for_category(file_dict, EDITMODEMGR_KEY, final_dir, "editmodemgr.txt")
    make_file_for_category(file_dict, EDITORS_KEY, final_dir, "editors.txt")
    make_file_for_category(file_dict, HANDLERS_KEY, final_dir, "handlers.txt")
    make_file_for_category(file_dict, DIALOGS_KEY, final_dir, "dialogs.txt")
    make_file_for_category(file_dict, ELEMENT_KEY, final_dir, "element.txt")
    make_file_for_category(file_dict, OTHERS_KEY, final_dir, "others.txt")

    cat_list = [(EDITMODEMGR_KEY, "editmodemgr_detail.html"),
                (EDITORS_KEY, "editors_detail.html"),
                (HANDLERS_KEY, "handlers_detail.html"),
                (DIALOGS_KEY, "dialogs_detail.html"),
                (ELEMENT_KEY, "element_detail.html"),
                (OTHERS_KEY, "others_detail.html")]

    make_html_detailed_report_for_categories(final_dir, file_dict, cat_list)


def parse_file(file_path):
    src_parser = ParseSource()
    return src_parser.parse(file_path)


def parse_header(source_file_path):
    header_path = parseUtil.find_existing_header_path_with_source(source_file_path)
    if os.path.exists(header_path):
        return ParseHeader().parse(header_path)
    else:
        print("Path doesn't exist {path}".format(path=header_path))

    return dict()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("doh")
    else:
        path = sys.argv[1]
        script_path = sys.argv[0]
        script_dir = os.path.dirname(script_path)
        parse(path, script_dir)


"""
            if idxCount < 1:
                idxCount += 1

                print(the_file_path)
                header_path = os.path.basename(the_file_path)
                header_dir = os.path.split(the_file_path)[0]
                header_path = os.path.splitext(header_path)[0]
                header_path = os.path.join(header_dir, header_path) + ".h"

                print("Testing path: " + header_path)
                if os.path.exists(header_path):
                    header_dict = ParseHeader().parse(header_path)

                    for k in header_dict.keys():
                        print("Class: {classname} Base: {base}".format(
                                classname=k, base=header_dict.get(k)))
                else:
                    print("Path doesn't exist")
"""
