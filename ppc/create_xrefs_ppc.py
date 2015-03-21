# Looks for relativ access to resources where the reg r30 is used and create a xref to this resource
# arch: ppc
import struct

neg = lambda x: struct.unpack('i', struct.pack('I', x))[0]


ea = ScreenEA()
names = {}
r30 = 0
names = {}
for func_ea in Functions(SegStart(ea), SegEnd(ea)):
    func_name = GetFunctionName(func_ea)
    instructions = Heads(func_ea, FindFuncEnd(func_ea))
    r30_is_set = False
    for inst in instructions:
        mnem = GetMnem(inst)

        # Look for the instruction which set r30 and then set the r30 variable
        if mnem == 'addi' and GetOpnd(inst, 0) == 'r30' and GetOpnd(inst, 1) == 'r30':
            r30 = Dfirst(inst)
            r30_is_set = r30 != BADADDR

        # Look for a loading instruction which uses r30. To go here r30 has to be set
        elif r30_is_set and mnem == 'lwz' and '(r30)' in GetOpnd(inst, 1) :
            if Dfirst(inst) == BADADDR:
                offset = GetOperandValue(inst, 1) & 0xFFFFFFFF

                # Make a negative value
                if offset > 0x7FFFFFFF:
                    offset -= 0x100000000

                # Looks for the xref of this got entry to get this name
                real_value = Dfirst(r30 + offset)
                if real_value != BADADDR:

                    name = Name(real_value)


                    if name:
                        count = names.get(name,-1)
                        count += 1
                        names[name] = count

                        while not MakeName(r30 + offset, 'dat_'+name + '_'+str(count) ):
                            count += 1
                            names[name] = count

                # If there is no xref a pseudo name is created
                elif not Name(r30 + offset):
                    MakeName(r30 + offset, 'dat_'+(hex(r30+offset)[2:-1]) )

                print "Create XREF from", hex(inst), 'to', hex(r30 + offset)

                add_dref(inst, r30 + offset, dr_R)


print 'End!'
