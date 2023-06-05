from sicasm_package.AssemblerDirectives import *
from sicasm_package.OPTAB import *
import re

class Expression_ERROR(Exception):
    def __init__(self, message):
        super().__init__(message)

# 建立symbol type table
def build_SymbolTypeTable(SYMTAB):
  global SymbolType
  for i in SYMTAB:
    SymbolType[i] = 'R'
  return SymbolType

# 取得expression的type
# step1. 對expression進行切割，並存成list(split_result)
# step2. 把split_result中的symbol和constant更換成各自對應到的type (R -> 1, A -> 0)
# step3. 把整個list轉成字串，並進行計算
# step4. 回傳結果
def get_expression_type(expression):
  split_result = re.split('([+|-])', expression) # 對expression進行切割
  split_result = [item for item in split_result if item != ''] # 移除''的元素
  # 把split_result中的symbol和constant更換成各自對應到的type (R -> 1, A -> 0)
  split_result = [item if item == '+' or item == '-' else '1' if SymbolType.get(item.upper(),item) =='R'  else '0' for item in split_result]
  split_result = ''.join(split_result) # 把list轉成字串
  ans = eval(split_result) # 取得字串計算的結果
  return ans

# 檢查expression的結果是合法or不合法(0 -> A)(1 -> R)(other -> 不合法)
# 合法
'''
# 如果EQU有使用expression且expression的type是Absolute -> 需要去修正SymbolType中的Type值為'A'
# 如果其他instruction有使用expression且expression的type是Relative -> 把該行內容儲存於modification_item的list中，方便後續撰寫Modification Record
'''
# 不合法: 跳出錯誤訊息並終止程式
def check_expression(Inter_file2):
  global SymbolType
  global modification_line
  #print('=====  EXPRESSION CHECK  =====')
  for line in Inter_file2:
    if line['Instruction'] == 'EQU':
      if line['Operand'] != '*':
        expression_type = get_expression_type(line['Operand']) 
        if expression_type == 0:
          # 修正SymbolType中的type為'A'
          SymbolType[line['Symbol']] = 'A' 
          #print(f'OK\n{line}')
        elif expression_type == 1:
          continue
        else:
          raise Expression_ERROR(f"輸入錯誤：{line['Operand']} 發生錯誤，這是不合法的 Expression\n")
          break #不合法
    elif '+' in line['Operand'] or '-' in line['Operand']:
      expression_type = get_expression_type(line['Operand']) 
      if expression_type == 0:
        continue
      elif expression_type == 1:
        #print(f'OK\n{line}')
        if line['Instruction'][0] == '+' or line['Instruction'] == 'WORD': 
          modification_line.append(line)
      else:
        raise Expression_ERROR(f"輸入錯誤：{line['Operand']} 發生錯誤，這是不合法的 Expression\n")
        break #不合法 

# 取得所有要建立modification record的line
def get_modificationLine(Inter_file2, SYMTAB):
  global modification_line
  for line in Inter_file2:
    if '+' in line['Instruction']:
      if line['Operand'][0] == '#' and line['Operand'][1:] not in SYMTAB:
        continue
      else:
        modification_line.append(line)
  
  modification_line.sort(key=lambda x: int(x['LOC'],16))
  return modification_line

# 紀錄header record
def write_header(Program_name, Inter_file2, SYMTAB):
  header_record = []
  buffer = ''
  program_name = Program_name.ljust(6)
  starting_address = '{:0>6}'.format(SYMTAB[Program_name])
  object_program_length = '{:0>6}'.format(hex(int(Inter_file2[-1]['LOC'],16)-int(SYMTAB[Program_name],16))[2:].upper())
  buffer = 'H' + program_name + starting_address + object_program_length
  header_record.append(buffer)
  return header_record

