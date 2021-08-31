import os
import util.config_loader as cfg

data_dir = cfg.get('data_dir_name')
train_dir = os.path.join(data_dir, cfg.get('train_dir_name'))
test_dir = os.path.join(data_dir, cfg.get('test_dir_name'))


msg_count = 0
train_count = 0
test_count = 0

word_count = 0

user_set_train = set()
user_set_test = set()
user_msg_count = {}


def word_counter(fileName):
    with open(fileName) as file:
        words = 0
        for lines in file.readlines():
            words += len(lines.split())

    return words


for folder in os.listdir(train_dir):
    user_set_train.add(folder)
    i = 0

    for file in os.listdir(os.path.join(train_dir, folder)):
        msg_count += 1
        train_count += 1
        word_count += word_counter(os.path.join(train_dir, folder, file))
        i += 1

    user_msg_count[folder] = i

for folder in os.listdir(test_dir):
    user_set_test.add(folder)
    i = 0

    for file in os.listdir(os.path.join(test_dir, folder)):
        msg_count += 1
        test_count += 1
        word_count += word_counter(os.path.join(test_dir, folder, file))

        i += 1
    user_msg_count[folder] = i

if __name__ == '__main__':
    print('Total users:', len(user_set_train))
    print('Total messages:', msg_count)
    print('Avg word count:', word_count/msg_count)
    print('Training data:', train_count, '-',
          str(int(train_count/msg_count*100)) + '%')
    print('Test data:', test_count, '-',
          str(int(test_count/msg_count*100)) + '%')

    for user in user_msg_count:
        print(user, ':', user_msg_count[user])
