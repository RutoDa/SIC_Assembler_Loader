from sicasm_package.AssemblerDirectives import *
from sicasm_package.OPTAB import *
from sicasm_package.Register import *

class PC_Base_ERROR(Exception):
    def __init__(self, message):
        super().__init__(message)

def handle_comment(index):
  output.append(f'{index:<2} Comment')

def handle_directive(index, line, directive, operand, SYMTAB):
  #'START', 'END', 'BYTE', 'WORD', 'RESB', 'RESW', 'BASE', 'EQU'
  global object_code
  global output
  if directive == 'START':
    output.append(f'{index:<2} LOC={line[0]}  none')
  elif directive == 'BASE':
    global base
    base = SYMTAB[operand]
    output.append(f'{index:<2} LOC={line[0]}  none')
  elif directive == 'BYTE':
    object_code = ''
    if operand[0] == 'C':
      # 要儲存字串
      string = operand.split("'")[1] #取欲儲存的字串
      for char in string:
        object_code += hex(ord(char))[2:].upper() # 將字串轉換為十六進位的ASCII
    elif operand[0] == 'X':
      # 要儲存十六進位
      object_code = operand.split("'")[1].upper() #取欲儲存的十六進位(2個十六進位組成一個BYTE)
    output.append(f'{index:<2} LOC={line[0]}  {object_code}, BYTE') 
  elif directive == 'WORD':
    if '+' in operand or '-' in operand:
      expression = operand
      object_code = compute_expression(expression, SYMTAB).zfill(6)
    else:
      object_code = hex(int(operand))[2:].upper().zfill(6)
    output.append(f'{index:<2} LOC={line[0]}  {object_code}, WORD') 
  else:
    # 處理 RESB RESW EQU END
    output.append(f'{index:<2} LOC={line[0]}  none')

def compute_negative_hex(decimal_number):
  """轉換十進位的負數為十六進位的二補數"""
  return hex(int('FFF', 16) - abs(decimal_number) + 1)[2:].upper()

def compute_disp_hex(pc, base, TA, SYMTAB):
  """Input: PC位址, BASE位址, TA位址
     return is_pc, is_base, is_error, disp_hex(3個16進位的disp)"""
  # 計算disp與決定用哪種relative
  disp_dec = int(TA, 16) - int(pc, 16)      # 10進位的disp(pc與TA的距離)
  if (-2048 <= disp_dec <= 2047):           # 是否符合 pc relatuve
    # return is_pc(1), is_base(0), is_error(0), 3個16進位的disp
    if disp_dec >= 0:
      return 1, 0, 0, hex(disp_dec)[2:].upper().zfill(3) 
    else:
      return 1, 0, 0, compute_negative_hex(disp_dec)
  else:
    disp_dec = int(TA, 16) - int(base, 16)  # 10進位的disp(base與TA的距離)
    if (0 <= disp_dec <= 4095):             # 是否符合 base relative
      # return is_pc(0), is_base(1), is_error(0) ,3個16進位的disp
      return 0, 1, 0, hex(disp_dec)[2:].upper().zfill(3)  
    else:
      # return is_pc(0), is_base(0), is_error(1), 000
      return 0, 0, 1, '000'                 # 皆不能的話表示有ERROR

def compute_opcode_ni_hex(opcode, is_indirect, is_immediate):
  """Input: opcode(10進位), is_indirect(是否為間接定址), is_immediate(是否為立即定址)
     return opcode_ni_hex(opcode加上ni後的兩個16進位)"""
  if not is_indirect and not is_immediate:
    #simple addressin (n=1, i=1)
    ni = 3
  else:
    ni = int(f'{is_indirect}{is_immediate}', 2)
  # return opcode_ni_hex(opcode加上ni後的兩個16進位)
  return hex(opcode + ni)[2:].upper().zfill(2)

def compute_expression(expression, SYMTAB):
  """ Input 為 expression，
      Output為 expression計算後的結果(16進位)"""
  # 將SYMTAB中的Symbol替換為對應的address
  for symbol in  sorted(SYMTAB.keys(), key=len ,reverse=True):
      expression = expression.upper().replace(symbol, str(int(SYMTAB.get(symbol),16)))
  result = eval(expression)
  if result < 0:
    return hex(int(compute_negative_hex(result), 16))[2:].upper()
  else:
    return hex(result)[2:].upper()

