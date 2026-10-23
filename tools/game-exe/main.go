// HauntedHouse.exe - the game as a single, standalone Windows program.
//
// The exe carries its own copy of Python (a trimmed python-build-standalone
// runtime) and the game (HauntedHouse.py plus the haunted_house package).
// On the first run it unpacks them into %LOCALAPPDATA%\HauntedHouse, then it
// simply runs the game in this console.
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

//go:embed game.zip
var gameZip []byte

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

// unpack extracts a zip archive into dest.
func unpack(archive []byte, dest string) error {
	r, err := zip.NewReader(bytes.NewReader(archive), int64(len(archive)))
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

// extract unpacks an archive into dir via a temporary folder, and marks it ready.
func extract(archive []byte, dir string) {
	os.RemoveAll(dir)
	tmp := dir + ".partial"
	os.RemoveAll(tmp)
	if err := unpack(archive, tmp); err != nil {
		fail("Could not unpack the game: %v", err)
	}
	if err := os.Rename(tmp, dir); err != nil {
		fail("Could not unpack the game: %v", err)
	}
	os.WriteFile(filepath.Join(dir, ".ready"), []byte("ok"), 0o644)
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
		extract(runtimeZip, runtimeDir)
	}

	// each game version gets its own folder, so an updated exe never runs old files
	gameDir := filepath.Join(base, "game-"+shortHash(gameZip))
	if _, err := os.Stat(filepath.Join(gameDir, ".ready")); err != nil {
		extract(gameZip, gameDir)
	}
	game := filepath.Join(gameDir, "HauntedHouse.py")

	python := filepath.Join(runtimeDir, "python", "python.exe")
	if runtime.GOOS != "windows" {
		python = filepath.Join(runtimeDir, "python", "bin", "python3")
	}

	// -I: isolated mode, so the player's own Python settings can't interfere
	// (HauntedHouse.py adds its own folder to the import path, so the package is found)
	cmd := exec.Command(python, "-I", game)
	cmd.Dir = gameDir
	cmd.Stdin, cmd.Stdout, cmd.Stderr = os.Stdin, os.Stdout, os.Stderr
	if err := cmd.Run(); err != nil {
		if exitErr, ok := err.(*exec.ExitError); ok {
			pause()
			os.Exit(exitErr.ExitCode())
		}
		fail("Could not start the game: %v", err)
	}
}
