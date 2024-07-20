import copy
import json
from typing import TextIO, Dict, Union, Any, List
import os
from queue import Queue

from test2va.generator.core.GUI import GUIEvent, GUIMethod, GUIElement, GUIControl
from test2va.generator.core.Mutant import MutantInfoPerEvent
from test2va.generator.exceptions.MethodGeneratorException import MethodGeneratorException
from test2va.generator.core.Method import Statement, Header

TAB_CONSTANT = "    "
END_OF_STATEMENT_CONSTANT = ";\n"


def get_output_file_path(input_file_path):
    """
    if input_file_path is task_method_generator/input/package.name_CreateLabel.java_parsed.json
    Then the output_file_path is task_method_generator/output/package.name/CreateLabel.txt
    And the directory path is task_method_generator/output/package.name/

    :param input_file_path: path of java_res.json
    :return:
    """
    # Replace 'java_parsed.json' with '.txt'
    #output_file_path = input_file_path.replace('.java_res.json', '.txt')
    # Replace 'input' with 'output'
    #output_file_path = output_file_path.replace('input', 'output')

    #index = output_file_path.rfind('_')

    normalized_path = os.path.normpath(input_file_path)
    dir_path = os.path.dirname(normalized_path)

    #output_directory = output_file_path[:index] + '/'
    output_directory = dir_path + "/generated_methods/"
    #output_full_path = output_file_path[:index] + '/' + output_file_path[index + 1:]
    output_full_path = output_directory + "generated_method.txt"

    return output_directory, output_full_path


def write_body_java(statement_queue: Queue, method_file: TextIO, language: str = 'java'):
    """
    This method will write the whole body of the java method.
    The method style we follow is:
        method_name() {
            statement 1;
            statement 2;
            . . .
        }
    :param statement_queue: the queue that stores all the Statement obj
    :param method_file: the output io
    :param language: default java
    :return: void
    """
    method_file.write(" {\n")  # beginning bracket
    # Dequeue every statement in the statement_queue
    while not statement_queue.empty():
        statement: Statement = statement_queue.get()
        method_file.write(statement.to_code(language))
    method_file.write("}")  # end bracket


def write_header_java(header: Header, method_file: TextIO, language: str = 'java'):
    """
    This method will write the header of the method in java
    For example, "public void method_name (parameter list ...)"
    :param header:
    :param method_file:
    :return:
    """
    method_file.write(header.to_code(language))


def add_mutant_event_statements(statement_queue: Queue, original_event: GUIEvent,
                                event_mutant_info: MutantInfoPerEvent) -> Queue:
    """
    This method adds mutable event and its replaceable mutants to statement queue
    For click event, will add the events (parameterized original mutable events and the replaceable events)
    For input event, will only add the replaceable event, an original event with parameterized input value.

    :param event_mutant_info: all mutant information of the original event
    :param statement_queue: the statement queue the original event will generate
    :param original_event: original mutable event
    :return:
    """

    if event_mutant_info.is_input_event():
        replaceable_event_statement: Statement = (
            Statement(original_event, True, event_mutant_info.get_input_mutant_parameter()))
        statement_queue.put(replaceable_event_statement)
    elif event_mutant_info.is_click_event():
        index = 0
        for replaceable_event in event_mutant_info.get_mutant_replaceable_events():
            replaceable_event_statement: Statement = (
                Statement(replaceable_event, True, event_mutant_info.get_click_mutant_parameter_by_index(index)))
            statement_queue.put(replaceable_event_statement)
            index += 1
    else:
        raise MethodGeneratorException("original event is not click nor input event")

    return statement_queue


def generate_statement_queue(method: GUIMethod, mutant_result_file_path=None) -> Queue:
    """
    Generate a queue of statements for mutable and non-mutable events, and the replaceable mutant
    events for mutable events.
    :param method:
    :param mutant_result_file_path:
    :return:
    """

    statement_queue = Queue()

    event_index = 0
    for event in method.get_events():

        event_mutant_info = MutantInfoPerEvent(mutant_result_file_path, event,
                                               event_index)
        # mutable flag
        mutable_flag = event_mutant_info.is_mutable_event()
        # event is non-mutable event
        if not mutable_flag:
            statement_queue.put(Statement(event))
        # event is mutable event
        else:
            # add mutable event and its replaceable mutants to statement queue
            statement_queue = add_mutant_event_statements(statement_queue, event, event_mutant_info)

        event_index += 1

    return statement_queue


