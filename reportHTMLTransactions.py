from htmlReportWriters import BaseHTMLReportWriter


# Should have a base to share between the writers.
class ReportHTMLWriterTransactions(BaseHTMLReportWriter):
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

