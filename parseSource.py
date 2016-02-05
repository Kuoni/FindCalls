import os.path
import re
import tempfile

import unittest

class TestParser(unittest.TestCase):

    def testPartialUpdateAllViews(self):
        lines = ["#include <toto.h>", "#include <GRep.h>", "#include <DBView.h>", "Patate::Patate()",
                 "{", " ", "}",
                 "Patate::~Patate()", "{", " ", "}",
                 "void Patate::funcBlah(ADocument* pDoc)", "{", "     pDoc->updateAllViews();", "}"]

        parser = ParseSource()
        result = parser.parse_lines(lines)
        self.assertTrue(result[0])
        self.assertEqual(0, result[1])
        self.assertEqual(1, result[2])

    def testPartialUpdateAllViewsWithFirstParamOnly(self):
        lines = ["#include <toto.h>", "#include <GRep.h>", "#include <DBView.h>", "Patate::Patate()",
                 "{", " ", "}",
                 "Patate::~Patate()", "{", " ", "}",
                 "void Patate::funcBlah(ADocument* pDoc)", "{", "     pDoc->updateAllViews( 0 );", "}"]

        parser = ParseSource()
        result = parser.parse_lines(lines)
        self.assertTrue(result[0])
        self.assertEqual(0, result[1])
        self.assertEqual(1, result[2])

    def testFullUpdateAllViews(self):
        lines = ["#include <toto.h>", "#include <GRep.h>", "#include <DBView.h>", "Patate::Patate()",
                 "{", " ", "}",
                 "Patate::~Patate()", "{", " ", "}",
                 "void Patate::funcBlah(ADocument* pDoc)", "{", "     pDoc->updateAllViews( 0, UV_FULL_REDRAW );", "}"]

        parser = ParseSource()
        result = parser.parse_lines(lines)
        self.assertTrue(result[0])
        self.assertEqual(1, result[1])
        self.assertEqual(0, result[2])

    def testFullUpdateAllViewsOneLineComment(self):
        lines = ["#include <toto.h>", "#include <GRep.h>", "#include <DBView.h>", "Patate::Patate()",
                 "{", " ", "}",
                 "Patate::~Patate()", "{", " ", "}",
                 "void Patate::funcBlah(ADocument* pDoc)", "{", "   //     pDoc->updateAllViews( 0, UV_FULL_REDRAW );",
                 " //        pDoc->updateAllViews( 0, UV_FULL_REDRAW );",
                 "}"]

        parser = ParseSource()
        result = parser.parse_lines(lines)
        self.assertFalse(result[0])
        self.assertEqual(0, result[1])
        self.assertEqual(0, result[2])

    def testUpdateAllViewsClassAndFunc(self):
        lines = ["#include <toto.h>", "#include <GRep.h>", "#include <DBView.h>", "Patate::Patate()",
                 "{", " ", "}",
                 "Patate::~Patate()", "{", " ", "}",
                 "void Patate::funcBlah(ADocument* pDoc)", "{", "     pDoc->updateAllViews( 0, UV_FULL_REDRAW );", "}"]

        parser = ParseSource()
        result = parser.parse_lines(lines)
        self.assertTrue(result[0])
        self.assertEqual(1, result[1])
        self.assertEqual(0, result[2])

        full_list = result[3]
        partial_list = result[4]
        self.assertEqual(len(full_list), 1)
        info = full_list[0]
        self.assertIsNotNone(info)
        code_info = info[2]
        self.assertEqual("Patate", code_info[0])
        self.assertEqual("funcBlah", code_info[1])

    def testUpdateAllViewsClassAndDtor(self):
        lines = ["#include <toto.h>", "#include <GRep.h>", "#include <DBView.h>", "Patate::Patate()",
                 "{", "   ", "}",
                 "Patate::~Patate()", "{", "   m_pADoc->updateAllViews( 0, UV_FULL_REDRAW );", "}",
                 "void Patate::funcBlah(ADocument* pDoc)", "{", "     pDoc->getGraphicsMgr().resetAllDirtyRects()", "}"]

        parser = ParseSource()
        result = parser.parse_lines(lines)
        self.assertTrue(result[0])
        self.assertEqual(1, result[1])
        self.assertEqual(0, result[2])

        full_list = result[3]
        partial_list = result[4]
        self.assertEqual(len(full_list), 1)
        info = full_list[0]
        self.assertIsNotNone(info)
        code_info = info[2]
        self.assertEqual("Patate", code_info[0])
        self.assertEqual("~Patate", code_info[1])

    def testUpdateAllViewsDontMatchFunctionCalls(self):
        # for v3.1.1 version. Doesn't match ASuper::DoFuncBlah.
        lines = ["#include <toto.h>", "#include <GRep.h>", "#include <DBView.h>", "Patate::Patate()",
                 "{", " ", "}",
                 "Patate::~Patate()", "{", " ", "}",
                 "void Patate::funcBlah(ADocument* pDoc)", "{",
                 "     ASuper::DoFuncBlah(  pDoc ); ",
                 "     pDoc->updateAllViews( 0, UV_FULL_REDRAW );", "}"]

        parser = ParseSource()
        result = parser.parse_lines(lines)
        self.assertTrue(result[0])
        self.assertEqual(1, result[1])
        self.assertEqual(0, result[2])

        full_list = result[3]
        self.assertEqual(len(full_list), 1)
        info = full_list[0]
        self.assertIsNotNone(info)
        code_info = info[2]
        self.assertEqual("Patate", code_info[0])
        self.assertEqual("funcBlah", code_info[1])

    def testUpdateAllViewsFullClearCache(self):
        lines = ["#include <Document.h>", "#include <GRep.h>", "#include <DBView.h>", "Patate::Patate()",
                 "{", " ", "}",
                 "Patate::~Patate()", "{", " ", "}",
                 "void Patate::funcBlah(ADocument* pDoc)", "{",
                 "     pDoc->updateAllViews( 0, UV_CLEAR_GRAPHIC_CACHE_AND_FULL_REDRAW );", "}"]

        parser = ParseSource()
        result = parser.parse_lines(lines)
        self.assertTrue(result[0])
        self.assertEqual(1, result[1])
        self.assertEqual(0, result[2])

        full_list = result[3]
        partial_list = result[4]
        self.assertEqual(len(full_list), 1)
        self.assertEqual(len(partial_list), 0)
        info = full_list[0]
        self.assertIsNotNone(info)
        code_info = info[2]
        self.assertEqual("Patate", code_info[0])
        self.assertEqual("funcBlah", code_info[1])


