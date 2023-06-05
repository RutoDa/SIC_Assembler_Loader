# @title 這個沒有說明(方便複製)
COPY        STL         0           
COPY        START       0
FIRST       STL         RETADR
Ldb         #LENGTH
BASE        LENGTH
CLOOP       +JSub       RDREC
LDA         LENGTH
COMP        #0
JEQ         ENDFIL
+JSUB       WRREC
J           CLOOP
ENDFIL      LDA         EOF
STA         BUFFER
LDA         #3
STA         LENGTH
+JSUB       WRREC
J           @RET
EOF         BYTE        c'EOF'
RETADR      RESW        1
LENGTH      RESW        1
BUFFER      RESB        a4096
BUFEND      Equ         *
MAXLEN      EQU         BUFEND-BUFFER
TEST        EQU         EXIT
.
.   SUBROUTINE RDREC
.
RDREC       CLEAR       X
CLEAR       A
CLEAR       S
+LDT        #MAXLEN
RLOOP       TD          INPUT
JEQ         RLOOP
RD          INPUT
COMPR       a,S
JEQ         EXIT
STCH        BUFFER,X
TIXR        T
JLT         RLoop
EXIT        STX         LENGTH
RSUB
INPUT       BYTE        X'F1'
.
.   SUBROUTINE WRREC
.
WRREC       CLEAR       X
LDT         LENGTH
WLOOP       TD          OUTPUT
JEG         WLOOP
LDCH        BUFFER,X
WD          output
TIXR        #T
JLT         WLoop
REF         LDA         WLoop+13
RSUB
OUTPUT      BYTE        Q'05'
END         FIRST
STL         FIRST