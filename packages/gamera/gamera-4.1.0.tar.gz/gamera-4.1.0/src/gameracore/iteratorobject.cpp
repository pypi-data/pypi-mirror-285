/*
 * Copyright (C) 2001-2005 Ichiro Fujinaga, Michael Droettboom, and Karl MacMillan
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 */

#include "python_iterator.hpp"

static PyTypeObject IteratorType = {
  PyVarObject_HEAD_INIT(nullptr, 0)
};

void iterator_dealloc(PyObject* self) {
  IteratorObject* so = (IteratorObject*)self;
#ifdef DEBUG_DEALLOC
  std::cerr << "iterator dealloc\n";
#endif
  (*(so->m_fp_dealloc))(so);
  self->ob_type->tp_free(self);
}

PyObject* iterator_get_iter(PyObject* self) {
  Py_XINCREF(self);
  return self;
}

PyObject* iterator_next(PyObject* self) {
  IteratorObject* so = (IteratorObject*)self;
  PyObject* result = (*(so->m_fp_next))(so);
  if (result == nullptr) {
    PyErr_SetString(PyExc_StopIteration, "");
    return 0;
  }
  return result;
}

void init_IteratorType(PyObject* module_dict) {
  #ifdef Py_SET_TYPE
    Py_SET_TYPE(&IteratorType, &PyType_Type);
  #else
    Py_TYPE(&IteratorType) = &PyType_Type;
  #endif
  IteratorType.tp_name =  "gamera.Iterator";
  IteratorType.tp_basicsize = sizeof(IteratorObject);
  IteratorType.tp_dealloc = iterator_dealloc;
  IteratorType.tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE;
  IteratorType.tp_getattro = PyObject_GenericGetAttr;
  IteratorType.tp_alloc = nullptr; // PyType_GenericAlloc;
  IteratorType.tp_free = nullptr; // _PyObject_Del;
  IteratorType.tp_iter = iterator_get_iter;
  IteratorType.tp_iternext = iterator_next;
  PyType_Ready(&IteratorType);
  PyDict_SetItemString(module_dict, "Iterator", (PyObject*)&IteratorType);
}
