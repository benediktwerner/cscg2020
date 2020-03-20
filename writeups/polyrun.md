# Polyrun

The challenge consists of a single file: `run.pl`.

## Attempt 1: Is this a perl script?

Judging by the `.pl` extension and having a quick glance at the code, this looks like a `perl` script:

```perl
'';open(Q,$0);while(<Q>){if(/^#(.*)$/){for(split('-',$1)){$q=0;for(split){s/\|/:.:/xg;s/:/../g;$Q=$_?length:$_;$q+=$q?$Q:$Q*20;};}}}print"\n";
'';$?=
#@~^UgAAAA==v,Zj;MPKtb/|r/|Y4+|0sCT{XKN@#@&H/T$G6,J;?/M,P_qj{g6K|I3)d{sJ)VTE~,#~rF}x^X~,JgGwJexkAAA==^#~@
eval eval '"'."'"."'".';'.'\\'.'$'.'_'.('{'^'[').'='.('{'^'[').'\\'.'"'.'\\'.'"'.';'.('!'^'+')."'"."'".';'.('\\').'$'.'_'.'_'.('{'^'[').'='.('{'^'[').'\\'.'"'.('!'^'+').'#'.'\\'.'@'.'~'.'^'.('{'^'.').('`'|"'").('`'^'!').('`'^'!').('`'^'!').('`'^'!').'='.'='.('['^'-').','.('{'^'!').('`'|'*').';'.('`'^'-').('{'^'+').('`'^'+').('['^'/').('`'|'"').'/'.'|'.('['^')').'/'.'|'.('{'^'"').('^'^('`'|'*')).'+'.'|'.(('^')^('`'|'.')).('['^'(').('`'^'#').('{'^'/').'\\'.'{'.('{'^'#').('`'^'+').('`'^'.').'\\'.'@'.'#'.'\\'.'@'.'&'.('`'^'(').'/'.('{'^'/').'\\'.'$'.('`'^"'").('^'^('`'|'(')).','.('`'^'*').';'.'?'.'/'.('`'^'-').','.('{'^'+').'_'.('['^'*').('`'|'*').'\\'.'{'.('`'|"'").('^'^('`'|'(')).('`'^'+').'|'.('`'^(')')).('^'^('`'|'-')).')'.('`'|'$').'\\'.'{'.('['^'(').('`'^'*').')'.('{'^'-').('{'^'/').('`'^'%').'~'.','.'#'.'~'.('['^')').('`'^'&').'\\'.'}'.('['^'#').'^'.('{'^'#').'~'.','.('`'^'*').('`'|"'").('`'^"'").('['^',').('!'^'^').('`'^'*').('`'|'%').('['^'#').('`'|'+').('`'^'!').('`'^'!').('`'^'!').'='.'='.'^'.'#'.'~'.'\\'.'@'.('!'^'+')."'"."'".'\\'.'"'.';'.('!'^'+')."'"."'".';'.('`'|'&').('`'|'/').('['^')').('{'^'[').'('.('`'|'-').('['^'"').('{'^'[').'\\'.'$'.('`'|'/').('`'|'/').('^'^('`'|'/')).('`'|'/').('`'^')').'='.('^'^('`'|'.')).';'.('{'^'[').'\\'.'$'.('`'|'/').('`'|'/').('^'^('`'|'/')).('`'|'/').('`'^')').('{'^'[').'<'.'='.('{'^'[').('^'^('`'|'/')).';'.('{'^'[').'\\'.'$'.('`'|'/').('`'|'/').('^'^('`'|'/')).('`'|'/').('`'^')').'+'.'+'.')'.('{'^'[').'\\'.'{'.('`'|')').('`'|'&').'('.'\\'.'$'.('`'|'/').('`'|'/').('^'^('`'|'/')).('`'|'/').('`'^')').('{'^'[').'='.'='.('{'^'[').('^'^('`'|'.')).')'.'\\'.'{'.'\\'.'$'.'_'.'.'.'='.('['^'(').('['^'.').('`'|'"').('['^'(').('['^'/').('['^')')."\(".'\\'.'$'.'_'.'_'.','.('^'^('`'|',')).('^'^('`'|'/')).'+'.'\\'.'$'.('`'|'/').('`'|'/').('^'^('`'|('/'))).('`'|'/').('`'^')').','.('^'^('`'|'/')).')'.';'.'\\'.'$'.'_'.'.'.'='.('['^'(').('['^'.').('`'|"\"").('['^'(').('['^'/').('['^')').'('.'\\'.'$'.'_'.'_'.','.('^'^('`'|',')).('^'^('`'|'+')).'+'.'\\'.'$'.('`'|'/').('`'|'/').('^'^('`'|'/')).('`'|'/').('`'^')').','.('^'^('`'|'/')).')'.';'.'\\'.'$'.'_'.'.'.'='.('['^'(').('['^'.').('`'|'"').('['^'(').('['^'/').('['^')').'('.'\\'.'$'.'_'.'_'.','.('^'^("\`"|',')).(':'&'=').'+'.'\\'.'$'.('`'|'/').('`'|'/').('^'^('`'|'/')).('`'|'/').('`'^')').','.('^'^("\`"|'/')).')'.';'.'\\'.'$'.'_'.'.'.'='.'\\'.'"'.('{'^'[').'\\'.'"'.';'.'\\'.'}'.('`'|'%').('`'|',').('['^'(').('`'|'%').'\\'.'{'.('{'^'[').'\\'.'$'.'_'.('{'^'[').'.'.'='.('{'^'[').('`'|'#').('`'|'(').('['^')').'('.('^'^('`'|'.')).('['^'#').('`'|'!').'*'.('^'^('`'|'.')).('['^'#').('^'^('`'|'/')).('`'|'#').'-'.('^'^('`'|'.')).('['^'#').('`'^'"').('^'^('`'|'.')).')'.';'.'\\'.'}'.'\\'.'}'.('!'^'+').("'")."'".';'.('{'^'[').('['^'+').('['^')').('`'|')').('`'|'.').('['^'/').('{'^'[').'\\'.'$'.'_'.('{'^'[').'.'.('{'^'[').'\\'.'"'.('`'|'!').('['^')').('`'|'$').('`'|'%').('['^')').'\\'.'"'.';'.'"';$:=('.');
```

However, running it only tells us to `trY harder`:
```
$ perl run.pl

trY harder
```

Taking another look at the code, this suspicious comment immediately jumps out:
```
#@~^UgAAAA==v,Zj;MPKtb/|r/|Y4+|0sCT{XKN@#@&H/T$G6,J;?/M,P_qj{g6K|I3)d{sJ)VTE~,#~rF}x^X~,JgGwJexkAAA==^#~@
```

However, at first glance, it doesn't look like anything useful.
`UgAAAA==` and `JexkAAA=` look a bit like `base64` but it doesn't look useful and the second one isn't even valid `base64`.

So, lets instead try to clean the code up a bit. Maybe this will help us understand what we are supposed to do.

`'';` is just an empty string, which does nothing on its own, so we can ignore this.

The rest of the first line opens the code itself as a file, looks for lines starting with `#` and calculates something depending on their content:
```perl
open(Q, $0);
while (<Q>){
    if (/^#(.*)$/) {                        # Search for lines starting with '#' and take everything after that
        for (split('-', $1)) {              # Split by '-'
            $q = 0;
            for (split) {                   # Split by whitespace
                s/\|/:.:/xg;                # Replace '|' with ':.:'
                s/:/../g;                   # Replace ':' with '..'
                $Q = $_ ? length : $_;      # Take the length of the result
                $q += $q ? $Q : $Q * 20;    # and add it to $q. Multiply by 20 if this is the first part.
            }
        }
    }
}
print "\n";
```

The next line sets `$?` to the result of some cryptic `eval`.
The expression to be evaluated is simply a concatenation of a lot of single letters.
Some of them are also the result of `xor`ing multiple characters, e.g. `('{'^'[')`.

We can just let `perl` tell us what this actually is:
```perl
print eval '"'. ... .'"';
```

And this is what we get:
```perl
'';$_ = "";
'';$__ = "
#@~^UgAAAA==v,Zj;MPKtb/|r/|Y4+|0sCT{XKN@#@&H/T$G6,J;?/M,P_qj{g6K|I3)d{sJ)VTE~,#~rF}x^X~,JgGwJexkAAA==^#~@
''";
'';for (my $oo1oI=0; $oo1oI <= 1; $oo1oI++) {if($oo1oI == 0){$_.=substr($__,21+$oo1oI,1);$_.=substr($__,25+$oo1oI,1);$_.=substr($__,28+$oo1oI,1);$_.=" ";}else{ $_ .= chr(0xa*0x1c-0xB0);}}
''; print $_ . "arder";
```

This is again `perl` code that gets passed to another `eval`, so lets clean it up a bit:

```perl
$_ = "";
$__ = "\n#@~^UgAAAA==v,Zj;MPKtb/|r/|Y4+|0sCT{XKN@#@&H/T$G6,J;?/M,P_qj{g6K|I3)d{sJ)VTE~,#~rF}x^X~,JgGwJexkAAA==^#~@\''";
for (my $oo1oI=0; $oo1oI <= 1; $oo1oI++) {
    if ($oo1oI == 0) {
        $_ .= substr($__, 21 + $oo1oI, 1);
        $_ .= substr($__, 25 + $oo1oI, 1);
        $_ .= substr($__, 28 + $oo1oI, 1);
        $_ .= " ";
    } else {
        $_ .= chr(0xa * 0x1c - 0xB0);
    }
}
print $_ . "arder";
```

The loop just performs the `if`-branch in the first iteration and then the `else`-branch in the second iteration, so the code is actually more like this:
```perl
$_ = "";
$__ = "\n#@~^UgAAAA==v,Zj;MPKtb/|r/|Y4+|0sCT{XKN@#@&H/T$G6,J;?/M,P_qj{g6K|I3)d{sJ)VTE~,#~rF}x^X~,JgGwJexkAAA==^#~@\n''";
$_ .= substr($__, 21, 1);
$_ .= substr($__, 25, 1);
$_ .= substr($__, 28, 1);
$_ .= " ";
$_ .= chr(0xa * 0x1c - 0xB0);
print $_ . "arder";
```

This just takes some characters from the string in `$__` and prints it.
To be exact it takes the characters `t`, `r`, and `Y` and the second last line evaluates to `h`,
so this is just the code that prints `trY harder`.

In conclusion, it looks like this perl code actually doesn't do anything useful at all.


## Attempt 2: Is this also valid code in some other language?

Thinking about the name `polyrun` again, maybe this has something to do with `polyglot`.
Maybe the file is also valid code in another language?

This could also explain the weird `'';` at the start of some lines and the weird comment in the middle.
Maybe in some languages `'` starts a comment and the weird comment is the actual code.

Looking through some esoteric programming languages on `esolang.org`
shows some languages with similar syntax, but none of them matched completely.

Looking at the comment again, it starts with `#@~^` and ends with `^#~@`.
These look like some kind of starting and ending delimiters.
Maybe searching for them on Google will give some results.

And indeed this was one of the results I got: <https://master.ayra.ch/vbs/vbs.aspx>.

The page talks about encrypted VBScript files and how to detect them:
> The content should start with `#@~^XXXXXX==` and end with `==^#~@` plus a "null" char, which is not visible in most editors.

This matches our code and indeed in VBScript `'` also starts a comment,
so it looks like the file is also a valid encrypted VBScript.

The page also explains how to run these encrypted scripts:
> An encrypted vbs file can be launched directly in windows if it is has `.vbe` file extension.<br/>

So let's try changing the file extension to `.vbe` and running it.

This pops up a message box saying `CSCG[THIS_NOT_REAL_FLAG]` and then fails on the `eval`.

It looks like there is still another step required to get the flag.
Maybe there is a way to decrypt the VBScript code?
Searching on the internet for a bit we find out that this encryption is actually called `JScript.Encode`
and there exists a decoder for it: <https://gist.github.com/bcse/1834878>.

Using it we can indeed decrypt the script:
```vbs
'';open(Q,$0);while(<Q>){if(/^#(.*)$/){for(split('-',$1)){$q=0;for(split){s/\|/:.:/xg;s/:/../g;$Q=$_?length:$_;$q+=$q?$Q:$Q*20;};}}}print"\n";
'';$?=
' CSCG{This_is_the_flag_yo}
MsgBox "CSCG[THIS_NOT_REAL_FLAG]", VBOKOnly, "Nope"
eval eval ...
```

We can see the code that shows the message box and we find the real flag in a comment: `CSCG{This_is_the_flag_yo}`.
