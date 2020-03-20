open(Q, "run.pl");
while (<Q>){
    if (/^#(.*)$/) {
        for (split('-', $1)) {
            $q = 0;
            for (split) {
                s/\|/:.:/xg;
                s/:/../g;
                $Q = $_ ? length : $_;
                $q += $q ? $Q : $Q * 20;
            }
        }
    }
}

print "\n";
$?=

#@~^UgAAAA==v,Zj;MPKtb/|r/|Y4+|0sCT{XKN@#@&H/T$G6,J;?/M,P_qj{g6K|I3)d{sJ)VTE~,#~rF}x^X~,JgGwJexkAAA==^#~@

$_ = "";
$__ = "
#@~^UgAAAA==v,Zj;MPKtb/|r/|Y4+|0sCT{XKN@#@&H/T$G6,J;?/M,P_qj{g6K|I3)d{sJ)VTE~,#~rF}x^X~,JgGwJexkAAA==^#~@
''";

$_ .= substr($__, 21, 1);
$_ .= substr($__, 25, 1);
$_ .= substr($__, 28, 1);
$_ .= " ";
$_ .= chr(0xa * 0x1c - 0xB0);
print $_ . "arder";

$: = '.';
