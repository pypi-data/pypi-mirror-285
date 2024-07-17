from typing import Sequence
import dis
import types
from collections.abc import Iterator
import inspect
from opcode import HAVE_ARGUMENT

class InstructionOperationIterator(Iterator):
    def __init__(self, iterable):
        self.__iterator = iterable.__iter__()
    def __iter__(self):
        return self
    def __next__(self):
        instructions = self.__iterator.__next__()
        return instructions.opcode, instructions.arg

def instructions_to_bytecode(instructions: Sequence[dis.Instruction]):
    return reverse_opargs(InstructionOperationIterator(instructions))

def reverse_opargs(op_arg_arr):
    code = bytearray()
    for op, arg in op_arg_arr:
        if op < HAVE_ARGUMENT:
            # For opcodes without an argument, add only the op
            arg = 0
        else:
            # For opcodes with an argument, handle potential extended arguments
            while arg > 255:
                arg = arg & 0xff  # Keep only the lower byte for the final argument
        code.extend([op, arg])
    return bytes(code)

def _find_super_init_pairs(bytecode):
    pairs = []
    init_index = None  # Track the index of the last seen __init__
    for i, instr in enumerate(bytecode):
        if instr.argval == '__init__' and bytecode[i - 2].argval == 'super':
            init_index = i # Found an __init__, remember its index
        # Check if this is a POP_TOP and we have seen an __init__ before it
        if instr.opname == 'POP_TOP' and init_index is not None:
            # Ensure the POP_TOP is after the __init__
            if i > init_index:
                pairs.append((init_index - 2, i + 1))
                init_index = None  # Reset init_index for the next pair
    return pairs

def modify_func(func, instructions: Sequence[dis.Instruction], func_name: str = ''):
    code = types.CodeType(
        func.__code__.co_argcount,
        func.__code__.co_posonlyargcount,
        func.__code__.co_kwonlyargcount,
        func.__code__.co_nlocals,
        func.__code__.co_stacksize,
        func.__code__.co_flags,
        instructions_to_bytecode(instructions),
        func.__code__.co_consts,
        func.__code__.co_names,
        func.__code__.co_varnames,
        func.__code__.co_filename,
        func_name,
        func.__code__.co_firstlineno,
        func.__code__.co_lnotab
    )
    return types.FunctionType(code, globals())

def main_globals():
    stack = inspect.stack()
    for frame_info in stack:
        if frame_info.frame.f_globals.get('__name__') == '__main__':
            main_globals = frame_info.frame.f_globals
            break
    return main_globals

def op_arg_at(code, i):
    extended_arg = 0
    last_op_offset = i - 2
    if last_op_offset >= 0 and code[last_op_offset] == dis.EXTENDED_ARG:
        start_offset = last_op_offset - 2
        for j in range(start_offset, -1, -2):
            if code[j] != dis.EXTENDED_ARG:
                start_offset = j
                break
        for j in range(start_offset, last_op_offset + 1, 2):
            op = code[j]
            arg = code[j + 1] | extended_arg
            extended_arg = arg << 8
    op = code[i]
    if op >= dis.HAVE_ARGUMENT:
        arg = code[i + 1] | extended_arg
    else:
        arg = None
    return (op, arg)

def get_instruction_at(co, offset):
    cell_names = co.co_cellvars + co.co_freevars
    return _get_instruction_object_at(offset, co.co_code, co.co_varnames, co.co_names,
                                   co.co_consts, cell_names)

def _get_instruction_object_at(offset, code, varnames=None, names=None, constants=None,
                      cells=None):
    op, arg = op_arg_at(code, offset)
    argval = None
    argrepr = ''
    if arg is not None:
        #  Set argval to the dereferenced value of the argument when
        #  available, and argrepr to the string representation of argval.
        #    _disassemble_bytes needs the string repr of the
        #    raw name index for LOAD_GLOBAL, LOAD_CONST, etc.
        argval = arg
        if op in dis.hasconst:
            argval, argrepr = dis._get_const_info(arg, constants)
        elif op in dis.hasname:
            argval, argrepr = dis._get_name_info(arg, names)
        elif op in dis.hasjabs:
            argval = arg*2
            argrepr = "to " + repr(argval)
        elif op in dis.hasjrel:
            argval = offset + 2 + arg*2
            argrepr = "to " + repr(argval)
        elif op in dis.haslocal:
            argval, argrepr = dis._get_name_info(arg, varnames)
        elif op in dis.hascompare:
            argval = dis.cmp_op[arg]
            argrepr = argval
        elif op in dis.hasfree:
            argval, argrepr = dis._get_name_info(arg, cells)
        elif op == dis.FORMAT_VALUE:
            argval, argrepr = dis.FORMAT_VALUE_CONVERTERS[arg & 0x3]
            argval = (argval, bool(arg & 0x4))
            if argval[1]:
                if argrepr:
                    argrepr += ', '
                argrepr += 'with format'
        elif op == dis.MAKE_FUNCTION:
            argrepr = ', '.join(s for i, s in enumerate(dis.MAKE_FUNCTION_FLAGS)
                                if arg & (1<<i))
    return dis.Instruction(dis.opname[op], op,
                        arg, argval, argrepr,
                        offset, None, None)