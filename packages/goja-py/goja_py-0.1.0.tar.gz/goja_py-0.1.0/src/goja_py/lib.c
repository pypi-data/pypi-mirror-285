#include <Python.h>

PyObject* execute(PyObject*);

int PyArg_ParseTuple_U(PyObject* args, PyObject** obj) {
    return PyArg_ParseTuple(args, "U", obj);
}

static struct PyMethodDef methods[] = {
    {"execute", (PyCFunction)execute, METH_VARARGS},
    {NULL, NULL}
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "goja_py_runtime",
    NULL,
    -1,
    methods
};

PyMODINIT_FUNC PyInit_goja_py_runtime(void) {
    return PyModule_Create(&module);
}
