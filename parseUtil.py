import os.path
import shutil
import unittest

from pathlib import Path


class ParseUtilTest(unittest.TestCase):
    def setUp(self):
        base_test_dir = os.path.join(os.getcwd(), "unittest") # be careful if modifying this line, check teardown rmtree.
        base_p = Path(base_test_dir)
        base_p.mkdir()
        src_test_dir = os.path.join(base_test_dir, "Source")
        src_p = Path(src_test_dir)
        src_p.mkdir()
        revit_test_dir = os.path.join(src_test_dir, "Revit")
        revit_p = Path(revit_test_dir)
        revit_p.mkdir()
        revitdb_test_dir = os.path.join(revit_test_dir, "RevitDB")
        revitdb_p = Path(revitdb_test_dir)
        revitdb_p.mkdir()

        self.base_path = base_test_dir
        self.local_path = revitdb_test_dir

    def tearDown(self):
        shutil.rmtree(self.base_path)

    def test_one_up_header_path(self):
        local_p = Path(self.local_path)
        parts_tup = local_p.parts
        parts = list(parts_tup)
        parts.pop()# get rid of last elem.
        parts.append("inc")

        one_up_inc_path = os.path.join(*parts)
        one_up_inc_p = Path(one_up_inc_path)
        one_up_inc_p.mkdir()

        source_path = os.path.join(self.local_path, "DBView.cpp")
        header_path = os.path.join(str(one_up_inc_p), "DBView.h")

        with open(source_path, "w") as fh:
            fh.write("test source")

        with open(header_path, "w") as fh:
            fh.write("test header")

        result_path = find_existing_header_path_with_source(source_path)
        self.assertIsNotNone(result_path)
        self.assertEqual(result_path, header_path)

    def test_local_inc_header_path(self):
        source_path = os.path.join(self.local_path, "DBView.cpp")
        local_inc_path = os.path.join(self.local_path, "inc")
        local_inc_p = Path(local_inc_path)
        local_inc_p.mkdir()

        header_path = os.path.join(local_inc_path, "DBView.h")

        with open(source_path, "w") as fh:
            fh.write("test source")

        with open(header_path, "w") as fh:
            fh.write("test header")

        result_path = find_existing_header_path_with_source(source_path)
        self.assertIsNotNone(result_path)
        self.assertEqual(result_path, header_path)

    def test_same_dir_header_path(self):
        source_path = os.path.join(self.local_path, "DBView.cpp")
        header_path = os.path.join(self.local_path, "DBView.h")

        with open(source_path, "w") as fh:
            fh.write("test source")

        with open(header_path, "w") as fh:
            fh.write("test header")

        result_path = find_existing_header_path_with_source(source_path)
        self.assertIsNotNone(result_path)
        self.assertEqual(result_path, header_path)


def find_existing_header_path_with_source(src_file_path):
    header_path = os.path.basename(src_file_path)
    header_filename = os.path.splitext(header_path)[0] + ".h"
    header_dir = os.path.split(src_file_path)[0]

    header_path = os.path.join(header_dir, header_filename)
    if os.path.exists(header_path):
        return header_path
    else:
        header_local_inc_dir = os.path.join(header_dir, "inc")
        local_inc_header_path = os.path.join(header_local_inc_dir, header_filename)
        if os.path.exists(local_inc_header_path):
            return local_inc_header_path
        else:
            local_p = Path(header_dir)
            parts_tup = local_p.parts
            parts = list(parts_tup)
            parts.pop()
            parts.append("inc")

            header_one_up_inc_dir = os.path.join(*parts)
            header_one_up_inc_path = os.path.join(header_one_up_inc_dir, header_filename)
            if header_one_up_inc_path:
                return header_one_up_inc_path
            else:
                return None

if __name__ == "__main__":
    unittest.main()