import os
import sys
import shutil
from data_info import user_msg_count, test_dir, train_dir


def remove_user(user):
    for dir in [test_dir, train_dir]:
        if user in os.listdir(dir):
            shutil.rmtree(os.path.join(dir, user))


if len(sys.argv) > 2 and sys.argv[1] == 'threshold':
    threshold = sys.argv[2]

    count = 0
    for user in user_msg_count:
        if user_msg_count[user] <= int(threshold):
            remove_user(user)
            count += 1
    print("Remove %d users!" % (count))
else:
    while True:
        user_to_purge = input("User ID: ")

        if user_to_purge == 'q':
            exit()

        if user_to_purge not in user_msg_count:
            print('User not found!')
            continue

        confirmation = input('User has %d messages. Are you sure? (y/n) ' %
                             (user_msg_count[user_to_purge]))

        if confirmation != 'y' and confirmation != 'yes':
            continue

        remove_user(user_to_purge)

        print("User purged!")
