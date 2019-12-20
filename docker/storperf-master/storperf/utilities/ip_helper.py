##############################################################################
# Copyright (c) 2019 VMware and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################


def parse_address_and_port(address):
    port = 22
    if '.' in address:
        # this is IPv4
        if ':' in address:
            host = address.split(':')[0]
            port = int(address.split(':')[1])
        else:
            host = address
    else:
        if ']' in address:
            # this is IPv6
            host = address.split(']')[0].split('[')[1]
            port = int(address.split(']')[1].split(':')[1])
        else:
            host = address
    return (host, port)
