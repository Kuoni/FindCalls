import re

import unittest

"""
Module: Parses a C++ header file and returns information about classes and their base classes.
"""


class ParseTestRegex(unittest.TestCase):
    def test_with_header_with_base(self):
        test_dict = ParseHeader().parse("F:\Project\Python\FindCalls\ConduitSurfaceConnectorEditModeMgr.h")
        keys = ("SurfaceConnectorEditModeMgr", "GrepKeeperElemForSurfConn",
                "TempDimDataCacheSurfConn", "CurveElemForSurfConn")
        bases = ("EditModeMgr", "TempGrepKeeper", "TempDimDataCacheInterface", "CurveElem")

        self.assertEqual(len(test_dict.keys()), len(keys))
        #self.assertEqual(len(test_dict.values()), len(bases))

        for key in test_dict.keys():
            self.assertTrue(key in keys, "{key} is not in dict".format(key=key))
            base_list = test_dict[key]
            for base in base_list:
                self.assertTrue(base in bases,
                                "{base} is not in dict for key {key}".format(
                                    base=base, key=key))


class ParseWithFakeLines(unittest.TestCase):
    def test_one_base_one_class(self):
        lines = ["#include <toto.h>", "#include <GRep.h>", "#include <DBView.h>",
                 "class ADocument;", "class DBView;",
                 "class CRSAPI DBView : public Element ",
                 "{", " DBView();", "virtual ~DBView()", "};"
                 ]
        parser = ParseHeader()
        header_dict = parser.parse_lines(lines)

        self.assertTrue("DBView" in header_dict)
        self.assertTrue("Element" in header_dict["DBView"])

    def test_class_no_base(self):
        lines = ["#include <toto.h>", "#include <GRep.h>", "#include <DBView.h>",
                 "class ADocument;", "class DBView;",
                 "class CRSAPI DBView   ",
                 "{", " DBView();", "virtual ~DBView()", "};"
                 ]
        parser = ParseHeader()
        header_dict = parser.parse_lines(lines)

        self.assertTrue("DBView" in header_dict)
        self.assertEqual(0, len(header_dict["DBView"]))

    def test_class_one_base_no_class_specifier(self):
        lines = ["#include <toto.h>", "#include <GRep.h>", "#include <DBView.h>",
                 "class ADocument;", "class DBView;",
                 "class DBView : public Element  ",
                 "{", " DBView();", "virtual ~DBView()", "};"
                 ]
        parser = ParseHeader()
        header_dict = parser.parse_lines(lines)

        self.assertTrue("DBView" in header_dict)
        self.assertEqual(1, len(header_dict["DBView"]))
        self.assertTrue("Element" in header_dict["DBView"])

    def test_class_no_base_no_class_specifier(self):
        lines = ["#include <toto.h>", "#include <GRep.h>", "#include <DBView.h>",
                 "class ADocument;", "class DBView;",
                 "class DBView  ",
                 "{", " DBView();", "virtual ~DBView()", "};"
                 ]
        parser = ParseHeader()
        header_dict = parser.parse_lines(lines)

        self.assertTrue("DBView" in header_dict)
        self.assertEqual(0, len(header_dict["DBView"]))

    def test_multiple_bases(self):
        lines = ["#include <Document.h>", "#include <GRep.h>", "#include <DBView.h>",
                 "class DirtyRect;", "class DBView;",
                 "class DESKTOPMFCAPI DesktopMFCView : public MFCView,  public ADialogCore ",
                 "{", " DesktopMFCView();", "virtual ~DesktopMFCView()",
                 "protected:   ", "void doPartialUpdate();",
                 "};"
                 ]
        parser = ParseHeader()
        header_dict = parser.parse_lines(lines)

        self.assertTrue("DesktopMFCView" in header_dict)
        base_classes = header_dict["DesktopMFCView"]
        self.assertEqual(2, len(base_classes))
        self.assertTrue("MFCView" in base_classes)
        self.assertTrue("ADialogCore" in base_classes)

    def test_one_base_no_inheritance_specifier(self):
        lines = ["#include <toto.h>", "#include <GRep.h>", "#include <DBView.h>",
                 "class ADocument;", "class DBView;",
                 "class CRSAPI DBView : Element ",
                 "{", " DBView();", "virtual ~DBView()", "};"
                 ]
        parser = ParseHeader()
        header_dict = parser.parse_lines(lines)

        self.assertTrue("DBView" in header_dict)
        self.assertTrue("Element" in header_dict["DBView"])


class ParseHeader:
    """
    class ParserHeader: parses a c++ header file and returns information about it.
    """
    def __init__(self):
        # CLASS WITH SPECIFIER REGEX example: class CRSAPI Building
        self.patt_class = re.compile("class\s+\w*\s+(\w+)\s*")
        # CLASS NO SPECIFIER REGEX example: class Building but also matches "class Building;"
        self.patt_class_no_specifier = re.compile("class\s+(\w+)\s*:?")# fwd decl are ignored later.
        # BASE_CLASS REGEX example: class CRSAPI Building : public Elem
        # Accepts no class specifier (aka no CRSAPI)
        # Accepts multiple base classes.
        self.patt_base_classes = re.compile("class\s+\w*\s*\w+\s*:(.*)")
        self.patt_base_class = re.compile(r"\s*(?:\w+)?\s+(\w+),?")
        self.header_dict = dict()

    def parse(self, file_path):
        """
        Opens up a file which should be a header file and parses the lines.
        :param file_path: full file path to a header file.
        :return: See the result of parse_lines
        """
        with open(file_path) as fh:
            lines = list()
            try:
                lines = fh.readlines()
            except:
                lines = list()
                print("Error in header parsing")

            return self.parse_lines(lines)

    def parse_lines(self, lines):
        """
        Parses all the lines of a file and searches for class information.
        :param lines: All the lines of a file
        :return: A dictionary: each key is a class name found in the header file. The value for that
        key is a list of base class names.
        """
        for line in lines:
            line = line.strip("\n")
            if line.startswith("//"):
                continue

            result_class = self.patt_class.search(line)
            result_class_no_spec = self.patt_class_no_specifier.match(line)
            result_bases = self.patt_base_classes.search(line)

            foundClassName = False
            class_name = None
            if not line.endswith(";") and (result_class or result_class_no_spec):
                foundClassName = True
                if result_class:
                    class_name = result_class.groups()[0]
                elif result_class_no_spec:
                    class_name = result_class_no_spec.groups()[0]

            if foundClassName and result_bases:
                base_matches = result_bases.groups()[0]
                result_base = self.patt_base_class.findall(base_matches)

                base_list = list()
                for base in result_base:
                    base_list.append(base)

                self.header_dict[class_name] = base_list
            elif foundClassName:
                self.header_dict[class_name] = list()

        return self.header_dict


if __name__ == "__main__":
    unittest.main()
