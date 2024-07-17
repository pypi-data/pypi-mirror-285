import os
import xml.etree.ElementTree as et

import click

from xml_report.link_prediction_example import json_data


def process_xml_files(input_folder, json_filter, output_file):
    click.secho("Starting the parsing of the xml files...", fg='yellow')
    xml_files = [f for f in os.listdir(input_folder) if f.endswith(".xml")]

    if not xml_files:
        raise ValueError("No XML files found in the input folder")

    # Use the root element of the first XML input file
    first_file_path = os.path.join(input_folder, xml_files[0])
    tree = et.parse(first_file_path)
    test_suites_root = tree.getroot()

    # Remove all children to avoid duplicated at the root element
    for ts in test_suites_root.findall("testsuite"):
        test_suites_root.remove(ts)

    for xml_file in xml_files:
        click.secho(f"Parsing file: {xml_file}", fg='yellow')
        file_path = os.path.join(input_folder, xml_file)
        tree = et.parse(file_path)
        test_suite_root_element = tree.getroot()

        # Filter the test case elements based on classname and name
        for testsuite in test_suite_root_element:
            for testcase in testsuite:
                classname = testcase.get("classname")
                name = testcase.get("name")

                if classname and name:
                    if not find_link(json_filter, classname, name):
                        testcase.set("MISMATCH", "True")

            for child in list(testsuite):
                if child.get("MISMATCH") == "True":
                    testsuite.remove(child)

            if len(testsuite):
                test_suites_root.append(testsuite)

    # Write the new XML to the output file
    tree = et.ElementTree(test_suites_root)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)


def find_link(json_filter, title, title_label):
    for item in json_filter.get("items", []):
        target_artifact = item.get("target", {}).get("artifact", {})
        if (
            target_artifact.get("api") == "testrail"
            and target_artifact.get("title") == title
            and target_artifact.get("title_label")
            == title_label.lower().replace(" ", "_")
        ):
            return target_artifact.get("link")
        source_artifact = item.get("source", {}).get("artifact", {})
        if (
            source_artifact.get("api") == "testrail"
            and source_artifact.get("title") == title
            and source_artifact.get("title_label")
            == title_label.lower().replace(" ", "_")
        ):
            return source_artifact.get("link")
    return False
