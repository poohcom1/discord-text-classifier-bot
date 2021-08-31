import os
from data_info import user_msg_count, test_dir, train_dir


def is_below_word_count(file, word_count: int):
    words = 0
    for lines in file.readlines():
        words += len(lines.split())

    return words <= word_count


def purge_files(conditions: list, args: list, count=False):
    removed_files = 0

    for dir in [test_dir, train_dir]:
        for user in os.listdir(dir):
            user_dir = os.path.join(dir, user)
            for fileName in os.listdir(user_dir):
                file_dir = os.path.join(user_dir, fileName)
                with open(file_dir) as file:
                    for i, cond in enumerate(conditions):
                        if cond(file, *(args[i])):
                            if not count:
                                os.remove(file_dir)
                            removed_files += 1
                            break

    return removed_files


if __name__ == '__main__':
    args = [[1]]

    count = purge_files([is_below_word_count], args, False)
    print('Removed %d files' % (count))
