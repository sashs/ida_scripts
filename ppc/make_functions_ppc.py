# Looks for stwu r1 instructions and create a function unless this instruction is in a function
# arch: ppc
# fileformat: ELF

current_address = ScreenEA()

start = SegStart(current_address)
end = SegEnd(current_address)
old_start = None

while start < end and (start != old_start):
    old_start = start
    for instruction in Heads(start, end):

        func_start = FirstFuncFchunk(instruction)
        if func_start == BADADDR:
            if GetMnem(instruction) == 'stwu' and GetOpnd(instruction,0) == 'r1':
                print "Make function for Address", hex(instruction)
                MakeFunction(instruction, BADADDR)
        else:
            start = FindFuncEnd(instruction)
            break

print 'End!'
