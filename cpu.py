"""CPU functionality."""
import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.PC = 0
        self.ram = [0] * 128
        self.flag = [0] * 8

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, value):
        self.ram[address] = value

    def load(self):
        """Load a program into memory."""

        if len(sys.argv) != 2:
            print("usage: ls8.py <filename>")
            sys.exit(1)

        try:
            address = 0
            with open(sys.argv[1]) as f:
                for line in f:
                    comment_split = line.split("#")
                    num = comment_split[0].strip()
                    if len(num) == 0:
                        continue
                    instruction = int(num, 2)
                    self.ram[address] = instruction
                    address += 1

        except FileNotFoundError:
            print(f"{sys.argv[0]}: {sys.argv[1]} not found")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.PC,
            self.ram_read(self.PC),
            self.ram_read(self.PC + 1),
            self.ram_read(self.PC + 2)
        ), end='')
        for i in range(8):
            print(" %02X" % self.reg[i], end='')
        print()

    def run(self):
        """Run the CPU."""
        # as the ram digits been converted to decimal
        LDI = 0b10000010
        MUL = 0b10100010
        PRN = 0b01000111
        HLT = 0b00000001
        PUSH = 0b01000101
        POP = 0b01000110
        SP = 7
        CALL = 0b01010000
        RET = 0b00010001
        ADD = 0b10100000
        CMP = 0b10100111
        JMP = 0b01010100
        JEQ = 0b01010101
        JNE = 0b01010110
        running = True

        while running:
            IR = self.ram[self.PC]
            operand_a = self.ram_read(self.PC + 1)
            operand_b = self.ram_read(self.PC + 2)
            if IR == HLT:
                print("Exiting...")
                running = False
            elif IR == LDI:
                self.reg[operand_a] = operand_b
                inc_size = 3
            elif IR == ADD:
                self.reg[operand_a] += self.reg[operand_b]
                inc_size = 3
            elif IR == MUL:
                self.reg[operand_a] *= self.reg[operand_b]
                inc_size = 3
            elif IR == PRN:
                print(self.reg[operand_a])
                inc_size = 2
            elif IR == PUSH:
                inc_size = 2
                val = self.reg[operand_a]
                self.reg[SP] -= 1
                self.ram[self.reg[SP]] = val
            elif IR == POP:
                inc_size = 2
                val = self.ram[self.reg[SP]]
                self.reg[operand_a] = val
                self.reg[SP] += 1
            elif IR == CALL:
                self.reg[SP] -= 1
                self.ram[self.reg[SP]] = self.PC + 2
                self.PC = self.reg[operand_a]
                inc_size = 0
            elif IR == RET:
                self.PC = self.ram[self.reg[SP]]
                self.reg[SP] += 1
                inc_size = 0
            elif IR == CMP:
                register_a = self.reg[self.ram[self.PC + 1]]
                register_b = self.reg[self.ram[self.PC + 2]]
                if register_a < register_b:
                    self.flag[5] = 1
                elif register_a > register_b:
                    self.flag[6] = 1
                elif register_a == register_b:
                    self.flag[7] = 1
                inc_size = 3
            elif IR == JMP:
                register_a = self.ram[self.PC + 1]
                self.PC = self.reg[register_a]
                inc_size = 0
            elif IR == JEQ:
                if self.flag[7] == 1:
                    register_a = self.ram[self.PC + 1]
                    self.PC = self.reg[register_a]
                    inc_size = 0
                else:
                    inc_size = 2
            elif IR == JNE:
                if self.flag[7] == 0:
                    register_a = self.ram[self.PC + 1]
                    self.PC = self.reg[register_a]
                    inc_size = 0
                else:
                    inc_size = 2
            else:
                print(f"Invalid instruction {IR}")
                sys.exit(1)
            self.PC += inc_size
