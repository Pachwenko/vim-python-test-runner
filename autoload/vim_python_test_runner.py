#!/bin/env python
import os
import re
import json


class NotDjango(Exception):

    def __str__(self):
        return "Are you sure this is a Django project?"


class NoVimDjango(Exception):

    def __str__(self):
        return ".vim-django file does not exist or is improperly formated. ':help vim-python-test-runner.txt'"


def get_command_to_run_the_current_app(current_dir):
    path_to_manage = find_path_to_file(current_dir, "manage.py", NotDjango)
    app_name = get_app_name(current_dir)
    env_name = get_env_name_if_exists(current_dir)
    flags = get_flags(current_dir)
    command = "{0}{1}test {2}{3}".format(path_to_manage, env_name, flags, app_name)
    write_test_command_to_cache_file(command)
    return (command)


def get_command_to_run_the_current_file(current_dir):
    command_to_current_app = get_command_to_run_the_current_app(current_dir)
    path_to_tests = get_dot_notation_path_to_test(current_dir)
    file_name = get_file_name(current_dir)
    cmd = "{}.{}.{}".format(command_to_current_app, path_to_tests, file_name)
    write_test_command_to_cache_file(cmd)
    return cmd


def get_command_to_run_the_current_class(current_dir, current_line, current_buffer):
    class_name = get_current_method_and_class(current_line, current_buffer)[0]
    divider = '.' if get_test_runner(current_dir) == 'django' else ':'
    cmd = "{}{}{}".format(get_command_to_run_the_current_file(current_dir), divider, class_name)
    write_test_command_to_cache_file(cmd)
    return cmd


def get_command_to_run_the_current_method(current_dir, current_line, current_buffer):
    # raise Exception('here')
    print('hereeee')
    method_name = get_current_method_and_class(current_line, current_buffer)[1]
    print("method_name==({})".format(method_name))
    command_to_current_class = get_command_to_run_the_current_class(current_dir, current_line, current_buffer)
    print("command_to_current_class==({})".format(command_to_current_class))
    cmd = "{}.{}".format(command_to_current_class, method_name)
    print("cmd==({})".format(cmd))
    write_test_command_to_cache_file(cmd)
    return cmd


def get_command_to_run_current_file_with_nosetests(path_to_current_file):
    command = ":!nosetests {0}".format(path_to_current_file)
    write_test_command_to_cache_file(command)
    return command


def get_command_to_run_current_class_with_nosetests(path_to_current_file, current_line, current_buffer):
    run_file = get_command_to_run_current_file_with_nosetests(path_to_current_file)
    current_class = get_current_method_and_class(current_line, current_buffer)[0]
    command = run_file + ":" + current_class
    write_test_command_to_cache_file(command)
    return command


def get_command_to_run_current_method_with_nosetests(path_to_current_file, current_line, current_buffer):
    run_class = get_command_to_run_current_class_with_nosetests(path_to_current_file, current_line, current_buffer)
    current_method = get_current_method_and_class(current_line, current_buffer)[1]
    command = run_class + "." + current_method
    write_test_command_to_cache_file(command)
    return command


def get_command_to_run_current_base_method_with_nosetests(path_to_current_file, current_line, current_buffer):
    run_file = get_command_to_run_current_file_with_nosetests(path_to_current_file)
    current_method = get_current_method_and_class(current_line, current_buffer)[1]
    command = run_file + ":" + current_method
    write_test_command_to_cache_file(command)
    return command


def get_command_to_run_current_file_with_pytests(path_to_current_file):
    command = ":!pytest {0}".format(path_to_current_file)
    write_test_command_to_cache_file(command)
    return command


def get_command_to_run_current_class_with_pytests(path_to_current_file, current_line, current_buffer):
    run_file = get_command_to_run_current_file_with_pytests(path_to_current_file)
    current_class = get_current_method_and_class(current_line, current_buffer)[0]
    command = run_file + "::" + current_class
    write_test_command_to_cache_file(command)
    return command


def get_command_to_run_current_method_with_pytests(path_to_current_file, current_line, current_buffer):
    run_class = get_command_to_run_current_class_with_pytests(path_to_current_file, current_line, current_buffer)
    current_method = get_current_method_and_class(current_line, current_buffer)[1]
    command = run_class + "::" + current_method
    write_test_command_to_cache_file(command)
    return command


def get_command_to_run_current_base_method_with_pytests(path_to_current_file, current_line, current_buffer):
    run_file = get_command_to_run_current_file_with_pytests(path_to_current_file)
    current_method = get_current_method_and_class(current_line, current_buffer)[1]
    command = run_file + "::" + current_method
    write_test_command_to_cache_file(command)
    return command


def get_command_to_rerun_last_tests():
    with open("/tmp/vim_python_test_runner_cache", "r") as f:
        return f.read()


def write_test_command_to_cache_file(command):
    with open("/tmp/vim_python_test_runner_cache", "w") as f:
        f.write(command)


