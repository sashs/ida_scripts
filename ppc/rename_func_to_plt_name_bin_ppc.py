# Renames the wrapper functions for library calls to the function which is called and add a xref to this function
# arch: ppc
# fileformat: ELF

import struct

names = {}

neg = lambda x: struct.unpack('i', struct.pack('I', x))[0]
x86 = lambda x: x & 0xFFFFFFFF


def handle_function(func_name, func_start_address):
    instructions = Heads(func_start_address, FindFuncEnd(func_start_address))

    inst_lis = instructions.next()
    inst_lwz = instructions.next()

    if isCode(GetFlags(inst_lis)):

        if GetMnem(inst_lis) == 'lis' and  GetMnem(inst_lwz) == 'lwz':

            print "Renaming function:", func_name
            print hex(GetOperandValue(inst_lis,1))
            print hex(GetOperandValue(inst_lwz,1))
            addr = (GetOperandValue(inst_lis,1) << 16) + GetOperandValue(inst_lwz,1)
            print addr
            name = Name(addr)
            demangled_name = Demangle(name, GetLongPrm(INF_SHORT_DN))
            if demangled_name:
                name = demangled_name
            if name.startswith('.'):
                name = name[1:]

            count = names.get(name, -1)
            count +=1
            names[name] = count

            # try to set a name, if it is not successful increase the counter and try again
            while not MakeName(func_start_address,'call_'+name+'_'+str(count)):
                count += 1
            else:
                names[name] = count
            print "New name:", 'call_'+name+'_'+str(count)


ea = ScreenEA()

for func_ea in Functions(SegStart(ea), SegEnd(ea)):
    func_name = GetFunctionName(func_ea)
    if func_name.startswith('sub_'):
        handle_function(func_name, func_ea)

print 'End!'
