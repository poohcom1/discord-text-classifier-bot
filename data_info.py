import os
import util.config_loader as cfg

data_dir = cfg.get('data_dir_name')
train_dir = os.path.join(data_dir, cfg.get('train_dir_name'))
test_dir = os.path.join(data_dir, cfg.get('test_dir_name'))


msg_count = 0
train_count = 0
test_count = 0
user_set = set()

for folder in os.listdir(train_dir):
    user_set.add(folder)

    for file in os.listdir(os.path.join(train_dir, folder)):
        msg_count += 1
        train_count += 1

for folder in os.listdir(test_dir):
    user_set.add(folder)

    for file in os.listdir(os.path.join(test_dir, folder)):
        msg_count += 1
        test_count += 1

print('Total users:', len(user_set))
print('Total messages:', msg_count)
print('Training data:', train_count, '-',
      str(int(train_count/msg_count*100)) + '%')
print('Test data:', test_count, '-',
      str(int(test_count/msg_count*100)) + '%')
