from sicasm_package.OPTAB import *
from sicasm_package.AssemblerDirectives import *

def pass1(file_name):
  LOC = 0
  SYMTAB = {}
  Inter_file = [] 

  with open(file_name, 'r') as f:
    line = f.readline()
    while line:
      temp = line.split()  #切割輸入內容
      if temp == []:
          line = f.readline()
          continue
      
      place1 = temp[0]    
      line = line.strip()  #去除句尾的\n

      #判斷切割後的輸入長度
      if len(temp) == 3:

        if temp[1] == 'START':
          LOC = int(temp[2])
          SYMTAB[temp[0]] =  '{:0>4X}'.format(LOC) # 將LOC轉成hex四碼靠右對齊的字串，將檔名寫入SYMTAB
          Program_name = temp[0]
          Inter_file.append('{:0>4X}'.format(LOC) +' '+ line)
          
        else:
          if temp[0] != '.': #判斷是否為註解
            if temp[1] not in Assembler_directives and temp[0] not in SYMTAB:
              LOC = int(LOC)
              SYMTAB[temp[0]] = '{:0>4X}'.format(LOC)

              Inter_file.append('{:0>4X}'.format(LOC) +' '+ line)

            if temp[1][0] == '+' and temp[1][1:] in OPTAB: #若operator為 Format 4
              LOC += 4

            if temp[1] in OPTAB:  
              if temp[1][-1] == 'R': # operator為 Format 2
                LOC += 2
              else:
                LOC += 3 
            #處理資料的宣告
            elif temp[1] == 'BYTE':
              #抓取兩個分號，如: C'EOF'
              first_quote = temp[2].find('\'')
              second_quote = temp[2].find('\'', first_quote+1)

              #取分號中的內容
              trimed_str = temp[2][first_quote+1:second_quote]

              
              Inter_file.append('{:0>4X}'.format(LOC) +' '+ line)

              
              SYMTAB[temp[0]] = '{:0>4X}'.format(LOC)
              #若為"C"則1個字元1個byte, "X"則2位數1個byte
              LOC += len(trimed_str) if temp[2][0] == 'C' else len(trimed_str)//2 
            
            elif temp[1] == 'RESB':
              
              Inter_file.append('{:0>4X}'.format(LOC) +' '+ line)
              SYMTAB[temp[0]] = '{:0>4X}'.format(LOC)
              LOC += int(temp[2])

            elif temp[1] == 'WORD':
              
              Inter_file.append('{:0>4X}'.format(LOC) +' '+ line)
              SYMTAB[temp[0]] = '{:0>4X}'.format(LOC)
              LOC += 3

            elif temp[1] == 'RESW':
              
              Inter_file.append('{:0>4X}'.format(LOC) +' '+ line)
              SYMTAB[temp[0]] = '{:0>4X}'.format(LOC)
              LOC += int(temp[2]) * 3

            elif temp[1] == 'EQU':
              if temp[2] == '*':
                LOC = int(LOC)
                
                Inter_file.append('{:0>4X}'.format(LOC) +' '+ line)
                
                SYMTAB[temp[0]] =  '{:0>4X}'.format(LOC)
              
              else: # Handle expression

                subtract, add = -1, -1
                subtract = temp[2].find('-')
                add = temp[2].find('+')

                operator_num = temp[2].count('-')  + temp[2].count('+')

                if operator_num == 1: #處理運算式僅有2運算元的情況
                  if subtract != -1:

                    #抓運算元
                    op1 = temp[2][:subtract]
                    op2 = temp[2][subtract+1:]

                    if op1 in SYMTAB and op2 in SYMTAB:    #2者皆為symbol
                      res = int(SYMTAB[op1], 16) - int(SYMTAB[op2], 16) 
                      SYMTAB[temp[0]] = '{:0>4X}'.format(res)
                        

                    elif op1.isnumeric() == True and op2.isnumeric() == True: #2者皆為為數值
                      res = int(op1) - int(op2)
                      SYMTAB[temp[0]] = '{:0>4X}'.format(res)

                    elif op1.isnumeric() == True:        # A - R (不合法表示式)
                        res = int(op1) - int(SYMTAB[op2], 16)
                        SYMTAB[temp[0]] = '{:0>4X}'.format(res)
                    else:
                        res = int(SYMTAB[op1], 16) - int(op2) # R - A
                        SYMTAB[temp[0]] =  '{:0>4X}'.format(res)
                    
                    Inter_file.append('{:0>4X}'.format(res) +' '+ line)

                  elif add != -1:
                    op1 = temp[2][:add]
                    op2 = temp[2][add+1:]

                    if op1 in SYMTAB and op2 in SYMTAB:        # 需判斷表示式正確性   
                      res = int(SYMTAB[op1], 16) + int(SYMTAB[op2], 16)
                      SYMTAB[temp[0]] = '{:0>4X}'.format(res)
                    
                    elif op1.isnumeric() == True and op2.isnumeric() == True:
                      res = int(op1) + int(op2)
                      SYMTAB[temp[0]] = '{:0>4X}'.format(res)
                    
                    elif op1.isnumeric() == True:
                      res = int(op1) + int(SYMTAB[op2], 16)
                      SYMTAB[temp[0]] =  '{:0>4X}'.format(res)

                    else:
                      res = int(SYMTAB[op1], 16) + int(op2)
                      SYMTAB[temp[0]] = '{:0>4X}'.format(res)

                    Inter_file.append('{:0>4X}'.format(res) +' '+ line)

                else:  #表示式有多個運算元
                  
                  res = 0
                  op1 = ''
                  op2 = ''
                  buf = ''
                  operator = ''
                  

                  for character in temp[2]:
                    if character == ' ': #略過空字元
                      pass
                    elif character != '+' and character != '-': #逐字讀取運算元名稱
                      buf += character
                    else:
                      if op1 == '': #將運算元名稱存入空的暫存
                        op1 = buf
                        buf = ''
                      elif op2 == '':
                        op2 = buf
                        buf = ''

                      if op1 != '' and op2 != '' and operator != '': # 3項皆不為空時，開始計算
                        
                          if operator == '+':       #需判斷表示式正確性
                            if op1.isnumeric() == True and op2.isnumeric() == True:
                              res += (int(op1) + int(op2))

                            elif op1.isnumeric() == True and op2 in SYMTAB:
                              res += (int(op1) + int(SYMTAB[op2], 16))
                              
                            
                            elif op1 in SYMTAB and op2.isnumeric() == True:
                              res += (int(SYMTAB[op1], 16) + int(op2))
                              
                            else:
                              res += (int(SYMTAB[op1], 16) + int(SYMTAB[op2], 16))
                              

                            op1 = str(res)
                            op2 = ''
                            operator = ''
                            res = 0

                          elif operator == '-':  #需判斷表示式正確性
                            if op1 in SYMTAB and op2 in SYMTAB:
                              res += (int(SYMTAB[op1], 16) - int(SYMTAB[op2], 16)) 
                              
                                #SYMTAB[temp[0]] = 'A ' + '{:0>4X}'.format(res)

                            elif op1.isnumeric() == True and op2.isnumeric() == True:
                              res += (int(op1) - int(op2))

                            elif op1.isnumeric() == True:
                                res += (int(op1) - int(SYMTAB[op2], 16))
                                
                            else:
                              res += (int(SYMTAB[op1], 16) - int(op2))
                              

                            op1 = str(res)
                            op2 = ''
                            operator = ''
                            res = 0

                      operator = character

                  op2 = buf #處理最後一輪計算
                  
                  if operator ==  '+':   #需判斷表示式正確性
                    if op1.isnumeric() == True and op2.isnumeric() == True:
                      res += (int(op1) + int(op2))

                    elif op1.isnumeric() == True and op2 in SYMTAB:
                      res += (int(op1) + int(SYMTAB[op2], 16))
                      
                    
                    elif op1 in SYMTAB and op2.isnumeric() == True:
                      res += (int(SYMTAB[op1], 16) + int(op2))
                      
                    else:
                      res += (int(SYMTAB[op1], 16) + int(SYMTAB[op2], 16))

                    op1 = ''
                    op2 = ''
                    operator = ''
                

                  elif operator == '-':  #需判斷表示式正確性
                    if op1 in SYMTAB and op2 in SYMTAB:
                      res += (int(SYMTAB[op1], 16) - int(SYMTAB[op2], 16))
                    
                        #SYMTAB[temp[0]] = 'A ' + '{:0>4X}'.format(res)

                    elif op1.isnumeric() == True and op2.isnumeric() == True:
                      res += (int(op1) - int(op2))

                    elif op1.isnumeric() == True:
                      res += (int(op1) - int(SYMTAB[op2], 16))  #需修改，依據R, S判斷
                    else:
                      res += (int(SYMTAB[op1], 16) - int(op2))
                      
                    op1 = ''
                    op2 = ''
                    operator = ''

                  Inter_file.append('{:0>4X}'.format(res) +' '+ line)
                  SYMTAB[temp[0]] =  '{:0>4X}'.format(res)
                  res = 0
                  

          else: # copy comment 
            Inter_file.append('{:0>4X}'.format(LOC) +' '+ line)
      #輸入長度為2  
      elif len(temp) == 2:
        #處理註解
        if temp[0] == '.':
          Inter_file.append('{:0>4X}'.format(LOC) +' '+ line)
          
        #opcode為format 4  
        elif place1[0] == '+':
          t = place1[1:]
          if t in OPTAB:
            Inter_file.append('{:0>4X}'.format(LOC) +' '+ line)
            LOC += 4
        elif place1 in OPTAB:
          # Format 2
          if place1[-1] == 'R':
            Inter_file.append('{:0>4X}'.format(LOC) +' '+ line)
            LOC += 2 
          else:
            Inter_file.append('{:0>4X}'.format(LOC) +' '+ line)
            LOC += 3
          #處理BASE和END directive  
        elif temp[0] == 'BASE':
          Inter_file.append('{:0>4X}'.format(LOC) + ' ' + line)
          
        elif temp[0] == 'END':
          Inter_file.append('{:0>4X}'.format(LOC) + ' ' + line)
          
        else:
          Inter_file.append('{:0>4X}'.format(LOC) +' '+ line)
          LOC += 3

      #輸入長度為1
      else:
        #處理註解
        if temp[0] == '.':
          Inter_file.append('{:0>4X}'.format(LOC) +' '+ line)
          
        elif temp[0] == 'JSUB' or temp[0] == 'RSUB':
          Inter_file.append('{:0>4X}'.format(LOC) +' '+ line)
          LOC += 3
      
      line = f.readline()
  return Inter_file, SYMTAB , Program_name