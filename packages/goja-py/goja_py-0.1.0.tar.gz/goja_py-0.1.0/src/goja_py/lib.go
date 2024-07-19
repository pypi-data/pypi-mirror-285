package main

// #include <stdlib.h>
// #include <Python.h>
// int PyArg_ParseTuple_U(PyObject*, PyObject**);
import "C"
import "fmt"
import "unsafe"
import "github.com/dop251/goja"

func executeJS(codeStr string) string {
	runtime := goja.New()
	value, err := runtime.RunString(codeStr)
	if err != nil {
		return fmt.Sprintf("{\"___error___\": \"%s\"}", err.Error())
	}
	return value.String()
}

//export execute
func execute(self *C.PyObject, args *C.PyObject) *C.PyObject {
	var obj *C.PyObject
	if C.PyArg_ParseTuple_U(args, &obj) == 0 {
		return nil
	}
	bytes := C.PyUnicode_AsUTF8String(obj)
	resultStr := C.CString(executeJS(C.GoString(C.PyBytes_AsString(bytes))))
	ret := C.PyUnicode_FromString(resultStr)

	C.free(unsafe.Pointer(resultStr))
	C.Py_DecRef(bytes)

	return ret
}

func main() {}
