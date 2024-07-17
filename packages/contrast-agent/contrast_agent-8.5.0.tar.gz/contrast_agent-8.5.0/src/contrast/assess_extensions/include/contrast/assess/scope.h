/*
 * Copyright © 2024 Contrast Security, Inc.
 * See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
 */
#ifndef _ASSESS_SCOPE_H_
#define _ASSESS_SCOPE_H_
/* Python requires its own header to always be included first */
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <patchlevel.h>

typedef PyObject PyContextVarT;
typedef PyObject PyContextTokenT;

void init_contrast_scope_cvars(PyContextVarT *, PyContextVarT *, PyContextVarT *);

PyContextTokenT *enter_contrast_scope(void);
void reset_contrast_scope(PyContextTokenT *);
PyContextTokenT *enter_propagation_scope(void);
void reset_propagation_scope(PyContextTokenT *);
int should_propagate(void);

#endif /* _ASSESS_SCOPE_H_ */
