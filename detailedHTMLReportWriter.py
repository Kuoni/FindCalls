import os
import re

import unittest


class WriteWithSingleResult(unittest.TestCase):
    def testWithSingleResult(self):
        pass
        """writer = DetailedHTMLReportWriter()
        writer.write()"""

    def testCommentBlocks(self):
        patt_start = re.compile(".*?/\*.*")
        patt_end = re.compile(".*?\*/.*")
        line_start = "  toto crap crap   /*"
        line_end = " lol ok its fine method delcl */    "

        result_start = patt_start.search(line_start)
        self.assertIsNotNone(result_start)

        result_end = patt_end.search(line_end)
        self.assertIsNotNone(result_end)


class DetailedHTMLReportWriter:
    def __init__(self, fh):
        self.file_handle = fh

    def write(self, file_dict, catstr):
        self.create_html_head()
        self.create_html_body()
        self.file_handle.write("<table>\n")
        self.create_table_header()
        for file_info in file_dict[catstr]:
            the_file_path = file_info[0] #result[1] = full count, result[2] is partial count.
            full_list = file_info[3]
            partial_list = file_info[4]
            header_dict = file_info[5]

            self.write_list_results(the_file_path, "Full", full_list, header_dict)
            self.write_list_results(the_file_path, "Partial", partial_list, header_dict)

        self.file_handle.write("</table>\n")
        self.file_handle.write("<br/>\n<br/>\n")
        self.file_handle.write("<p>Function calls</p>\n")
        self.file_handle.write("<table>\n")
        self.create_table_header_for_line_results()
        for file_info in file_dict[catstr]:
            the_file_path = file_info[0] #result[1] = full count, result[2] is partial count.
            full_list = file_info[3]
            partial_list = file_info[4]

            self.write_list_line_results(the_file_path, "Full", full_list)
            self.write_list_line_results(the_file_path, "Partial", partial_list)

        self.file_handle.write("</table>\n")
        self.end_html_body()
        self.end_html()

    def create_html_head(self):
        self.file_handle.write("<html>\n")
        self.file_handle.write("<head>\n")
        self.file_handle.write("<link rel='stylesheet' type='text/css' href='style.css'>\n")
        self.file_handle.write("</head>\n")

    def end_html(self):
        self.file_handle.write("</html>\n")

    def create_html_body(self):
        self.file_handle.write("<body>\n")

    def end_html_body(self):
        self.file_handle.write("</body>\n")

    def create_table_header(self):
        self.start_table_row()
        self.file_handle.write("<th>Type</th>\n")
        self.file_handle.write("<th>File</th>\n")
        self.file_handle.write("<th>Line#</th>\n")
        self.file_handle.write("<th>Class</th>\n")
        self.file_handle.write("<th>Function</th>\n")
        self.file_handle.write("<th>Base Classes</th>\n")
        self.end_table_row()

    def create_table_header_for_line_results(self):
        self.start_table_row()
        self.file_handle.write("<th>Type</th>\n")
        self.file_handle.write("<th>File</th>\n")
        self.file_handle.write("<th>Line#</th>\n")
        self.end_table_row()

    def start_table_row(self):
        self.file_handle.write("<tr>\n")

    def end_table_row(self):
        self.file_handle.write("</tr>\n")

    def write_list_results(self, file_path, result_type_name, results, header_dict):
        for result in results: # a result contains: line, line_num, class, func.
            line = result[0]
            line_number = result[1]
            code_info = result[2]
            class_name = code_info[0]
            func_name = code_info[1]

            try:
                bases = header_dict[class_name]
            except KeyError:
                bases = list()

            base_classes = ",".join(bases)

            self.start_table_row()
            self.write_line(result_type_name, file_path, line_number, class_name, func_name, base_classes)
            self.file_handle.write("\n")
            self.end_table_row()

    def write_line(self, type_name, file_path, line_number, class_name, func_name, base_classes):
        self.file_handle.write( (
            "<td>{type}</td>\n" +
            "<td>{file_path}</td>\n" +
            "<td style='text-align:center'>{line_num}</td>\n" +
            "<td style='text-align:center'>{class_name}</td>\n" +
            "<td style='text-align:center'>{func_name}</td>\n" +
            "<td style='text-align:center'>{base_classes}</td>\n").format(
                type=type_name, file_path=file_path, line_num=line_number,
                class_name=class_name, func_name=func_name,
                base_classes=base_classes))

    def write_list_line_results(self, file_path, result_type_name, results):
        for result in results: # a result contains: line, line_num, class, func.
            line = result[0]
            line_number = result[1]

            self.start_table_row()
            self.write_line_line(result_type_name, file_path, line_number, line)
            self.file_handle.write("\n")
            self.end_table_row()

    def write_line_line(self, type_name, file_path, line_number, line):
        self.file_handle.write((
            "<td>{type}</td>\n" +
            "<td>{file_path}</td>\n" +
            "<td style='text-align:center'>{line_num}</td>\n" +
            "<td>{line}</td>\n").format(
                type=type_name, file_path=file_path, line_num=line_number,
                line=line))

if __name__ == "__main__":
    unittest.main()
"""('E:\\Git\\ADSK\\t_babii_main_WC1\\Dev\\Source\\Revit\\RevitUI\\Commands\\ACommandRouter.cpp', 0, 1,
 [], [('         executionContext.getADocument()->updateAllViews();\n', 164, ('ACommandRouter', 'onC
ommand'))])"""