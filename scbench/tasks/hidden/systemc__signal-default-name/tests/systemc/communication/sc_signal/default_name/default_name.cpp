/*****************************************************************************

  Licensed to Accellera Systems Initiative Inc. (Accellera) under one or
  more contributor license agreements.  See the NOTICE file distributed
  with this work for additional information regarding copyright ownership.
  Accellera licenses this file to you under the Apache License, Version 2.0
  (the "License"); you may not use this file except in compliance with the
  License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
  implied.  See the License for the specific language governing
  permissions and limitations under the License.

 *****************************************************************************/

/*****************************************************************************

  default_name.cpp -- Default name of a signal whose value type generates names

  Original Author: Mayur Kubavat, 2026-11-15

 *****************************************************************************/

/*****************************************************************************

  MODIFICATION LOG - modifiers, enter your name, affiliation, date and
  changes you are making here.

      Name, Affiliation, Date:
  Description of Modification:

 *****************************************************************************/

// sc_signal and sc_buffer test;
// The default constructor of the value type calls sc_gen_unique_name().
// The signal shall still get a name of its own, and create one value only.

#include "systemc.h"

struct item
{
    item() : m_name( sc_gen_unique_name( "item" ) ) { count++; }

    bool operator == ( const item& rhs ) const
        { return m_name == rhs.m_name; }

    std::string m_name;
    static int count;
};

int item::count = 0;

std::ostream&
operator << ( std::ostream& os, const item& i )
{
    return os << i.m_name;
}

void
sc_trace( sc_trace_file*, const item&, const std::string& )
{}

int
sc_main( int, char*[] )
{
    sc_signal<item> sig1;
    sc_signal<item> sig2( sc_gen_unique_name( "sig" ) );
    sc_buffer<item> buf1;
    sc_buffer<item> buf2( sc_gen_unique_name( "buf" ) );

    cout << sig1.name() << endl;
    cout << sig2.name() << endl;
    cout << buf1.name() << endl;
    cout << buf2.name() << endl;
    cout << endl;

    // The current and the new value of a signal are one default
    // constructed object and its copy, so that they are equal.
    cout << "default constructed items: " << item::count << endl;

    return 0;
}