def find_path_to_file(current_dir, file_to_look_for, raise_exception=False):
    dir_list = [directory for directory in current_dir.split(os.path.sep) if directory]
    for x in range(len(dir_list) - 1, -1, -1):
        path_to_check = os.path.sep + os.path.sep.join(dir_list[:x])
        if file_to_look_for in os.listdir(path_to_check):
            return path_to_check + os.sep + file_to_look_for
    raise raise_exception


def get_app_name(current_dir):
    apps = get_json_field_from_config_file(current_dir, "app_name")
    print("apps==({})".format(apps))
    try:
        current_dirs = current_dir.split(os.sep)
        for app in apps.split(','):
            if f'/{app.lstrip()}/' in current_dir:
                return app.lstrip()
        # result = [
        #     app.lstrip() for app in apps.split(",")
        #     if app.lstrip() in current_dir
        # ][0]
        print("result==({})".format(result))
        return result
    except:
        raise NoVimDjango


def has_exact_match(array, to_find):
    for x in array:
        if x == to_find:
            return True
    return False


def get_dot_notation_path_to_test(current_dir):
    print("current_dir==({})".format(current_dir))
    app_name = get_app_name(current_dir)
    print("app_name==({})".format(app_name))
    if app_name:
        # TODO: failing in here index out of range
        print("current_dir==({})".format(current_dir))
        print("os.sep + app_name + os.sep==({})".format(os.sep + app_name + os.sep))
        print("current_dir.split(os.sep + app_name + os.sep)==({})".format(current_dir.split(os.sep + app_name + os.sep)))
        split = current_dir.split(os.sep + app_name + os.sep)
        # raise Exception(str(split))
        path_to_tests = split[1]
        return ".".join(path_to_tests.split("/")[:-1])
    return False


def get_file_name(current_dir):
    path_parts = current_dir.split(os.sep)
    return path_parts[-1].split(".")[0]


def get_current_method_and_class(current_line_index, current_buffer):
    class_regex, class_name = re.compile(r"^class (?P<class_name>.+)\("), False
    method_regex, method_name = re.compile(r"def (?P<method_name>.+)\("), False
    for line in range(current_line_index - 1, -1, -1):
        if class_regex.search(current_buffer[line]) is not None and not class_name:
            class_name = class_regex.search(current_buffer[line])
            class_name = class_name.group(1)
        if method_regex.search(current_buffer[line]) is not None and not method_name and not class_name:
            method_name = method_regex.search(current_buffer[line])
            method_name = method_name.group(1)
    return (class_name, method_name)


def get_json_field_from_config_file(current_dir, field_name):
    try:
        with open(find_path_to_file(current_dir, ".vim-django"), "r") as f:
            json_string = f.read()
        parsed_json = json.loads(json_string)
        return parsed_json[field_name]
    except Exception:
        return False


def get_flags(current_dir):
    formatted_flags = ""
    user_flags = get_json_field_from_config_file(current_dir, "flags") or []
    for flag in user_flags:
        formatted_flags += "--{} ".format(flag)
    return formatted_flags


def get_env_name_if_exists(current_dir):
    env_name = get_json_field_from_config_file(current_dir, "environment")
    if env_name:
        return " {} ".format(env_name)
    return " "


def get_test_runner(current_dir):
    runner = get_json_field_from_config_file(current_dir, "test-runner")
    if runner:
        return "{}".format(runner)
    return " "


# method_name==(test_related_perils_are_returned_in_coverage_data)

# Error detected while processing function vim_python_test_runner#RunDesiredTests:
# line   49:
# Traceback (most recent call last):
#   File "<string>", line 38, in main
#   File "<string>", line 21, in get_proper_command
#   File "<string>", line 10, in <lambda>
#   File "/Users/patrickmccartney/dotfiles/vim/plugged/vim-python-test-runner/autoload/vim_python_test_r
# unner.py", line 51, in get_command_to_run_the_current_method
#     command_to_current_class = get_command_to_run_the_current_class(current_dir, current_line, current
# _buffer)
#   File "/Users/patrickmccartney/dotfiles/vim/plugged/vim-python-test-runner/autoload/vim_python_test_r
# unner.py", line 41, in get_command_to_run_the_current_class
#     cmd = "{}{}{}".format(get_command_to_run_the_current_file(current_dir), divider, class_name)
#   File "/Users/patrickmccartney/dotfiles/vim/plugged/vim-python-test-runner/autoload/vim_python_test_r
# unner.py", line 31, in get_command_to_run_the_current_file
#     path_to_tests = get_dot_notation_path_to_test(current_dir)
#   File "/Users/patrickmccartney/dotfiles/vim/plugged/vim-python-test-runner/autoload/vim_python_test_r
# unner.py", line 149, in get_dot_notation_path_to_test
#     path_to_tests = current_dir.split(os.sep + app_name + os.sep)[1]
# IndexError: list index out of range
