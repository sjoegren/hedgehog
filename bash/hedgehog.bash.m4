# Bash completion for sshansible
_complete_sshansible() {
	case ${COMP_WORDS[$COMP_CWORD]} in
		-*)
			COMPREPLY=($(compgen -W "--help --scp --last --ssh-copy-id --version" -- ${COMP_WORDS[$COMP_CWORD]}))
			;;
		*)
			if [ ${COMP_WORDS[(($COMP_CWORD - 1))]} == "--inventory" ]; then
				# complete filenames, not used right now
				COMPREPLY=($(compgen -f "${COMP_WORDS[$COMP_CWORD]}"))
			else
				for ((i=1; i < $COMP_CWORD - 1; i++)); do
					if [ "${COMP_WORDS[$i]}" == "--scp" ]; then
						COMPREPLY=($(compgen -f "${COMP_WORDS[$COMP_CWORD]}"))
						return
					fi
				done
				COMPREPLY=($(compgen -W "$(INSTALL_DIR/bin/sshansible --complete-hosts)" "${COMP_WORDS[$COMP_CWORD]}"))
			fi
			;;
	esac
}

complete -F _complete_sshansible sshansible

# Functions for use with the dirstack program.
ds() {
    local out rv
    if [ -n "$1" ]; then
        # Must cd first, to honor CDPATH
        cd "$1" || return
        INSTALL_DIR/bin/dirstack --add "$PWD"
        return
    fi
    out="$(INSTALL_DIR/bin/dirstack)"
    rv=$?
    case $rv in
        0) cd "$out" ;;  # go to selected dir
        3) ;;
        4) echo $out ;;
        *)
    esac
}
complete -o nospace -F _cd ds

export PATH="$PATH:INSTALL_DIR/bin"
