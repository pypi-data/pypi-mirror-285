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
static const char* messagestream_class_doc = "\n"
                                             "  A message handler used to create an in-thread iterator interface over the Messages that are returned from a command.\n\n";

static const char* close_doc = "close()\n\nCloses this message stream.\n\n";
static const char* timeout_doc = "timeout(millis)\n\nSets the timeout on this message stream.\n\n"
                                 " If no message is received in this timeout, None is returned to the caller of next(), and the\n"
                                 " stream remains open.\n\n";
static const char* conflate_doc = "conflate()\n\n"
                                  "Enables message conflation by SOW key.\n\n";

static const char* max_depth_doc = "max_depth(maxDepth)\n\n"
                                   "Sets the maximum depth allowed for this message stream (that is, the maximum number of messages stored in this object at a given time). When this limit is exceeded, the Client will stop receiving messages from the socket until messages are removed from the MessageStream.\n\n"
                                   ":param maxDepth: The maximum number of messages that are buffered in this stream\n"
                                   "       before pushback on the network connection.\n";

static const char* get_max_depth_doc = "get_max_depth()\n\n"
                                       "Gets the maximum depth allowed for this message stream.\n\n";

static const char* get_depth_doc = "get_depth()\n\n"
                                   "Gets the current depth of this message stream.\n\n";

