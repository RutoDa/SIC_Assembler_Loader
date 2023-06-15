from sicasm_package.Error_Scan import *
from sicasm_package.Pass1 import *
from sicasm_package.Pass2_1 import *
from sicasm_package.Pass2_2 import *
import argparse
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("InputFile", help="要編譯的檔案名稱(需放在同個目錄底下)或檔案路徑")
    args = parser.parse_args()
    file_name = args.InputFile
    file_basename = os.path.basename(file_name)
    file_name_without_extension = os.path.splitext(file_basename)[0]
    if error_scan(file_name):
        try:
            Inter_file, SYMTAB, Program_name = pass1(file_name)
            output, Inter_file2 = pass2_1(Inter_file, SYMTAB)
            pass2_2(file_name, Program_name, Inter_file2, SYMTAB, file_name_without_extension)
    
            # pass2_2確認沒有expression illegal後會輸出object file，以下為提示使用者已輸出完成
            print(f"輸出Object File: {file_name_without_extension}.obj")
            # 接著，會輸出題目指定的輸出
            with open(f"{file_name_without_extension}_output.txt", "w") as file:
                for line in output:
                    file.write(line + "\n")
            print(f"輸出題目要求的輸出: {file_name_without_extension}_output.txt")
        except PC_Base_ERROR as msg:
            print(msg)
            print('程式因錯誤暫停執行!!')
        except Expression_ERROR as msg:
            print(msg)
            print('程式因錯誤暫停執行!!')
        except :          
            print('程式因不明錯誤暫停執行!!')
    else:
        print('程式因錯誤暫停執行!!')