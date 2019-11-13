"""CPU functionality."""

import sys
HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010


# class Foo:

#     def __init__(self):
#         # Set up the branch table
#         self.branchtable = {
#             LDI: self.handle_LDI,
#             PRN: self.handle_PRN,
#             MUL: self.handle_MUL,
#             HLT: self.handle_HLT,
#         }

#     def handle_LDI(self):
#         operand_a = self.ram_read(self.pc+1)
#         operand_b = self.ram_read(self.pc+2)

#         self.reg[operand_a] = operand_b

#     def handle_PRN(self):
#         operand_a = self.ram_read(self.pc+1)
#         print(self.reg[operand_a])

#     def handle_MUL(self):
#         operand_a = self.ram_read(self.pc+1)
#         operand_b = self.ram_read(self.pc+2)

#         self.alu('MUL', operand_a, operand_b)

#     def handle_HLT(self):
#         halted = True

#     def run(self):
#         # Example calls into the branch table
#         halted = False

#         while not halted:
#             ir = self.ram_read(self.pc)
#             self.branchtable[ir]


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [00000000] * 32
        self.reg = [0] * 8
        self.pc = 0

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

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
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

    def run(self):
        """Run the CPU."""
        halted = False

        while not halted:
            ir = self.ram_read(self.pc)

            if ir == LDI:
                operand_a = self.ram_read(self.pc+1)
                operand_b = self.ram_read(self.pc+2)

                self.reg[operand_a] = operand_b

            elif ir == PRN:
                operand_a = self.ram_read(self.pc+1)
                print(self.reg[operand_a])

            elif ir == MUL:
                operand_a = self.ram_read(self.pc+1)
                operand_b = self.ram_read(self.pc+2)

                self.alu('MUL', operand_a, operand_b)

            elif ir == HLT:
                halted = True

            else:
                print(f"Unknown instruction at index {self.pc}")
                sys.exit(1)

            operand_count = ir >> 6
            instruction_length = operand_count + 1
            self.pc += instruction_length
            # print(self.pc)
