# hrm
Human Resource Machine interpreter in Python

How to run
==========

From the root directory,

    python src/run.py question_dir answer_file
    
For example, to run original question number `16` with the answer file `16-yukuku.txt`

    python src/run.py levels/original/16 answers/original/16-yukuku.txt

Questions
=========

Questions are stored inside `levels` directory.

Each directory must have a `q.txt` file that describes the question, and one or more pairs of `*.in` and `*.out` files that describes the input and the expected output boxes.

q.txt file
----------

Description to be read by humans starts with `//`

Other than that, it contains the allowed commands, a subset or all of:

    inbox outbox
    copyto copyfrom
    add sub
    bumpup bumpdn
    jump jumpz jumpn

To specify the memory slots (floor tiles), use:

    mem size n
    
where `n` is the number of memory slots, and then to pre-fill the memory slots, use:

    mem[i] = v
    
where `i` is a non-negative integer < `n`, and `v` is either a number or a single non-numeric character.

Sample data files
-----------------

Both the `*.in` and `*.out` files contain a value in each line, either a  number or a single non-numeric character. 

Comments are allowed in form of lines of itself, where a line starts with `//`.

This is not allowed:

    A  // comment

This is allowed:

    // comment
    A

Answers
=======

The answer is written in a text file where each line can be:

A label, written as 

    label:
    
where `label` is any number of word characters.

A 0-argument command `inbox` or `outbox`.

    // take one item from inbox. If no more item, program ends.
    inbox
    
    // put the accumulator value to outbox
    outbox

A 1-argument jump command `jump`, `jumpn` (jump if negative), `jumpz` (jump if zero), where it is followed by the label of destination. For example:

    // jump to the label written as 'beginning:'
    jump beginning
    
    // if accumulator is zero, jump to the label written as `is_zero:`
    jumpz is_zero

A 1-argument command `copyfrom` `copyto` `add` `sub` `bumpup` `bumpdn`, where it is followed by a number or a number enclosed in brackets `[` `]`. For example:

    // copy from memory slot 0
    copyfrom 0
    
    // copy to memory slot 1
    copyto 1
    
    // add the accumulator with the value in memory slot 2
    add 2
    
    // subtract the accumulator with the value in memory slot pointed by value in memory slot 3
    sub [3]
    
    // increase by one the value in memory slot pointed by value in memory slot 4
    bumpup [4]

Credits
=======

Level data extracted from: https://github.com/atesgoral/hrm-level-data
