from parseSource import ParseSource

import re

import unittest


class TestParseLinesFindCtorCommit(unittest.TestCase):
    def testParseFindCtor(self):
        lines = ["#include <DBView.h>", "class ADocument;", "class GRep;",
                 "DBView::DBView(int a)", "{", " ", "}",
                 "void DBView::updateGReps(ADocument* pDoc)", "{",
                 "  DBG_WARN('Patate', 'Inouk', '01/02/2016'); ",
                 "  initiateSelfDestruct();  ", "Transaction trans(TR_PATATE);  ", # line 12 for trans.
                 "  for(ElementId id : m_elementPatate)", "{",
                 "  ErrorStatus err = pDoc->regenerate(PATATE);", "if(err == ERR_SUCCESS)",
                 "{", "trans.commit();", "}", "}",    # finish if, finish for. line 18 for commit.
                 "  pDoc->updateAllViews();"
                 "}"    # finish function.
                 ]
        info = {
            21: {"Function": "updateGReps", "Class": "DBView"}
        }
        parser = ParseSourceFile()
        res_dict_list = parser.parse_lines(lines, info)
        self.assertEqual(1, len(res_dict_list))
        res_dict = res_dict_list[0]
        self.assertEqual(18, res_dict["commit"])
        self.assertEqual(12, res_dict["ctor"])

    def testParseCtorDoesntEndOnSameLine(self):
        lines = ["#include <DBView.h>", "class ADocument;", "class GRep;",
                 "DBView::DBView(int a)", "{", " ", "}",
                 "void DBView::updateGReps(ADocument* pDoc)", "{",
                 "  DBG_WARN('Patate', 'Inouk', '01/02/2016'); ",
                 "  initiateSelfDestruct();  ", "Transaction trans(TR_PATATE, ",
                 "     EndUndoTransactionOptions().mayModifyEditorOrModScope());",
                 "  for(ElementId id : m_elementPatate)", "{",
                 "  ErrorStatus err = pDoc->regenerate(PATATE);", "if(err == ERR_SUCCESS)",
                 "{", "trans.commit();", "}", "}",
                 "  pDoc->updateAllViews();"
                 "}"    # finish function.
                 ]
        info = {
            21: {"Function": "updateGReps", "Class": "DBView"}
        }
        parser = ParseSourceFile()
        res_dict_list = parser.parse_lines(lines, info)
        self.assertEqual(1, len(res_dict_list))
        res_dict = res_dict_list[0]
        self.assertEqual(19, res_dict["commit"])
        self.assertEqual(12, res_dict["ctor"])


class TestProcessSourceResults(unittest.TestCase):
    # results contains 5 structs if remember correctly.
    # found_one, num_full, num_partial, full_mat, partial_mat.
    # mat tup is: line, line_num, tup = (class, meth)
    def testProcessOneList(self):
        match_list = [("pADoc->updateAllViews", 2, ("Patate", "DoSomething")),
                      ("pDoc->updateAllViews", 10, ("DBView", "UpdateGReps"))]

        parser = ParseSourceFile()
        info_dict = dict()
        parser.processSourceResult(match_list, info_dict)
        self.assertIsNotNone(info_dict.get(2))
        self.assertIsNotNone(info_dict.get(10))

        self.assertEqual("Patate", info_dict[2]["Class"])
        self.assertEqual("DoSomething", info_dict[2]["Function"])

        self.assertEqual("DBView", info_dict[10]["Class"])
        self.assertEqual("UpdateGReps", info_dict[10]["Function"])


class ParseSourceFile:
    def parse(self, file_path):
        src_parser = ParseSource()
        results = src_parser.parse(file_path)
        # results contains 5 structs if remember correctly.
        # found_one, num_full, num_partial, full_mat, partial_mat.
        # mat list is: line, line_num, tup = (class, meth)
        res_list = list()
        if results[0]:
            info_dict = dict()
            self.processSourceResult(results[3], info_dict)
            self.processSourceResult(results[4], info_dict)

            with open(file_path) as fh:
                lines = fh.readlines()
                res_list = self.parse_lines(lines, info_dict)
        else:
            print("Info is outdated, skipped file: {file}".format(file=file_path))

        return res_list

    def parse_lines(self, lines, file_info):
        """
        Returns: a list of dictionaries, 1 dict per call.
        Dictionary has 2 entries: commit: line number of commit found. ctor: line of Transaction constructor.
        Parses all the lines of a file looking for the functions in which we previously found updateAllViews.
        :param lines: All the lines of a file.
        :param file_info: dictionary with keys=line numbers and values = dict of Function name and Class Name.
        :return: a list of dictionaries.
        """
        patt_open_brace = re.compile("{")
        patt_close_brace = re.compile("}")
        res_list = list()
        keys = file_info.keys()
        for key in keys:
            the_line_number = key
            info = file_info[key]
            func_def_name = info["Class"] + "::" + info["Function"]
            func_regex = r"\w+\s+{func}".format(func=func_def_name)
            ctor_regex = r"{ctor}".format(ctor=func_def_name)
            patt_func = re.compile(func_regex)
            patt_ctor = re.compile(ctor_regex)

            patt_trans = re.compile("\s*Transaction\s+\w*\(.*")
            patt_commit = re.compile("commit.*\(.*\);")
            line_num = 0

            isFuncFound = False
            isInFunction = False
            braces_num = 0
            res_dict = dict()
            for line in lines:
                result_func = patt_func.search(line)
                result_ctor = patt_ctor.search(line)

                line_num += 1
                if result_func or result_ctor:
                    braces_num = 0
                    isFuncFound = True

                if isFuncFound:
                    result_open = patt_open_brace.search(line)
                    result_close = patt_close_brace.search(line)
                    if result_open:
                        braces_num += 1

                    if result_close:
                        braces_num -= 1

                    if isFuncFound and braces_num > 0:
                        isInFunction = True

                    result_trans = patt_trans.search(line)
                    result_commit = patt_commit.search(line)

                    if result_trans:
                        res_dict["ctor"] = line_num
                    if result_commit:
                        res_dict["commit"] = line_num

                if isInFunction and braces_num <= 0:
                    break   # skip lines.

            res_dict["line"] = the_line_number
            res_list.append(res_dict)

        return res_list

    def processSourceResult(self, match_list, info_dict):
        for match in match_list:
            line_num = match[1]
            code_info = match[2]
            class_name = code_info[0]
            meth_name = code_info[1]
            info_dict[line_num] = {"Class": class_name, "Function": meth_name}

if __name__ == "__main__":
    unittest.main()
