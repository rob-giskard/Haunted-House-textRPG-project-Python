// HauntedHouse.exe - the game as a single, standalone Windows program.
//
// The exe carries its own copy of Python (a trimmed python-build-standalone
// runtime) and the game script. On the first run it unpacks Python into
// %LOCALAPPDATA%\HauntedHouse, then it simply runs the game in this console.
// Nothing needs to be installed on the player's computer.
//
// Build with build.sh in this folder (see the README).
package main

import (
	"archive/zip"
	"bufio"
	"bytes"
	"crypto/sha256"
	_ "embed"
	"encoding/hex"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
)

//go:embed runtime.zip
var runtimeZip []byte

//go:embed HauntedHouse.py
var gameScript []byte

func pause() {
	fmt.Print("\nPress Enter to close...")
	bufio.NewReader(os.Stdin).ReadString('\n')
}

func fail(format string, args ...any) {
	fmt.Printf(format+"\n", args...)
	pause()
	os.Exit(1)
}

func shortHash(b []byte) string {
	sum := sha256.Sum256(b)
	return hex.EncodeToString(sum[:6])
}

// unpack extracts the embedded runtime into dest.
func unpack(dest string) error {
	r, err := zip.NewReader(bytes.NewReader(runtimeZip), int64(len(runtimeZip)))
	if err != nil {
		return err
	}
	for _, f := range r.File {
		path := filepath.Join(dest, filepath.FromSlash(f.Name))
		mode := f.Mode()
		switch {
		case mode.IsDir():
			if err := os.MkdirAll(path, 0o755); err != nil {
				return err
			}
			continue
		case mode&os.ModeSymlink != 0:
			rc, err := f.Open()
			if err != nil {
				return err
			}
			target, _ := io.ReadAll(rc)
			rc.Close()
			os.MkdirAll(filepath.Dir(path), 0o755)
			if err := os.Symlink(string(target), path); err != nil {
				return err
			}
			continue
		}
		if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
			return err
		}
		rc, err := f.Open()
		if err != nil {
			return err
		}
		out, err := os.OpenFile(path, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, mode.Perm()|0o600)
		if err != nil {
			rc.Close()
			return err
		}
		_, err = io.Copy(out, rc)
		rc.Close()
		out.Close()
		if err != nil {
			return err
		}
	}
	return nil
}

func main() {
	cache, err := os.UserCacheDir()
	if err != nil {
		cache = os.TempDir()
	}
	base := filepath.Join(cache, "HauntedHouse")
	runtimeDir := filepath.Join(base, "runtime-"+shortHash(runtimeZip))
	ready := filepath.Join(runtimeDir, ".ready")

	if _, err := os.Stat(ready); err != nil {
		fmt.Println("Preparing the haunted house (first run only)...")
		os.RemoveAll(runtimeDir)
		tmp := runtimeDir + ".partial"
		os.RemoveAll(tmp)
		if err := unpack(tmp); err != nil {
			fail("Could not unpack the game: %v", err)
		}
		if err := os.Rename(tmp, runtimeDir); err != nil {
			fail("Could not unpack the game: %v", err)
		}
		os.WriteFile(ready, []byte("ok"), 0o644)
	}

	game := filepath.Join(base, "HauntedHouse-"+shortHash(gameScript)+".py")
	if _, err := os.Stat(game); err != nil {
		if err := os.WriteFile(game, gameScript, 0o644); err != nil {
			fail("Could not write the game file: %v", err)
		}
	}

	python := filepath.Join(runtimeDir, "python", "python.exe")
	if runtime.GOOS != "windows" {
		python = filepath.Join(runtimeDir, "python", "bin", "python3")
	}

	// -I: isolated mode, so the player's own Python settings can't interfere
	cmd := exec.Command(python, "-I", game)
	cmd.Dir = base
	cmd.Stdin, cmd.Stdout, cmd.Stderr = os.Stdin, os.Stdout, os.Stderr
	if err := cmd.Run(); err != nil {
		if exitErr, ok := err.(*exec.ExitError); ok {
			pause()
			os.Exit(exitErr.ExitCode())
		}
		fail("Could not start the game: %v", err)
	}
}
