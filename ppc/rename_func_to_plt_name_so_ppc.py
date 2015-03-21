# Renames the wrapper functions for library calls to the function which is called and add a xref to this function
# arch: ppc
# fileformat: ELF

import struct

names = {}

neg = lambda x: struct.unpack('i', struct.pack('I', x))[0]
x86 = lambda x: x & 0xFFFFFFFF

def is_addi_r30(addr):
    return GetMnem(addr) == 'addi' and GetOpnd(addr, 0) == 'r30' and GetOpnd(addr, 1) == 'r30'

def find_addi_r30(xref_pos, xref_func_addr):
    if xref_func_addr == BADADDR or xref_func_addr > xref_pos:
        while True:
            inst = PrevHead(xref_pos)
            if is_addi_r30(inst):
                return inst
            xref_pos = inst
    else:
        for inst in Heads(xref_func_addr, xref_pos):
            if is_addi_r30(inst):
                return inst
    print 'Cannot find addi r30'


def handle_xref(xref_pos, xref_func_addr, func_to_rename, offset):
    global names

    # if the instruction is addi r30 then this is the calculation of the baseaddr of the got
    print hex(xref_pos), hex(xref_func_addr)
    instruction = find_addi_r30(xref_pos, xref_func_addr)
    if instruction:
        baseaddr = Dfirst(instruction)
        called_func = baseaddr + offset
        # get the name for renaming
        name = Name(called_func)

        # try to demangle if it is a C++ method
        demangled_name = Demangle(name, GetLongPrm(INF_SHORT_DN))
        if demangled_name:
            name = demangled_name
        if name.startswith('.'):
            name = name[1:]

        # Name counter because there are many wrapper function for a library function call
        count = names.get(name, -1)
        count +=1
        names[name] = count

        # try to set a name, if it is not successful increase the counter and try again
        while not MakeName(func_to_rename,'call_'+name+'_'+str(count)):
            count += 1
        else:
            names[name] = count
        print "New name:", 'call_'+name+'_'+str(count)
        # add xref for better navigation
        add_dref(func_to_rename, called_func, dr_R)

def look_for_xref(func_start_address):
    """Looks for a xref which is in a function"""
    xref_pos = RfirstB(func_start_address)
    xref_func = FirstFuncFchunk(xref_pos)
    if xref_func == BADADDR:
        while xref_func == BADADDR and xref_pos != BADADDR:
            xref_pos = RnextB(func_start_address, xref_pos)
            xref_func = FirstFuncFchunk(xref_pos)

    return (xref_pos, xref_func)

def handle_function(func_name, func_start_address):
    instructions = Heads(func_start_address, FindFuncEnd(func_start_address))

    # if instruction is addis, we need the first two instructions
    instruction = [instructions.next()]
    if GetMnem(instruction[0]) == 'addis':
        instruction.append(instructions.next())

    if isCode(GetFlags(instruction[0])):
        # if the first instruction is lwz reg, offs(r30) or
        # the first two instructions are addis reg, r30, <i> and lwz reg, offs(r30)
        if (GetMnem(instruction[0]) == 'lwz' and 'r30' in GetOpnd(instruction[0], 1)) \
         or (GetMnem(instruction[0]) == 'addis' and GetOpnd(instruction[0], 1) == 'r30' \
         and GetMnem(instruction[1]) == 'lwz'):

            print "Try to rename function:", func_name

            # if the first instruction is addis, we need to add this value to offset
            if GetMnem(instruction[0]) == 'addis':
                addis_value = GetOperandValue(instruction[0],2)
                offset = neg(x86(GetOperandValue(instruction[1],1)))
                offset += (addis_value << 16)
            else:
                offset = neg(x86(GetOperandValue(instruction[0],1)))

            xref_pos, xref_func = look_for_xref(func_start_address)
            if xref_pos == BADADDR:
                print "Cannot rename function (no xref):", func_name
                return
            handle_xref(xref_pos, xref_func, instruction[0], offset)


ea = ScreenEA()

for func_ea in Functions(SegStart(ea), SegEnd(ea)):
    func_name = GetFunctionName(func_ea)
    if func_name.startswith('sub_'):
        handle_function(func_name, func_ea)

print 'End!'
