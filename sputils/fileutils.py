# import video_2_frame_folder as video_converter
# import argparse
import os
import fnmatch
# from tqdm import tqdm


def find_all_files(input_path, ending):
    '''
    find all files with endnin
    :param input_path:
    :param ending:
    :return:
    '''
    input_path_co = correct_path(input_path)
    output_files = []
    for root, dirs, files in os.walk(input_path_co):
        for file in files:
            if file.startswith('.'):
                continue
            if file.endswith(ending): #fnmatch.fnmatch(file, ending):
                output_files.append(os.path.join(root,file))
    # print(files)
    return output_files


def correct_path(path):
    '''
    Correct the path when it statrs the with ~ (LINUX MAXOS case)
    :param path:
    :return:
    '''
    if path.startswith('~'):
        path = os.path.expanduser(path)
    return os.path.abspath(path)