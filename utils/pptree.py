# from https://github.com/clemtoy/pptree
from itertools import chain, zip_longest, repeat
from turtle import pen

JOINER_WIDTH = 3
DEFAULT_JOINER = ' ' * JOINER_WIDTH
CONNECTION_JOINER = '─' * JOINER_WIDTH
L_BRANCH_CONNECTOR = '─┘ '
LR_BRANCH_CONNECTOR = '─┴─'
R_BRANCH_CONNECTOR = ' └─'
L_NODE_CONNECTOR = '─┐ '
LR_NODE_CONNECTOR = '─┬─'
R_NODE_CONNECTOR= ' ┌─'


def multijoin(blocks, joiners=()):
    f"""
    Take one block (list of strings) or more and join them line by line with the specified joiners
    :param blocks: [['a', ...], ['b', ...], ...]
    :param joiners: ['─', ...]
    :return: ['a─b', ...]
    """

    # find maximum content width for each block
    block_content_width = tuple(max(map(len, block), default=0) for block in blocks)

    return tuple(

        joiner.join(

            (string or '')                 # string if present (see fillvalue below)
            .center(block_content_length)  # normalize content width across block

            for string, block_content_length in zip(block, block_content_width)

        )

        for block, joiner in zip(zip_longest(*blocks, fillvalue=None),
                                 chain(joiners, repeat(DEFAULT_JOINER))) # joiners or default

    )


def wire(block, connector):
    left_c = ' ' if connector == R_NODE_CONNECTOR else '─'
    right_c = ' ' if connector == L_NODE_CONNECTOR else '─'

    block, (left, right) = block

    if not (left or right):
        length = len(block[0])  # len of first line


        length -= 1             # ignore connector
        left = length // 2
        right = length - left

    return multijoin([[
        f'{left_c * left}{connector}{right_c * right}',
        *block
    ]])


def branch(blocks):
    wired_blocks = tuple(map(lambda blk: wire(blk, LR_NODE_CONNECTOR), blocks))

    return multijoin(wired_blocks, (CONNECTION_JOINER,))


def branch_left(blocks):
    last, *rest = blocks

    last = wire(last, R_NODE_CONNECTOR)
    rest = branch(rest)

    return multijoin([last, rest], (CONNECTION_JOINER,))


def branch_right(blocks):
    *rest, last = blocks

    rest = branch(rest)
    last = wire(last, L_NODE_CONNECTOR)

    return multijoin([rest, last], (CONNECTION_JOINER,))


def connect_branches(left, right):
    joiner = (LR_BRANCH_CONNECTOR if right else L_BRANCH_CONNECTOR) if left else R_BRANCH_CONNECTOR

    return multijoin([left, right], (joiner,))


def blocklen(block):
    if block:
        return len(block[0])

    else:
        return 0    

class Node:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.children = []

        if parent:
            self.parent.children.append(self)


def print_tree(current_node, childattr='children', nameattr='name', horizontal=True):
    if hasattr(current_node, nameattr):
        name = lambda node: getattr(node, nameattr)
    else:
        name = lambda node: str(node)

    children = lambda node: getattr(node, childattr)
    nb_children = lambda node: sum(nb_children(child) for child in children(node)) + 1

    def balanced_branches(current_node):
        size_branch = {child: nb_children(child) for child in children(current_node)}

        """ Creation of balanced lists for "a" branch and "b" branch. """
        a = sorted(children(current_node), key=lambda node: nb_children(node))
        b = []
        while a and sum(size_branch[node] for node in b) < sum(size_branch[node] for node in a):
            b.append(a.pop())

        return a, b
    
    output = []
    if horizontal:
        print_tree_horizontally(output, current_node, balanced_branches, name)
    else:
        print_tree_vertically(output, current_node, balanced_branches, name, children)
    # print(type())
    return "".join(output)

def print_tree_horizontally(output, current_node, balanced_branches, name_getter, indent='', last='updown'):

    up, down = balanced_branches(current_node)

    """ Printing of "up" branch. """
    for child in up:     
        next_last = 'up' if up.index(child) == 0 else ''
        next_indent = '{0}{1}{2}'.format(indent, ' ' if 'up' in last else '│', ' ' * len(name_getter(current_node)))
        print_tree_horizontally(output, child, balanced_branches, name_getter, next_indent, next_last)

    """ Printing of current node. """
    if last == 'up': start_shape = '┌'
    elif last == 'down': start_shape = '└'
    elif last == 'updown': start_shape = ' '
    else: start_shape = '├'

    if up: end_shape = '┤'
    elif down: end_shape = '┐'
    else: end_shape = ''    

    output.extend(list('{0}{1}{2}{3}\n'.format(indent, start_shape, name_getter(current_node), end_shape)))
    """ Printing of "down" branch. """
    for child in down:
        next_last = 'down' if down.index(child) is len(down) - 1 else ''
        next_indent = '{0}{1}{2}'.format(indent, ' ' if 'down' in last else '│', ' ' * len(name_getter(current_node)))
        print_tree_horizontally(output, child, balanced_branches, name_getter, next_indent, next_last)


def tree_repr(output, current_node, balanced_branches, name, children):

    sx, dx = balanced_branches(current_node)

    """ Creation of children representation """

    tr_rpr = lambda node: tree_repr(output, node, balanced_branches, name, children)

    left = branch_left(map(tr_rpr, sx)) if sx else ()
    right = branch_right(map(tr_rpr, dx)) if dx else ()

    children_repr = tuple(
        connect_branches(
            left,
            right
        ) if sx or dx else ()
    )

    current_name = name(current_node)
    
    name_len = len(current_name)
    name_l, name_r = name_len // 2, name_len // 2

    left_len, right_len = blocklen(left), blocklen(right)
    
    current_name = f"{' ' * (left_len - name_l)}{current_name}{' ' * (right_len - name_r)}"

    return multijoin([[current_name, *children_repr]]), (max(left_len, name_l), max(right_len, name_r))


def print_tree_vertically(*args):
    output += '\n'.join(tree_repr(*args)[0])