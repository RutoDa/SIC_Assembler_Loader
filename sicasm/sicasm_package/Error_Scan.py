def error_scan(file_path):
  #  讀入資料
  array = []
  with open(file_path, 'r') as file:
      for line in file:
          words = line.split()
          array.append(words)
          
  check = True
  CheckTab = ["ADD","CLEAR","COMP","COMPR","DIV","J","JEQ","JGT",
      "JLT","JSUB","LDA","LDB","LDCH","LDL","LDT","LDX",
      "MUL","RD","RSUB","STA","STB","STCH","STL","STT",
      "STX","SUB","TD","TIX",'TIXR','WD','START', 'END',
      'BYTE', 'WORD', 'RESB', 'RESW', 'BASE', 'EQU', 'ADDR', 'LDS',
      "DIVR", "MULR", "SUBR"]
  Register = ['A','X','L','B','S','T','F','PC','SW']

  #主程式開始
  for index, line in enumerate(array):
    # 1.段落數不合規定----------------------------------------------------
    if len(line)>3 and line[0]!='.':
      output = ' '.join(line)
      print(f'格式錯誤：第{index+1}行"{output}，\n建議修正：請檢查是否有多餘的空格\n')
      check = False

    # 2.operand中不可有空格分割---------------------------------------------
    if len(line) != 1 and line[0] != '.':
      instruction = line[-2]
      if instruction.startswith('+'):
          instruction = instruction[1:]

      if not instruction in CheckTab:
        if not instruction.upper() in CheckTab and ( line[0].upper()in CheckTab or line[1].upper()in CheckTab):
          output = ' '.join(line)
          print(f'格式錯誤：第{index+1}行"{output}"，operand中不可有空格分割\n')
          check = False
    
  #確認沒有格式錯誤後才會判斷輸入錯誤
  if check:
    # 儲存所有Label方便後面做辨識
    Label = []
    for index, line in enumerate(array):
      if len(line) == 3 and line[0]!='.':
        Label.append(line[0])
    
    for index, line in enumerate(array):
      if len(line) != 1 and line[0] != '.':
        # 3.instruction位置是輸入了不合法的資料-------------------------------
        # 4.instruction內容必須是大寫
        instruction = line[-2]
        if instruction.startswith('+'):
            instruction = instruction[1:]
        if not instruction in CheckTab:
          if instruction.upper() in CheckTab:
            print(f'輸入錯誤：第{index+1}行"{line[-2]}"，instruction只能有大寫英文字母\n建議修正：{line[-2].upper()}\n')
          else:
            print(f'輸入錯誤：第{index+1}行"{line[-2]}"，輸入instruction不合法\n')
          check = False
      
        # 5.operand有寫到非數字、label、register的資料----------------------------
        # 6.label、register寫成小寫
        if "'" in line[-1]:
          string = line[-1].split("'")
          if not string[0] == 'X' and not string[0] == 'C':
            if string[0] == 'x' or string[0] == 'c':
              output = ' '.join(line)
              print(f'輸入錯誤：第{index+1}行"{output}"，{string[0]}必須為大寫英文字母\n')
            else:
              output = ' '.join(line)
              print(f'輸入錯誤：第{index+1}行"{output}"，{string[0]}必須改為"C"或"X"\n')
            check = False
        # #number 
        elif line[-1].startswith('#'):
          string = line[-1]
          string = string[1:]
          if not string.isdigit() and not string in Label and not string in Register:
            output = ' '.join(line)
            print(f'輸入錯誤：第{index+1}行"{output}"，"#"後面必須連接數值、label或register\n')
            check = False
        # @ register
        elif line[-1].startswith('@'):
          string = line[-1]
          string = string[1:]
          if not string.isdigit() and not string in Label and not string in Register:
            output = ' '.join(line)
            print(f'輸入錯誤：第{index+1}行"{output}"，"@"後面必須連接數值、label或register\n')
            check = False
        # 不可以出現*/ (但只有*的例外)
        elif ('*' in line[-1] or '/' in line[-1])and line[-1]!='*':
          output = ' '.join(line)
          print(f'輸入錯誤：第{index+1}行"{output}"，不可使用"*"或"/"')
          check = False
        # aa+bb-cc 不會有 register
        elif '+' in line[-1] or '-' in line[-1]:
          result = line[-1].split('+')
          final_result = [item.split('-') for item in result]
          final_result = [item for sublist in final_result for item in sublist]
          for string in final_result:
            if not string.isdigit() and not string in Label and len(string)>0:
              if not string.isdigit() and not string.upper() in Label :
                print('!!!'+str(len(string))+'!!!!!')
                output = ' '.join(line)
                print(f'輸入錯誤：第{index+1}行"{output}"，不可使用未經宣告的label:{string}\n')
                check = False
              else:
                output = ' '.join(line)
                print(f'警告：第{index+1}行"{output}"，label "{string}" 請轉換成大寫\n建議修正：{string.upper()}\n')
        # aa,bb
        elif ',' in line[-1]:
          string = line[-1].split(',')
          for name in string:
            if not name in Register and not name in Label and not name.isdigit():
              if name.upper() in Register:
                print(f'輸入錯誤：第{index+1}行"{line[-1]}"，register "{name}" 必須為大寫英文字母\n建議修正：{name.upper()}\n')
                check = False
              if name.upper() in Label:
                print(f'輸入錯誤：第{index+1}行"{line[-1]}"，Label "{name}" 必須為大寫英文字母\n建議修正：{name.upper()}\n')
                check = False
        elif not line[-1].isdigit() and not line[-1] in Label and not line[-1] in Register and line[-1]!='*':
          if  not line[-1].upper() in Label and not line[-1].upper() in Register:
            output = ' '.join(line)
            print(f'輸入錯誤：第{index+1}行"{output}"，必須為數值、label或register\n')
            check = False
          else:
            output = ' '.join(line)
            print(f'警告：第{index+1}行"{output}"，請轉換成大寫\n建議修正：{line[-1].upper()}\n')

        # 7.START、RESW、RESB後面要是數字------------------------------------------------------------
        if line[-2] == 'START' or line[-2] == 'RESW' or line[-2] == 'RESB':
          if not line[-1].isdigit():
            output = ' '.join(line)
            print(f'輸入錯誤：第{index+1}行"{output}"，"{line[-2]}"後面必須連接數字\n')
            check = False
        # 8.EQU不能forward reference
        if line[-2].upper() == 'EQU':
          for id in range(index,len(array)):
            if line[-1] == array[id][0]:
              output = ' '.join(line)
              print(f'輸入錯誤：第{index+1}行"{output}"，EQU不能forward reference\n')

    # 9.開頭必須是START，結尾必須是END----------------------------------------------------
    line = array[0]
    if line[-2] != 'START':
      output = ' '.join(line)
      print(f'輸入錯誤：第1行"{output}"，開頭第一行必須要為"START"\n')
      check = False
    line = array[-1]
    if line[-2] != 'END':
      output = ' '.join(line)
      print(f'輸入錯誤：第{len(array)}行"{output}"，結尾最後一行必須要為"END"\n') 
      check = False

  if not check:
    return False
  else:
    return True