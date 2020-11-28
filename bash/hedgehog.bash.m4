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
				COMPREPLY=($(compgen -W "$(sshansible --complete-hosts)" "${COMP_WORDS[$COMP_CWORD]}"))
			fi
			;;
	esac
}

complete -F _complete_sshansible sshansible

export PATH="$PATH:INSTALL_DIR/bin"
