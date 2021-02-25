/*
 * instructions.h
 *
 *  Created on: 2021. 2. 25.
 *      Author: yuchan
 */

#ifndef INSTRUCTIONS_H_
#define INSTRUCTIONS_H_


enum Instructions {
	ADD,
	SUB,
	MUL,
	DIV,

	ADDS,
	MULS,

	PUSH,
	PUSHS,

	POP,  // pop element from stack and
	POPS,

	PUSHVS, // get value from variable and push it to stack (string)
	PUSHV,  // same as above but for numerical

	JMP, // jump to address of top of stack
	JMT, // JuMp if True

	ADDR, // get address from string

	AVAR,
	ASVAR,

	HALT,
};


#endif /* INSTRUCTIONS_H_ */
