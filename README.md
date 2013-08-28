Antares
=======

Antares is an open source Web Services attacking framework which is intended to implement the basic WS-related 
mechanisms in order for a human to start interaction with the EndPoint as soon as possible. It will parse a WSDL
document in the form of a local file or URL in order to organize and display information in a simple yet powerfull
manner. 

Its basic functions will create request samples for different operations, bindings and port types with a minimalistic
editor for manual testing, it will also parse the related XSD structure to easily detect data types mismatch against 
the application and the presentation layers. An injector plugin has being built to test for generic web application
data injections also.

A set of functions will help create other Web Service specific exploit modules. This is the final objective of this
project.

Features
======

- Offline WSDL parsing: Antares will save a copy of the target WSDL in your filesystem when a project is created.
                        The user is able to choose between offline or online WSDL parsing which allows him to modify
                        WSDL and/or XSD files. Such functionality can be useful for fixing broken descriptions or 
                        spoofing XSD structures.

Considerations
======

Building a generic WebService client is an ambitious task. Developers don't usually stick to standards 
