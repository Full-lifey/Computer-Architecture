"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110
AND = 0b10101000
OR = 0b10101010
XOR = 0b10101011
NOT = 0b01101001
SHL = 0b10101100
SHR = 0b10101101
MOD = 0b10100100


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [00000000] * 255
        self.reg = [0] * 8
        self.pc = 0
        self.halted = False
        self.SP = 7
        self.reg[self.SP] = 0xF3
        self.FL = 0b00000000

        self.branchtable = {}
        self.branchtable[HLT] = self.handle_hlt
        self.branchtable[LDI] = self.handle_ldi
        self.branchtable[PRN] = self.handle_prn
        self.branchtable[MUL] = self.handle_mul
        self.branchtable[PUSH] = self.handle_push
        self.branchtable[POP] = self.handle_pop
        self.branchtable[CALL] = self.handle_call
        self.branchtable[RET] = self.handle_ret
        self.branchtable[ADD] = self.handle_add
        self.branchtable[CMP] = self.handle_cmp
        self.branchtable[JMP] = self.handle_jmp
        self.branchtable[JEQ] = self.handle_jeq
        self.branchtable[JNE] = self.handle_jne
        self.branchtable[AND] = self.handle_and
        self.branchtable[OR] = self.handle_or
        self.branchtable[XOR] = self.handle_xor
        self.branchtable[NOT] = self.handle_not
        self.branchtable[SHL] = self.handle_shl
        self.branchtable[SHR] = self.handle_shr
        self.branchtable[MOD] = self.handle_mod

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def load(self, program):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]

        for instruction in program:
            number = int(instruction, 2)
            self.ram[address] = number
            address += 1

    def alu(self, op, reg_a, reg_b=None):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            result = reg_a - reg_b

            if result < 0:
                self.FL = 0b00000100
            elif result > 0:
                self.FL = 0b00000010
            else:
                self.FL = 0b00000001
        elif op == "AND":
            self.reg[reg_a] = self.reg[reg_a] & self.reg[reg_b]
        elif op == "OR":
            self.reg[reg_a] = self.reg[reg_a] | self.reg[reg_b]
        elif op == "XOR":
            self.reg[reg_a] = self.reg[reg_a] ^ self.reg[reg_b]
        elif op == "NOT":
            self.reg[reg_a] = ~ self.reg[reg_a]
        elif op == "SHL":
            self.reg[reg_a] = self.reg[reg_a] << self.reg[reg_b]
        elif op == "SHR":
            self.reg[reg_a] = self.reg[reg_a] >> self.reg[reg_b]
        elif op == "MOD":
            self.reg[reg_a] /= self.reg[reg_b]

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def handle_ldi(self):
        operand_a = self.ram_read(self.pc+1)
        operand_b = self.ram_read(self.pc+2)

        self.reg[operand_a] = operand_b

    def handle_prn(self):
        operand_a = self.ram_read(self.pc+1)
        print(self.reg[operand_a])

    def handle_hlt(self):
        self.halted = True

    def handle_mul(self):
        operand_a = self.ram_read(self.pc+1)
        operand_b = self.ram_read(self.pc+2)

        self.alu('MUL', operand_a, operand_b)

    def handle_add(self):
        operand_a = self.ram_read(self.pc+1)
        operand_b = self.ram_read(self.pc+2)

        self.alu("ADD", operand_a, operand_b)

    def handle_push(self):
        operand_a = self.ram_read(self.pc+1)
        self.reg[self.SP] -= 1

        self.ram_write(self.reg[self.SP], self.reg[operand_a])

    def handle_pop(self):
        operand_a = self.ram_read(self.pc+1)
        self.reg[operand_a] = self.ram_read(self.reg[self.SP])

        self.reg[self.SP] += 1

    def handle_call(self):
        # # push address of next instruction to stack
        return_address = self.pc+2
        # print(return_address)
        self.reg[self.SP] -= 1
        self.ram_write(self.reg[self.SP], return_address)

        # # set the pc to the value in the register
        # print(self.reg[self.SP])
        reg_num = self.reg[self.ram_read(self.pc+1)]
        # print(reg_num)
        self.pc = reg_num

    def handle_ret(self):
        # pop the return address off the stack
        # store it in the pc
        # print(self.reg[self.SP])
        self.pc = self.ram_read(self.reg[self.SP])
        self.reg[self.SP] += 1

    def handle_cmp(self):
        operand_a = self.reg[self.ram_read(self.pc+1)]
        operand_b = self.reg[self.ram_read(self.pc+2)]

        self.alu("CMP", operand_a, operand_b)

    def handle_jmp(self):
        # jump to the address stored in the given register
        # print(self.reg[self.ram_read(self.pc+1)])
        self.pc = self.reg[self.ram_read(self.pc+1)]

    def handle_jeq(self):
        operand_a = self.reg[self.ram_read(self.pc+1)]

        if self.FL == 1:
            self.pc = operand_a
        else:
            self.pc += 2

    def handle_jne(self):
        operand_a = self.reg[self.ram_read(self.pc+1)]

        # mask FL to see if JUST equal bit is 0
        FL_mask = self.FL & 0b00000001

        if FL_mask == 0:
            self.pc = operand_a
        else:
            self.pc += 2

    def handle_and(self):
        operand_a = self.ram_read(self.pc+1)
        operand_b = self.ram_read(self.pc+2)

        self.alu("AND", operand_a, operand_b)

    def handle_or(self):
        operand_a = self.ram_read(self.pc+1)
        operand_b = self.ram_read(self.pc+2)

        self.alu("OR", operand_a, operand_b)

    def handle_xor(self):
        operand_a = self.ram_read(self.pc+1)
        operand_b = self.ram_read(self.pc+2)

        self.alu("XOR", operand_a, operand_b)

    def handle_not(self):
        operand_a = self.ram_read(self.pc+1)

        self.alu("NOT", operand_a)

    def handle_shl(self):
        operand_a = self.ram_read(self.pc+1)
        operand_b = self.ram_read(self.pc+2)

        self.alu("SHL", operand_a, operand_b)

    def handle_shr(self):
        operand_a = self.ram_read(self.pc+1)
        operand_b = self.ram_read(self.pc+2)

        self.alu("SHR", operand_a, operand_b)

    def handle_mod(self):
        operand_a = self.ram_read(self.pc+1)
        operand_b = self.ram_read(self.pc+2)

        if operand_b == 0:
            self.halted = True
        else:
            self.alu("MOD", operand_a, operand_b)

    def run(self):
        """Run the CPU."""
        # SP = 7
        # self.reg[SP] = 0xF3

        while not self.halted:
            ir = self.ram_read(self.pc)
            if ir == 0 or None:
                print(f"Unknown instruction at index {self.pc}")
                sys.exit(1)

            self.branchtable[ir]()

            # if ir == LDI:
            #     operand_a = self.ram_read(self.pc+1)
            #     operand_b = self.ram_read(self.pc+2)

            #     self.reg[operand_a] = operand_b

            # elif ir == PRN:
            #     operand_a = self.ram_read(self.pc+1)
            #     print(self.reg[operand_a])

            # elif ir == MUL:
            #     operand_a = self.ram_read(self.pc+1)
            #     operand_b = self.ram_read(self.pc+2)

            #     self.alu('MUL', operand_a, operand_b)

            # elif ir == PUSH:
            #     operand_a = self.ram_read(self.pc+1)
            #     self.reg[SP] -= 1

            #     self.ram_write(self.reg[SP], self.reg[operand_a])

            # elif ir == POP:
            #     operand_a = self.ram_read(self.pc+1)
            #     self.reg[operand_a] = self.ram_read(self.reg[SP])

            #     self.reg[SP] += 1

            # elif ir == HLT:
            #     halted = True

            # elif ir == CALL:
            #     pass
            #     # push address of next instruction to stack
            #     # set the pc to the value in the register

            # elif ir == RET:
            #     # pop the return address of the stack
            #     # store it in the pc

            mask = ir & 0b00010000
            c_bit = mask >> 4

            if c_bit != 1:
                # print('counting', self.pc)
                operand_count = ir >> 6
                instruction_length = operand_count + 1
                self.pc += instruction_length
            # else:
                # print(self.pc)
