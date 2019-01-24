#!/bin/bash
export RPM_OPT_FLAGS="-O2 -g -m64 -mtune=generic"
#-pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector-strong --param=ssp-buffer-size=4 -grecord-gcc-switches
export RPM_LD_FLAGS="-Wl,-z,relro"
export CFLAGS="$RPM_OPT_FLAGS -D_GNU_SOURCE -fPIC -fwrapv"
export CXXFLAGS="$RPM_OPT_FLAGS -D_GNU_SOURCE -fPIC -fwrapv"
export CPPFLAGS="$(pkg-config --cflags-only-I libffi)"
export OPT="$RPM_OPT_FLAGS -D_GNU_SOURCE -fPIC -fwrapv"
export LINKCC="gcc"
export LDFLAGS="$RPM_LD_FLAGS"
if pkg-config openssl ; then
  export CFLAGS="$CFLAGS $(pkg-config --cflags openssl)"
  export LDFLAGS="$LDFLAGS $(pkg-config --libs-only-L openssl)"
fi