# 紀錄text record
def write_text(Program_name, Inter_file2, SYMTAB):
  # 儲存'T'和starting address和此record的長度(未知，預設為'XX，要把buffer放入text_record前在修正)
  buffer = 'T'+'{:0>6}'.format(SYMTAB[Program_name])+'XX'
  text_record = []

  for line in Inter_file2:

    # 判斷是否有object code存在(是：,否：判斷是否換行)
    if line['ObjectCode'] == 'none': 
      if line['Instruction'] == 'END' and len(buffer) != 0:
        length = '{:0>2}'.format(hex(len(buffer[9:])//2)[2:].upper())
        buffer = buffer.replace('XX',length)
        text_record.append(buffer)
      elif line['Instruction'] == 'RESW' or line['Instruction'] == 'RESB':
        if len(buffer) < 10:
          buffer = ''
        else:
            # 把buffer的值加入text_record
            # 清空buffer
            length = '{:0>2}'.format(hex(len(buffer[9:])//2)[2:].upper())
            buffer = buffer.replace('XX',length)
            text_record.append(buffer)
            buffer = ''
      else:
        continue
    else:
      if (len(buffer[9:])+len(line['ObjectCode']))//2 > 30:
        # 把buffer的值加入text_record
        # 清空buffer
        length = '{:0>2}'.format(hex(len(buffer[9:])//2)[2:].upper())
        buffer = buffer.replace('XX',length)
        text_record.append(buffer)
        buffer = 'T'+'{:0>6}'.format(line['LOC'])+'XX'+line['ObjectCode']
      else:
        if len(buffer) == 0:
          buffer = 'T'+'{:0>6}'.format(line['LOC'])+'XX'
        buffer += line['ObjectCode']
  return text_record

# 紀錄modification record
# relative不會是負的
def write_modification(Program_name):
  modification_record = []
  buffer = ''
  for line in modification_line: # 要考慮Operand是expression的狀況
    if '+' in line['Instruction']: 
      starting_address = '{:0>6}'.format(hex(int(line['LOC'],16)+1)[2:].upper())
      modified_length = '05'
    else: 
      starting_address = '{:0>6}'.format(line['LOC'])
      modified_length = '06'
    buffer = 'M' + starting_address + modified_length + f'+{Program_name}'
    modification_record.append(buffer)
  return modification_record

# 紀錄end record
def write_end(Program_name, SYMTAB):
  end_record = []
  buffer = 'E'+'{:0>6}'.format(SYMTAB[Program_name])
  end_record.append(buffer)
  return end_record

# 寫檔
def write_file(file_name, header_record, text_record, modification_record, end_record):
  data = []
  data.append(header_record)
  data.append(text_record)
  data.append(modification_record)
  data.append(end_record)

  filename = file_name
  #print('\n\n==========  RESULT  ==========')
  with open(filename, 'w') as file:
      for item in data:
          for line in item:
            if item[0][0] == 'E':
              #print(line)
              file.write(line)
            else:
              #print(line)
              file.write(line + '\n')

# pass2_2的主程式
def pass2_2(file_name, Program_name, Inter_file2, SYMTAB, file_name_without_extension):
  global SymbolType
  global modification_line
  SymbolType = {}
  modification_line = []
  header_record = []
  text_record = []
  modification_record = []
  end_record = []

  SymbolType = build_SymbolTypeTable(SYMTAB) # 初始化symbol type table(type全部預設為'R'，後續在check_expression()時會去修正)
  check_expression(Inter_file2) # 檢查expression的結果是合法or不合法
  modification_line = get_modificationLine(Inter_file2, SYMTAB) # 取得所有要建立modification record的line
  header_record = write_header(Program_name, Inter_file2, SYMTAB) # 紀錄Header Reocrd
  text_record = write_text(Program_name, Inter_file2, SYMTAB) # 紀錄Text Reocrd
  modification_record = write_modification(Program_name) # 紀錄Modification Reocrd
  end_record = write_end(Program_name, SYMTAB) # 紀錄End Reocrd
  write_file(f'{file_name_without_extension}.obj', header_record, text_record, modification_record, end_record) # 輸出結果並存成.obj檔