def generate_statement(method: GUIMethod, mutant_result_file_path=None) -> (Queue, list):
    """
    Generate a queue of statements for mutable and non-mutable events, and the replaceable mutant
    events for mutable events.
    :param method:
    :param mutant_result_file_path:
    :return: all in one queue and a list of queues with single mutant.
    """

    statement_queue = Queue()
    statement_queue_list = []

    mutable_event_index = set()

    # build the all-in-one queue
    event_index = 0
    for event in method.get_events():
        event_mutant_info = MutantInfoPerEvent(mutant_result_file_path, event,
                                               event_index)
        # mutable flag
        mutable_flag = event_mutant_info.is_mutable_event()
        # event is non-mutable event
        if not mutable_flag:
            statement_queue.put(Statement(event))
        # event is mutable event
        else:
            mutable_event_index.add(event_index)
            # add mutable event and its replaceable mutants to statement queue
            statement_queue = add_mutant_event_statements(statement_queue, event, event_mutant_info)

        event_index += 1

    # if the mutable event is more than one, build a list of queue with every single mutant.
    if len(mutable_event_index) > 1:

        for mutant_index in mutable_event_index:
            single_mutant_statement_queue = Queue()
            event_index = 0
            for event in method.get_events():
                event_mutant_info = MutantInfoPerEvent(mutant_result_file_path, event,
                                                       event_index)
                # event index is the mutant_index, this means we will create a statement queue with this index event
                if event_index == mutant_index:
                    single_mutant_statement_queue = add_mutant_event_statements(single_mutant_statement_queue,
                                                                                event, event_mutant_info)
                # event is non-target event
                else:
                    single_mutant_statement_queue.put(Statement(event))

                event_index += 1

            # add statement queue for target event to the queue list
            statement_queue_list.append(single_mutant_statement_queue)

    return statement_queue, statement_queue_list


# TODO: Rework the generate method so that we will generate one method for each mutable event,
#  and then one more for all mutable event
def generate_single(method: GUIMethod, language: str, mutant_result_file_path: str):
    """
    Generating many methods by given basic method and mutant result.
    Each method will only have one mutant.

    :param method: The basic method obj of GUIMethod type
    :param language: now only support "java"
    :param mutant_result_file_path: The file path where it stores the mutant results.
    :return: none
    """

    # get output file path
    output_directory, output_full_path = get_output_file_path(mutant_result_file_path)

    method_path = ""
    if language.lower() == "java":
        method_path = output_full_path.replace(".txt", ".java.txt")
    else:
        raise MethodGeneratorException("language not supported: " + language)

    # create a statement queue
    statement_queue = generate_statement_queue(method, mutant_result_file_path)

    # create header based on statements
    header: Header = Header(statement_queue, method)

    # Open method file to write method
    # Check whether the directory path exists or not
    is_exist = os.path.exists(output_directory)
    if not is_exist:
        # Create a new directory
        os.makedirs(output_directory)

    with open(method_path, 'w') as method_file:

        write_header_java(header, method_file)
        write_body_java(statement_queue, method_file)


def generate_all(method: GUIMethod, language: str, mutant_result_file_path: str):
    """
    Generating the method by given basic method and mutant result.
    put all mutant in one method

    :param method: The basic method obj of GUIMethod type
    :param language: now only support "java"
    :param mutant_result_file_path: The file path where it stores the mutant results.
    :return: none
    """

    # get output file path
    output_directory, output_full_path = get_output_file_path(mutant_result_file_path)

    # create a statement queue
    statement_queue, statement_queue_single_mutant_list = generate_statement(method, mutant_result_file_path)

    # create header based on statements
    header: Header = Header(statement_queue, method)

    method_path = ""
    if language.lower() == "java":
        method_path = output_directory + header.get_name() + ".java.txt"
    else:
        raise MethodGeneratorException("language not supported: " + language)

    # Open method file to write method
    # Check whether the directory path exists or not
    is_exist = os.path.exists(output_directory)
    if not is_exist:
        # Create a new directory
        os.makedirs(output_directory)

    with open(method_path, 'w') as method_file:

        write_header_java(header, method_file)
        write_body_java(statement_queue, method_file)

    # write optional single mutant event method
    if len(statement_queue_single_mutant_list) > 1:
        count = 1
        for statement_queue_single_mutant in statement_queue_single_mutant_list:
            header_single_mutant: Header = Header(statement_queue_single_mutant, method)
            header_single_mutant.set_name(header.get_name()+str(count))

            # new method path
            method_path_single_mutant = output_directory + header_single_mutant.get_name() + ".java.txt"

            with open(method_path_single_mutant, 'w') as method_file_single_mutant:
                write_header_java(header_single_mutant, method_file_single_mutant)
                write_body_java(statement_queue_single_mutant, method_file_single_mutant)

            count += 1