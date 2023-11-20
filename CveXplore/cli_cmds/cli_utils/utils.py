import json
from collections import defaultdict

import click
import pandas as pd
from dicttoxml import dicttoxml


def format_output(format_type, input_list):
    """
    Method to format the input_list based on a given format_type (json|csv|html|xml)

    :param format_type: Format type
    :type format_type: str
    :param input_list: List with dicts that needs formatting
    :type input_list: list
    :return: Formatted output
    :rtype: based on given format_type
    """

    if format_type == "json":
        output = json.dumps(input_list, indent=4, sort_keys=True, default=str)
    elif format_type == "csv":
        df = pd.DataFrame(input_list)
        output = df.to_csv(index=False)
    elif format_type == "html":
        df = pd.DataFrame(input_list)
        output = df.to_html(index=False)
    elif format_type == "xml":
        if isinstance(input_list, list):
            count = 1
            temp_dict = defaultdict(dict)
            for each in input_list:
                temp_dict[f"entry_{count}"] = each
                count += 1
            output = dicttoxml(temp_dict, custom_root="CveXplore")
        elif isinstance(input_list, dict):
            output = dicttoxml(input_list, custom_root="CveXplore")

    return output


def printer(input_data, output="json"):
    if isinstance(input_data, list):
        click.echo(format_output(output, input_data))
    elif isinstance(input_data, dict):
        click.echo(input_data)
