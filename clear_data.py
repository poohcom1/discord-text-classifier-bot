import shutil
import util.config_loader as cfg

confirm = input("Are you sure? ")

if confirm == 'yes' or confirm == 'y':
    print("Clearing data...")
    shutil.rmtree(cfg.get('data_dir_name'))
    print("Deleted")
else:
    print("Aborting")
