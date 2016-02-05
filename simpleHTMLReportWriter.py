import os
import re


class DetailedHTMLReportWriter:
    def __init__(self, fh):
        self.file_handle = fh

    def write(self, file_dict, catstr):
        self.create_html_head()
        self.create_html_body()
        self.file_handle.write("<table>\n")
        self.create_table_header()
        for file_info in file_dict[catstr]:
            the_file_path = file_info[0]
            counts = file_info[1:]

            self.file_handle.write("<tr>\n")
            self.file_handle.write("<td>{file_path}</td>\n<td style='text-align:center'>{full}</td>\n<td style='text-align:center'>{partial}</td>".format(
                file_path=the_file_path, full=counts[0], partial=counts[1]))
            self.file_handle.write("\n")
            self.file_handle.write("</tr>\n")

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
        self.file_handle.write("<th>File</th>\n")
        self.file_handle.write("<th>Full</th>\n")
        self.file_handle.write("<th>Partial</th>\n")
        self.end_table_row()

    def start_table_row(self):
        self.file_handle.write("<tr>\n")

    def end_table_row(self):
        self.file_handle.write("</tr>\n")

