// HauntedHouseAutoplay.exe - runs Haunted House from a walkthrough file.
//
// The exe is a small launcher: it finds Python on this computer and runs the
// embedded copy of autoplay.py against HauntedHouse.py and walkthrough.txt,
// which it looks for next to the exe. Any arguments are passed on to autoplay.py
// (for example: --fast, --delay 1, or a different walkthrough file).
//
// Build with build.sh in this folder; it copies the current autoplay.py in first.
package main

import (
	_ "embed"
	"bufio"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

//go:embed autoplay.py
var autoplayScript []byte

func pause() {
	fmt.Print("\nPress Enter to close...")
	bufio.NewReader(os.Stdin).ReadString('\n')
}

func fail(format string, args ...any) {
	fmt.Printf(format+"\n", args...)
	pause()
	os.Exit(1)
}

// findPython returns a command that starts Python 3, trying the Windows
// launcher first. The Microsoft Store "python" alias fails --version, so it is skipped.
func findPython() []string {
	candidates := [][]string{{"py", "-3"}, {"python"}, {"python3"}}
	for _, c := range candidates {
		args := append(append([]string{}, c[1:]...), "--version")
		out, err := exec.Command(c[0], args...).CombinedOutput()
		if err == nil && strings.HasPrefix(strings.TrimSpace(string(out)), "Python 3") {
			return c
		}
	}
	return nil
}

func main() {
	exe, err := os.Executable()
	if err != nil {
		fail("Could not locate the exe: %v", err)
	}
	dir := filepath.Dir(exe)
	game := filepath.Join(dir, "HauntedHouse.py")
	walkthrough := filepath.Join(dir, "walkthrough.txt")
	if _, err := os.Stat(game); err != nil {
		fail("HauntedHouse.py was not found next to the exe (%s).", dir)
	}

	python := findPython()
	if python == nil {
		fail("Python 3 was not found. Install it from python.org (tick \"Add python.exe to PATH\") and try again.")
	}

	tmp, err := os.CreateTemp("", "haunted-autoplay-*.py")
	if err != nil {
		fail("Could not create a temporary file: %v", err)
	}
	tmp.Write(autoplayScript)
	tmp.Close()
	defer os.Remove(tmp.Name())

	args := append([]string{}, python[1:]...)
	args = append(args, tmp.Name(), "--game", game)
	userArgs := os.Args[1:]
	hasWalkthrough := false
	for i := 0; i < len(userArgs); i++ {
		a := userArgs[i]
		if a == "--delay" || a == "--game" {
			i++ // skip the option's value
			continue
		}
		if !strings.HasPrefix(a, "-") {
			hasWalkthrough = true
		}
	}
	if !hasWalkthrough {
		args = append(args, walkthrough)
	}
	args = append(args, userArgs...)

	cmd := exec.Command(python[0], args...)
	cmd.Stdin, cmd.Stdout, cmd.Stderr = os.Stdin, os.Stdout, os.Stderr
	if err := cmd.Run(); err != nil {
		if exitErr, ok := err.(*exec.ExitError); ok {
			pause()
			os.Exit(exitErr.ExitCode())
		}
		fail("Could not start Python: %v", err)
	}
}
