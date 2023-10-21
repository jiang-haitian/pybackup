import os
import shutil
from pycksum import cksum
from tqdm import tqdm
import argparse

suffixes = ['caj', 'md', 'txt', 'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'jpg', 'jpeg', 'bmp', 'gif']

def main(current_dir, target_dir, check_only, auto_delete, use_cksum):
    delete_list = []

    size = len([None for _ in os.walk(current_dir)])

    print = tqdm.write
    for root, dirs, files in tqdm(os.walk(current_dir), total=size):
        target_root = root.replace(current_dir, target_dir)
        if not os.path.isdir(target_root):
            os.mkdir(target_root)
            print(f'mkdir {target_root}')

        for src_file in files:
            suffix = src_file.split('.')[-1]
            if not suffix.lower() in suffixes:
                continue

            dst_file = os.path.join(target_root, src_file)
            src_file = os.path.join(root, src_file)

            if not os.path.isfile(dst_file):
                print(f'New {dst_file}')
                if not check_only:
                    shutil.copy2(src_file, dst_file)
            else:
                if use_cksum:
                    # may be very slow
                    with open(dst_file, 'rb') as df, open(src_file, 'rb') as sf:
                        df_ck = cksum(df)
                        sf_ck = cksum(sf)
                    update_flag = df_ck != sf_ck
                else:
                    update_flag = os.path.getmtime(src_file) > os.path.getmtime(dst_file)

                if update_flag:
                    print(f'Update {dst_file}')
                    if not check_only:
                        shutil.copy2(src_file, dst_file)

        for tgt_obj in os.listdir(target_root):
            if not tgt_obj in files+dirs:
                delete_list.append(os.path.join(target_root, tgt_obj))

    if len(delete_list) == 0:
        exit()

    print('Delete list:')
    for tgt_obj in delete_list:
        if os.path.isfile(tgt_obj):
            print(f'FILE: {tgt_obj}')
        else:
            print(f'DIR: {tgt_obj}')

    if check_only:
        exit()

    delete_flag = True

    if not auto_delete:
        code = input('Enter *DELETE* to confirm: ')
        delete_flag = code == 'DELETE'

    if delete_flag:
        for tgt_obj in delete_list:
            if os.path.isfile(tgt_obj):
                os.remove(tgt_obj)
            else: # dir
                shutil.rmtree(tgt_obj)
        print('done')
    else:
        print('cancel')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--current_dir', default='H:/', type=str)
    parser.add_argument('--target_dir', default='D:/backup/', type=str)
    parser.add_argument('--check_only', action='store_true', default=False)
    parser.add_argument('--auto_delete', action='store_true', default=False)
    parser.add_argument('--cksum', action='store_true', default=False)
    args = parser.parse_args()

    assert os.path.isdir(args.current_dir)
    assert os.path.isdir(args.target_dir)

    main(args.current_dir, args.target_dir, args.check_only, args.auto_delete, args.cksum)