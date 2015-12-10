class { 'python':
  pip        => true,
  dev        => true,
  virtualenv => true,
}

class { 'graphite':
  port    => 8080,
  bind_address => '0.0.0.0',
}
