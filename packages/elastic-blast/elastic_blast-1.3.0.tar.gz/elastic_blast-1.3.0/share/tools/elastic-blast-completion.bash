#!/usr/bin/env bash
_elastic-blast()
{
    if [ ${#COMP_WORDS[*]} -ge 3 ] ; then
        return
    fi
    COMPREPLY=($(compgen -W "submit status delete run-summary --version --help" -- "${COMP_WORDS[1]}"))
}
complete -F _elastic-blast elastic-blast
