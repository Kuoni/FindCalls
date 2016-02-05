

# Should have a base to share between the writers.
class ReportHTMLWriterTransactions:

    def __init__(self, fh):
        self.file_handle = fh

    def write(self, list_of_list_of_dicts):
        """
        writes the report.
        :param list_of_list_of_dicts: each file generates a list of dicts. Dicts have only 2 keys.
        Thus all files are combined into a list of lists.
        :return: void
        """
        self.create_html_head()
        self.create_html_body()

        self.create_html_table()
        hdr_list = ["File", "Result line", "Ctor line", "Commit line"]
        self.create_table_header(hdr_list)
        total_result = 0
        trans_result = 0
        for list_of_dicts_tup in list_of_list_of_dicts:
            file_path = list_of_dicts_tup[0]
            list_of_dicts = list_of_dicts_tup[1]
            for info_dict in list_of_dicts:
                total_result += 1
                line = info_dict["line"]
                ctor_str = info_dict.get("ctor", "none")
                if info_dict.get("ctor") is not None:
                    trans_result += 1
                commit_str = info_dict.get("commit", "none")
                self.write_results(file_path, info_dict, line, ctor_str, commit_str)
        self.end_html_table()
        self.file_handle.write("<p>{trans} Transactions out of {total} results. Percent: {percent}</p>\n".format(
            trans=trans_result, total=total_result,
            percent=round((trans_result/total_result)*100, 2)
        ))
        self.end_html_body()
        self.end_html()

    def write_results(self, file_path, info_dict, line, ctor, commit):
        self.start_table_row()
        self.add_table_column(file_path)
        self.add_table_column(line)
        self.add_table_column(ctor)
        self.add_table_column(commit)
        self.end_table_row()

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

    def create_html_table(self):
        self.file_handle.write("<table>\n")

    def end_html_table(self):
        self.file_handle.write("</table>\n")

    def create_table_header(self, hdr_list):
        self.start_table_row()
        for hdr in hdr_list:
            self.add_table_header(hdr)
        self.end_table_row()

    def start_table_row(self):
        self.file_handle.write("<tr>\n")

    def end_table_row(self):
        self.file_handle.write("</tr>\n")

    def add_table_header(self, header_str):
        self.file_handle.write("<th>\n\t{header}\n</th>\n".format(header=header_str))

    def add_table_column(self, data_str):
        self.file_handle.write("<td>\n\t{data}\n</td>\n".format(data=data_str))
