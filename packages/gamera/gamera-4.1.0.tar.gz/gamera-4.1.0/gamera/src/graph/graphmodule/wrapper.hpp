/*
 *
 * Copyright (C) 2011 Christian Brandt
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


#ifndef _WRAPPER_HPP_940FFAA9288997
#define _WRAPPER_HPP_940FFAA9288997

////////////////#define __DEBUG_GAPI__

//@see https://docs.python.org/3/c-api/intro.html#include-files
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "gameramodule.hpp"
//##include "graphdata_pyobject.hpp"

#include "graph_common.hpp"
#include "graphdatapyobject.hpp"
#ifdef __DEBUG_GAPI__
#include <iostream>
#endif
using namespace Gamera::GraphApi;
struct GraphObject;
struct EdgeObject;
struct NodeObject;



// -----------------------------------------------------------------------------
// some wrappers for easier handling of self-parameters and return values
#define INIT_SELF_GRAPH() GraphObject* so = ((GraphObject*)self)
#define INIT_SELF_EDGE() EdgeObject* so = ((EdgeObject*)self)
#define INIT_SELF_NODE() NodeObject* so = ((NodeObject*)self)
#define RETURN_BOOL(a) {PyObject *_ret_ = PyBool_FromLong((long)(a)); return _ret_;}
#define RETURN_INT(a) {return PyLong_FromLong((long)(a));}
#define RETURN_VOID() {PyObject *_ret_ = Py_None; Py_XINCREF(_ret_); return _ret_;}
#define RETURN_DOUBLE(a) {return PyFloat_FromDouble((a));}

#endif /* _WRAPPER_HPP_940FFAA9288997 */

