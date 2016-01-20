##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

class { 'python':
  pip        => true,
  dev        => true,
  virtualenv => true,
}

class { 'graphite':
  port    => 8080,
  bind_address => '0.0.0.0',
}
