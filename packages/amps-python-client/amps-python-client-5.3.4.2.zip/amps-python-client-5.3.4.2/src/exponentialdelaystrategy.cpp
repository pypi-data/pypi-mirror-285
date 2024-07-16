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
#include <amps/ReconnectDelayStrategy.hpp>
#include <amps/ReconnectDelayStrategyImpl.hpp>


using namespace AMPS;
namespace ampspy
{
  namespace exponentialdelaystrategy
  {

    AMPSDLL ampspy::ampspy_type_object type;

//    def __init__(self, name):
    static int ctor(obj* self, PyObject* args, PyObject* kwds)
    {
      static const char* kwargs[] = { "initial_delay", "maximum_delay",
                                      "backoff_exponent", "maximum_retry_time", "jitter", NULL
                                    };
      unsigned long initial_delay = 200, maximum_delay = 20 * 1000,
                    maximum_retry_time = 0;
      double backoff_exponent = 2.0;
      double jitter = 1.0;

      if (!PyArg_ParseTupleAndKeywords(args, kwds, "|IIdId", (char**)kwargs,
                                       &initial_delay, &maximum_delay, &backoff_exponent, &maximum_retry_time,
                                       &jitter))
      {
        return -1;
      }
      new (&(self->impl)) ReconnectDelayStrategy(
        new AMPS::ExponentialDelayStrategy(initial_delay, maximum_delay,
                                           backoff_exponent, maximum_retry_time, jitter));
      return 0;
    }
    static void dtor(obj* self)
    {
      self->impl.~ReconnectDelayStrategy();
      shims::free(self);
    }

    static PyObject* get_connect_wait_duration(obj* self, PyObject* args)
    {
      const char* uri = NULL;
      if (!PyArg_ParseTuple(args, "s", &uri))
      {
        return NULL;
      }
      CALL_RETURN_SIZE_T( self->impl.getConnectWaitDuration(uri) );
    }

    static PyObject* reset(obj* self, PyObject* args)
    {
      self->impl.reset();
      NONE;
    }

    static const char* docstring =
      "ExponentialDelayStrategy is an implementation that exponentially\n"
      "backs off when reconnecting to the same server, with a maximum\n"
      "time to retry before it gives up entirely.\n\n"
      "By default, an ExponentialDelayStrategy has an initial delay of\n"
      "200 ms, a maximum delay of  20 seconds, a backoff exponent of\n"
      "2.0, and has no limit to the amount of time to retry the connection.\n"
      "\n"
      "Constructor parameters:\n\n"
      ":param initial_delay:      The time (in milliseconds) to wait before\n"
      "                           reconnecting to a server for the first\n"
      "                           time after a failed connection.\n\n"
      ":param maximum_delay:      The maximum time to wait for any reconnect\n"
      "                           attempt (milliseconds). Exponential\n"
      "                           backoff will not exceed this maximum.\n\n"
      ":param backoff_exponent:   The exponent to use for calculating the\n"
      "                           next delay time. For example, if the\n"
      "                           initial time is 200ms and the exponent\n"
      "                           is 2.0, the next delay will be 400ms,\n"
      "                           then 800ms, etc.\n\n"
      ":param maximum_retry_time: The maximum time (milliseconds) to allow\n"
      "                           reconnect attempts to continue without\n"
      "                           a successful connection, before \"giving\n"
      "                           up\" and abandoning the connection attempt.\n\n"
      ":param jitter:             The amount of 'jitter' to apply when\n"
      "                           calculating a delay time, measured in multiples\n"
      "                           of the initial delay. Jitter is used to reduce\n"
      "                           the number of simultaneous reconnects that may\n"
      "                           be issued from multiple clients.\n\n\n";

    void add_types(PyObject* module_)
    {
      type.setName("AMPS.ExponentialDelayStrategy")
      .setBasicSize(sizeof(obj))
      .setDestructorFunction(dtor)
      .setConstructorFunction(ctor)
      .setBaseType()
      .setDoc(docstring)
      .notCopyable()
      .addMethod("get_connect_wait_duration", get_connect_wait_duration,
                 "Returns the time that the client should delay before connecting "
                 "to the given server URI.")
      .addMethod("reset", reset, "Reset the state of this reconnect delay. AMPS calls this "
                 "method when a connection is established.")
      .createType()
      .registerType("ExponentialDelayStrategy", module_);
    }

  } // namespace exponentialdelaystrategy

} // namespace ampspy
