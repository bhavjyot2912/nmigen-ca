from typing import List

from nmigen import *
#from nmigen.sim import *
from nmigen.back.pysim import Simulator, Delay, Settle
from nmigen import Elaboratable, Module, Signal
from nmigen.build import Platform
from nmigen.cli import main_parser, main_runner


class Memory_stage(Elaboratable):
    def __init__(self):
        
        #input
        self.data_in = Signal(32) # data coming from decode stage which needs to be written to memory # input
        self.result = Signal(32)  # ALU ka result # input
        self.mem_imm = Signal(32)
        self.reg_addr_in = Signal(5) # write register address got from decode stage
        #reg_addr_in = reg_addr_out always
        
        self.inst_type = Signal(3)  # R, S, U etc.
        self.inst_type1 = Signal(11)  # 11 bit opcode + funct3 + funct7
        self.inst_type2 = Signal(10)  # 10 bit opcode + funct3
        self.inst_type3 = Signal(7)  # 7 bit opcode


        #intermediates
        self.address = Signal(32) # the address to be input in the Memory block, calculated in this stage itself
        self.zeroes24 = Signal(24)
        self.zeroes16 = Signal(16)
        #self.write = Signal(1)
        self.regfile = Array([Signal(32) for i in range(16)]) # 32x16 bits memory file
        
        #outputs
        self.reg_addr_out = Signal(5) # write register address to be passed on ahead to writeback
        self.data_copy = Signal(32) # passing the ALU result to the next stage in this variable
        self.data_out = Signal(32) # data output from memory after loads
        
        #instruction types
        self.R_type = 0b111
        self.I_type = 0b001
        self.S_type = 0b011
        self.B_type = 0b100
        self.U_type = 0b101
        self.J_type = 0b110
        

        self.LUI = 0b0110111
        self.AUIPC = 0b0010111
        self.JAL = 0b1101111
        
        self.JALB = 0b0001100111
        self.BEQ = 0b0001100011
        self.BNE = 0b0011100011
        self.BLT = 0b1001100011
        self.BGE = 0b1011100011
        self.BLTU = 0b1101100011
        self.BGEU = 0b1111100011
        self.LB = 0b0000000011
        self.LH = 0b0010000011
        self.LW = 0b0100000011
        self.LBU = 0b1000000011
        self.LHU = 0b1010000011
        self.SB = 0b0000100011
        self.SH = 0b0010100011
        self.SW = 0b0100100011
        self.ADDI = 0b0000010011
        self.SLTI = 0b0100010011
        self.SLTIU = 0b0110010011
        self.XORI = 0b1000010011
        self.ORI = 0b1100010011
        self.ANDI = 0b1110010011
        self.SLLI = 0b0010010011 #starting 1 bit removed
        self.SRLI = 0b1010010011 #starting 1 bit removed
        self.SRAI = 0b1010010011 #starting 1 bit removed
        
        self.ADD = 0b00000110011
        self.SUB = 0b10000110011
        self.SLL = 0b00010110011
        self.SLT = 0b00100110011
        self.SLTU = 0b00110110011
        self.XOR = 0b01000110011
        self.SRL = 0b01010110011
        self.SRA = 0b11010110011
        self.OR = 0b01100110011
        self.AND = 0b01110110011

    def elaborate(self, platform: Platform) -> Module:
        m = Module()
               
        with m.Switch(self.inst_type):
            with m.Case(self.I_type):
                with m.Switch(self.inst_type2):  
                    with m.Case(self.LB):
                        m.d.comb += self.address.eq(self.mem_imm+self.result)
                        m.d.sync += self.data_out.eq(Cat(self.zeroes24, self.regfile[self.address[0:7]]))
                        #m.d.sync += self.write.eq(0b0)
                        m.d.sync += self.reg_addr_out.eq(self.reg_addr_in)
                    with m.Case(self.LH):
                        m.d.comb += self.address.eq(self.mem_imm+self.result)
                        m.d.sync += self.data_out.eq(Cat(self.zeroes16, self.regfile[self.address[0:15]]))
                        #self.write = 0b0  
                        m.d.sync += self.reg_addr_out.eq(self.reg_addr_in)  
                    with m.Case(self.LW):
                        m.d.comb += self.address.eq(self.mem_imm+self.result)
                        #self.write = 0b0
                        m.d.sync += self.data_out.eq(self.regfile[self.address])
                        m.d.sync += self.reg_addr_out.eq(self.reg_addr_in)
                    with m.Case(self.LBU):
                        m.d.comb += self.address.eq(self.mem_imm+self.result)
                        m.d.sync += self.data_out.eq(Cat(Repl(self.regfile[self.address[31]], 24), self.regfile[self.address[0:7]]))
                        #self.write = 0b0
                        m.d.sync += self.reg_addr_out.eq(self.reg_addr_in)
                    with m.Case(self.LHU):
                        m.d.comb += self.address.eq(self.mem_imm+self.result)
                        #self.write = 0b0 
                        m.d.sync += self.data_out.eq(Cat(Repl(self.regfile[self.address[31]], 16), self.regfile[self.address[0:15]]))
                        m.d.sync += self.reg_addr_out.eq(self.reg_addr_in)
                        

                    with m.Case(self.SB):
                        m.d.comb += self.address.eq(self.mem_imm+self.result)
                        #self.write = 0b1
                        m.d.sync += self.regfile[self.address].eq(Cat(self.zeroes24, self.data_in[0:7]))
                    with m.Case(self.SH):
                        m.d.comb += self.address.eq(self.mem_imm+self.result)
                        #self.write = 0b1
                        m.d.sync += self.regfile[self.address].eq(Cat(self.zeroes16, self.data_in[0:15]))
                    with m.Case(self.SW):
                        m.d.comb += self.address.eq(self.mem_imm+self.result)
                        #self.write = 0b1
                        m.d.sync += self.regfile[self.address].eq(self.data_in)
                        
                    #other instructions in which memory block won't be used
                    with m.Case(self.ADDI):
                        m.d.sync += self.data_copy.eq(self.result)
                        #self.write = 0b0
                    with m.Case(self.SLTI):
                        m.d.sync += self.data_copy.eq(self.result)
                        #self.write = 0b0
                    with m.Case(self.SLTIU):
                        m.d.sync += self.data_copy.eq(self.result)
                        #self.write = 0b0
                    with m.Case(self.XORI):
                        m.d.sync += self.data_copy.eq(self.result)
                        #self.write = 0b0
                    with m.Case(self.ORI):
                        m.d.sync += self.data_copy.eq(self.result)
                        #self.write = 0b0
                    with m.Case(self.ANDI):
                        m.d.sync += self.data_copy.eq(self.result)
                        #self.write = 0b0
                    with m.Case(self.SLLI):
                        m.d.sync += self.data_copy.eq(self.result)
                        #self.write = 0b0
                    with m.Case(self.SRLI):
                        m.d.sync += self.data_copy.eq(self.result)
                        #self.write = 0b0
                    with m.Case(self.SRAI):
                        m.d.sync += self.data_copy.eq(self.result)
                        #self.write = 0b0
            
            #other instructions in which memory block won't be used
            with m.Case(self.R_type): 
                with m.Switch(self.inst_type1): 
                    with m.Case(self.ADD):
                        m.d.sync += self.data_copy.eq(self.result)
                        #self.write = 0b0
                    with m.Case(self.SUB):
                        m.d.sync += self.data_copy.eq(self.result)
                        #self.write = 0b0
                    with m.Case(self.SLL):
                        m.d.sync += self.data_copy.eq(self.result)
                        #self.write = 0b0
                    with m.Case(self.SLT):
                        m.d.sync += self.data_copy.eq(self.result)
                        #self.write = 0b0
                    with m.Case(self.SLTU):
                        m.d.sync += self.data_copy.eq(self.result)
                        #self.write = 0b0
                    with m.Case(self.XOR):
                        m.d.sync += self.data_copy.eq(self.result)
                        #self.write = 0b0
                    with m.Case(self.SRL):
                        m.d.sync += self.data_copy.eq(self.result)
                        #self.write = 0b0
                    with m.Case(self.SRA):
                        m.d.sync += self.data_copy.eq(self.result)
                        #self.write = 0b0
                    with m.Case(self.OR):
                        m.d.sync += self.data_copy.eq(self.result)
                        #self.write = 0b0
                    with m.Case(self.AND):
                        m.d.sync += self.data_copy.eq(self.result)
                        #self.write = 0b0                
        return m   
    
    def ports(self)->List[Signal]:
        return [
            self.data_in,
            self.mem_imm,
            self.result,
            self.address,
            self.reg_addr_in,
            self.inst_type,
            self.inst_type1,
            self.inst_type2,
            self.inst_type3,
            self.zeroes16,
            self.zeroes24,
            self.regfile,
            self.reg_addr_out,
            self.data_out,
            self.data_copy,
            ]
            
