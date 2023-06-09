COPY        START       0
FIRST       sTL         RETADD
            LDB         #LENGTH
            BASE        LENGTH
CLOOP       +JUMP       RDREC
            LDA         LENGTH
            COMP        #0
            JEQ         ENDFIL
            JSUB        WRREC
            J           CLOOB
ENDFIL      LDA         EOF
            STA         BUFFER
            LDA         #3
            STA         LENGTH
            JSUB        WRREC
            J           @RETADR
EOF         BYTE        C'EOF'
RETADR      RESW        1
LENGTH      RESW        1
BUFFER      RESB        4096
BUFEND      EQU         *
MAXLEN      EQU         BUFEND-BUFFER
.
.   SUBROUTINE RDREC
.
RDREC       CLEAR       X
            CLEAR       a
            CLEAR       S
            LDT         #MAXLEN
RLOOP       TD          INPUT
            JEQ         RLOOP
            RD          INPUT
            COMIC       A,S
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
            JEQ         WLOOP
            LDCH        BUFFER,X
            WD          output
            TIXR        T
            JLT         WLoop
REF         LDA         WLoop+13
            RSUB
OUTPUT      BYTE        X'05'
            END         FIRST