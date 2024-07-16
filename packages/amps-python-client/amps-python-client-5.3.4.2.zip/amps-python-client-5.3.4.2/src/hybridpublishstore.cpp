////////////////////////////////////////////////////////////////////////////
//
// Copyright (c) 2010-2024 60East Technologies Inc., All Rights Reserved.
//
// This computer software is owned by 60East Technologies Inc. and is
// protected by U.S. copyright laws and other laws and by international
// treaties.  This computer software is furnished by 60East Technologies
// Inc. pursuant to a written license agreement and may be used, copied,
// transmitted, and stored only in accordance with the terms of such
// license agreement and with the inclusion of the above copyright notice.
// This computer software or any other copies thereof may not be provided
// or otherwise made available to any other person.
//
// U.S. Government Restricted Rights.  This computer software: (a) was
// developed at private expense and is in all respects the proprietary
// information of 60East Technologies Inc.; (b) was not developed with
// government funds; (c) is a trade secret of 60East Technologies Inc.
// for all purposes of the Freedom of Information Act; and (d) is a
// commercial item and thus, pursuant to Section 12.212 of the Federal
// Acquisition Regulations (FAR) and DFAR Supplement Section 227.7202,
// Government's use, duplication or disclosure of the computer software
// is subject to the restrictions set forth by 60East Technologies Inc..
//
////////////////////////////////////////////////////////////////////////////

#define PY_SSIZE_T_CLEAN 1
#include <Python.h>
#include <amps/ampsplusplus.hpp>
#include <ampspy_types.hpp>
#include <ampspy_defs.hpp>
#include <amps/HybridPublishStore.hpp>
#include "hybridpublishstore_docs.h"

using namespace AMPS;
namespace ampspy
{
  namespace hybridpublishstore
  {

    AMPSDLL ampspy::ampspy_type_object hybridpublishstore_type;

//    def __init__(self, name):
    static int _ctor(obj* self, PyObject* args, PyObject* kwds)
    {
      char* filename = NULL;
      unsigned int maxMemoryCapacity = 0;
      if (!PyArg_ParseTuple(args, "sk", &filename, &maxMemoryCapacity))
      {
        return -1;
      }
      assert(filename != NULL);

      self->impl = new Store(new HybridPublishStore(filename, maxMemoryCapacity));
      self->resizeHandler = NULL;
      return 0;
    }

    static void _dtor(obj* self)
    {
      {
        UNLOCKGIL;
        delete self->impl;
      }
      Py_XDECREF(self->resizeHandler);
      shims::free(self);
    }

    static PyObject* get_unpersisted_count(obj* self, PyObject* args)
    {
      return PyInt_FromSize_t( self->impl->unpersistedCount() );
    }

    bool
    call_resize_handler(StoreImpl* store, size_t size, void* vp)
    {
      LOCKGIL;
      obj* s = (obj*)vp;
#if defined(_WIN32) && !defined(_WIN64)
      PyObject* args = Py_BuildValue("(Oi)", s, size);
#else
      PyObject* args = Py_BuildValue("(Ol)", s, size);
#endif
      PyObject* pyRet = PyObject_Call(s->resizeHandler, args, (PyObject*)NULL);
      Py_DECREF(args);
      if (pyRet == NULL || PyErr_Occurred())
      {
        Py_XDECREF(pyRet);
        if (PyErr_ExceptionMatches(PyExc_SystemExit))
        {
          ampspy::unhandled_exception();
        }
        throw StoreException("The resize handler threw an exception");
      }
      bool ret = (PyObject_IsTrue(pyRet) != 0);
      Py_DECREF(pyRet);
      return ret;
    }

    static PyObject* set_resize_handler(obj* self, PyObject* args)
    {
      PyObject* callable;
      if (!PyArg_ParseTuple(args, "O", &callable))
      {
        return NULL;
      }
      if (!PyCallable_Check(callable))
      {
        PyErr_SetString(PyExc_TypeError, "argument must be callable.");
        return NULL;
      }
      Py_INCREF(callable);
      if (self->resizeHandler)
      {
        Py_DECREF(self->resizeHandler);
      }
      self->resizeHandler = callable;
      CALL_RETURN_NONE(self->impl->setResizeHandler((AMPS::PublishStoreResizeHandler)call_resize_handler, self));
    }

    void add_types(PyObject* module_)
    {
      hybridpublishstore_type.setName("AMPS.HybridPublishStore")
      .setBasicSize(sizeof(obj))
      .setDestructorFunction(_dtor)
      .setConstructorFunction(_ctor)
      .setDoc(hybridpublishstore_class_doc)
      .setBaseType()
      .notCopyable()
      .addMethod("get_unpersisted_count", get_unpersisted_count, "get_unpersisted_count()\n\nReturns the number of messages published which have not been ACK'ed by the server.\n")
      .addMethod("set_resize_handler", set_resize_handler, "set_resize_handler()\n\nSets the object to call when the store needs to resize.\n")
      .createType()
      .registerType("HybridPublishStore", module_);

    }

  } // namespace hybridpublishstore
} // namespace ampspy