if __name__ == "__main__":
    parser = main_parser()
    args = parser.parse_args()

    m = Module()
    m.domains.sync = sync = ClockDomain("sync", async_reset=True)
    m.submodules.memory_stage = memory_stage  = Memory_stage()
    
    
    data_in = Signal(32) # data written to memory
    result = Signal(32)  # ALU ka result
    mem_imm = Signal(32)
    reg_addr_in = Signal(5) # write register address to be passed on ahead
    
    inst_type = Signal(3)  # R, S, U etc.
    inst_type1 = Signal(11)  # 11 bit opcode + funct3 + funct7
    inst_type2 = Signal(10)  # 10 bit opcode + funct3
    inst_type3 = Signal(7)  # 7 bit opcode

    regfile = Array([Signal(32) for i in range(16)])
    zeroes24 = Signal(24)
    zeroes16 = Signal(16)
    address = Signal(32)

    m.d.sync +=memory_stage.address.eq(address)
    m.d.sync += memory_stage.zeroes24.eq(zeroes24)
    m.d.sync += memory_stage.zeroes16.eq(zeroes16)    
    for i in range(16):
        m.d.sync += memory_stage.regfile[i].eq(regfile[i])
    
    m.d.sync += memory_stage.data_in.eq(data_in)
    m.d.sync += memory_stage.result.eq(result)
    m.d.sync += memory_stage.mem_imm.eq(mem_imm)
    m.d.sync += memory_stage.reg_addr_in.eq(reg_addr_in)
    
    m.d.sync += memory_stage.inst_type.eq(inst_type)
    m.d.sync += memory_stage.inst_type1.eq(inst_type1)
    m.d.sync += memory_stage.inst_type2.eq(inst_type2)
    m.d.sync += memory_stage.inst_type3.eq(inst_type3)
    
    
    sim = Simulator(m)
    sim.add_clock(1e-6, domain="sync")

    def process():
        yield regfile[1].eq(0x00000001)
        yield regfile[2].eq(0x00000002)
        yield regfile[3].eq(0x00000003)
        yield regfile[4].eq(0x00000004)
        yield regfile[5].eq(0x00000005)
        yield regfile[6].eq(0x00000006)
        

        yield zeroes24.eq(0x000000)
        yield zeroes16.eq(0x0000)
        
        yield data_in.eq(0x00000004)
        yield result.eq(0x00000005)
        yield mem_imm.eq(0x00000001)
        yield reg_addr_in.eq(0b00001)
        
        yield inst_type.eq(0b001)        
        yield inst_type2.eq(0b0100000011) # load word is the instruction here
        
        #yield Delay(1e-6)


sim.add_sync_process(process,domain = "sync")

with sim.write_vcd("test_1.vcd","test_1.gtkw",traces=[data_in, mem_imm, result, reg_addr_in, inst_type, inst_type1, inst_type2, inst_type3]+memory_stage.ports()):
    sim.run_until(100e-6, run_passive=True)                              
                                                    

#[data_in, mem_imm, result, reg_addr, inst_type, inst_type1, inst_type2, inst_type3]
                            
                                                        
                        
 #m.d.sync += mem[addr].eq(data)
     #m.d.sync += data_out.eq(mem[addr])                                           
                            
                        
                            
                            
                                    
                                       