# pygdo-fun
Some funny functions for the PyGDO chat system.

The module setting `teapot_header` controls the HTTP response header
`X-HTTP-TEAPOT-TEMP-C`. `always` (the default) sends `100`, a playful fictional
temperature in degrees Celsius; `no` omits it; `april_fools` sends it only on
April 1 according to the server's local calendar. It applies to HTTP responses
from PyGDO, not messages sent through chat connectors.