def handle_OP(index, line, pc, base, mnemonic, operand, SYMTAB):
  global output
  global object_code
  is_format2 = 0
  is_format4 = 0
  is_pc = 0
  is_base = 0
  is_immediate = 0
  is_indirect = 0
  is_indexed = 0
  is_error = 0

  loc = line[0]
  xbpe_hex = 'A'

  # format 2
  if mnemonic in Format2_mnemonic:
    is_format2 = 1
  # format 4
  elif mnemonic[0] == '+':
    mnemonic = mnemonic[1:]
    is_format4 = 1
  
  # immediate 、 indirect 與 indexed 為互斥的
  if operand[0] == '#':
    # immediate addressing
    is_immediate = 1
    operand = operand[1:]
  elif operand[0] == '@':
    # indirect addressing
    is_indirect = 1
    operand = operand[1:]
  elif ',X' in operand and not is_format2:
    # indexed addressing
    is_indexed = 1
    operand = operand.split(',')[0]
  

  if is_format2:
    # 處理format 2
    opcode = OPTAB[mnemonic] # 16進位的opcode
    operand = operand.split(',')
    if len(operand) == 2:
      object_code = f'{opcode}{Register[operand[0]]}{Register[operand[1]]}'
    else:
      object_code = f'{opcode}{Register[operand[0]]}0'
  elif is_format4:
    # 處理format 4
    if is_immediate and operand not in SYMTAB:
      # immediate addressing 
      # 且 operand 為常數 => disp 為該常數的十六進位
        address_hex = hex(int(operand))[2:].upper().zfill(5)
      # 判斷是否有expression，有的話需要特別處理，沒有的話address欄位可以直接填
    else:
      if '+' in operand or '-' in operand:
        expression = operand
        address_hex = compute_expression(expression ,SYMTAB).zfill(5)
      else:
        address_hex = SYMTAB[operand].zfill(5) # 5個16進位的絕對位址
    #算opcode+ni的16進位字元(2個字元)
    opcode = int(OPTAB[mnemonic], 16) # 10進位的opcode
    opcode_ni_hex = compute_opcode_ni_hex(opcode, is_indirect, is_immediate)
    #xbpe的字串
    xbpe_hex = hex(int(f'{is_indexed}{is_base}{is_pc}{is_format4}', 2))[2:].upper()
    object_code = f'{opcode_ni_hex}{xbpe_hex}{address_hex}'
  else: 
    # 處理format 3
    if is_immediate and operand not in SYMTAB:
      # immediate addressing 
      # 且 operand 為常數 => disp 為該常數的十六進位
        disp_hex = hex(int(operand))[2:].upper().zfill(3)
    else:
      # 判斷是否有expression，有的話需要特別處理
      if '+' in operand or '-' in operand:
        expression = operand
        TA = compute_expression(expression, SYMTAB) 
      else:
        TA = SYMTAB[operand]
      is_pc, is_base, is_error, disp_hex = compute_disp_hex(pc, base, TA, SYMTAB)
      if is_error:
        raise PC_Base_ERROR(f"輸入錯誤：第{index}行發生錯誤，PC Relative 與 Base Relative 皆無法使用\n")
    #算opcode+ni的16進位字元(2個字元)
    opcode = int(OPTAB[mnemonic], 16) # 10進位的opcode
    opcode_ni_hex = compute_opcode_ni_hex(opcode, is_indirect, is_immediate)
    
    #xbpe的字串
    xbpe_hex = hex(int(f'{is_indexed}{is_base}{is_pc}{is_format4}', 2))[2:].upper()
    
    object_code = f'{opcode_ni_hex}{xbpe_hex}{disp_hex}'
  
  if is_format2:
    nixbpe=''
  elif not is_indirect and not is_immediate:
    # simple addressing(n=1,i=1) 
    nixbpe=f', nixbpe=11{bin(int(xbpe_hex, 16))[2:].zfill(4)}' # 11xbpe
  else:
    nixbpe=f', nixbpe={is_indirect}{is_immediate}{bin(int(xbpe_hex, 16))[2:].zfill(4)}' # ??xbpe
  mode = 'format2' if is_format2 else 'format4' if is_format4 else 'pc-relative' if is_pc else 'base-relative' if is_base else 'none'
  output.append(f'{index:<2} LOC={loc}  {object_code}, {mode}{nixbpe}')

def pass2_1(Inter_file, SYMTAB):
  global output
  global object_code
  global base
  output = []
  Inter_file2 = []

  ## output SYMTAB
  output.append('=SYMTAB=')
  for symbol in SYMTAB:
    output.append(f'{symbol:<9}{SYMTAB[symbol]}')
  output.append('')
  output.append('=OBJECT CODES=')

  index = 1
  a = 0
 
  base = ""
  for line_str in Inter_file:
    line = line_str.split()
    object_code = 'none'
    for element in line:
      if element in Assembler_directives:
        directive = element
        operand = line[line.index(element)+1]
        handle_directive(index, line, directive, operand, SYMTAB)
        Inter_file2.append({'LOC':line[0], 'Symbol':"none" if line[1] not in SYMTAB else line[1], 'Instruction':directive, 'Operand':operand, 'ObjectCode':object_code}) #Line[0]為該指令的LOC
        break
      elif element in OPTAB or element[0] == '+':
        if element != 'RSUB':
          mnemonic = element
          operand = line[line.index(element)+1]
          pc = Inter_file[Inter_file.index(line_str)+1].split()[0]
          handle_OP(index, line, pc, base, mnemonic, operand.upper(), SYMTAB)
          Inter_file2.append({'LOC':line[0], 'Symbol':"none" if line[1] not in SYMTAB else line[1], 'Instruction':mnemonic, 'Operand':operand, 'ObjectCode':object_code}) #Line[0]為該指令的LOC
        else:
          Inter_file2.append({'LOC':line[0], 'Symbol':"none" if line[1] not in SYMTAB else line[1], 'Instruction':'RSUB', 'Operand':'none', 'ObjectCode':'4F0000'}) #Line[0]為該指令的LOC
          output.append(f'{index:<2} LOC={line[0]}  4F0000, none, nixbpe=110000')
        break
      elif element[0] == '.':
        handle_comment(index)
        Inter_file2.append({'LOC':line[0], 'Symbol':"none" if line[1] not in SYMTAB else line[1], 'Instruction':'comment', 'Operand':'comment', 'ObjectCode':'none'}) #Line[0]為該指令的LOC
        break
    index += 1
  # 輸出老師指定的output文件
  
  return output, Inter_file2