class ParseSource:
    def __init__(self):
        self.patt_full = re.compile("updateAllViews.+(?:UV)|(?:AND)_FULL_REDRAW")
        self.patt_partial = re.compile("updateAllViews\(.*?\)")
        self.patt_func_line = re.compile("\w+\s+(\w+)::(\w+)\(.*?\)\s*?$") # matches func decl, no semi-colon so doesn't match func calls
        self.patt_ctor_dtor_line = re.compile("\s*?(\w+)::(~?\w+)\(.*?\)\s*?$") # matches func decl, no semi-colon so doesn't match func calls
        self.patt_cmtblk_start = re.compile(".*?/\*.*")  # match anything ungreedily and match comment block start
        self.patt_cmtblk_end = re.compile(".*?\*/.*") # match anything ungreedily and match comment block end

    def parse(self, file_path):
        with open(file_path) as fh:
            return self.parse_file_handle(fh)

    def parse_file_handle(self, fh):
        try:
            lines = fh.readlines()
        except UnicodeDecodeError as ex:
            lines = list()
            print(ex.reason)

        return self.parse_lines(lines)

    def parse_lines(self, lines):
        full_matches = list()
        partial_matches = list()
        found_one = False
        full = 0
        partial = 0

        function_name = ""
        class_name = ""
        line_number = 1
        isInCommentBlock = False
        isCommentBlockJustStarted = False
        for line in lines:
            current_line_number = line_number
            line_number += 1

            result_patt_start = self.patt_cmtblk_start.search(line)
            result_patt_end = self.patt_cmtblk_end.search(line)
            if result_patt_start:
                isInCommentBlock = True
                isCommentBlockJustStarted = True
            if result_patt_end:
                isInCommentBlock = False

            is_comment_line = str.strip(line).startswith("//")
            if not is_comment_line and not (not isCommentBlockJustStarted and isInCommentBlock):
                isCommentBlockJustStarted = False
                result_func_line = self.patt_func_line.search(line)
                result_ctor_dtor_line = self.patt_ctor_dtor_line.search(line)
                if result_func_line or result_ctor_dtor_line:
                    if result_func_line:
                        class_name, function_name = self.get_first_two_groups_in_group(result_func_line.groups())
                    elif result_ctor_dtor_line:
                        class_name, function_name = self.get_first_two_groups_in_group(result_ctor_dtor_line.groups())
                    continue

                full_patt_match = self.patt_full.search(line)
                partial_patt_match = self.patt_partial.search(line)
                if full_patt_match or partial_patt_match:
                    found_one = True
                    line_tup = (line, current_line_number, (class_name, function_name))
                    if full_patt_match:
                        full_matches.append(line_tup)
                    elif partial_patt_match:
                        partial_matches.append(line_tup)

        if found_one:
            full = len(full_matches)
            partial = len(partial_matches)
            print("Found {full_count} FULL REDRAW and {partial_count} partial for a total of {total_count}".format(
                full_count=full, partial_count=partial, total_count=full+partial))

        return found_one, full, partial, full_matches, partial_matches

    def get_first_two_groups_in_group(self, aGroup):
        return aGroup[0], aGroup[1]

if __name__ == "__main__":
    unittest.main()
