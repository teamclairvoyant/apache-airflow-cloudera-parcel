require '_h2ph_pre.ph';

no warnings qw(redefine misc);

unless(defined(&_STDC_PREDEF_H)) {
    eval 'sub _STDC_PREDEF_H () {1;}' unless defined(&_STDC_PREDEF_H);
    eval 'sub __STDC_IEC_559__ () {1;}' unless defined(&__STDC_IEC_559__);
    eval 'sub __STDC_IEC_559_COMPLEX__ () {1;}' unless defined(&__STDC_IEC_559_COMPLEX__);
    eval 'sub __STDC_ISO_10646__ () {201103;}' unless defined(&__STDC_ISO_10646__);
    eval 'sub __STDC_NO_THREADS__ () {1;}' unless defined(&__STDC_NO_THREADS__);
}
1;
