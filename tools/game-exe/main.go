// HauntedHouse.exe - the game as a single, standalone Windows program.
//
// The exe carries its own copy of Python (a trimmed python-build-standalone
// runtime, with tkinter for the window) and the game: HauntedHouse.py, the
// haunted_house package and walkthrough.txt. On the first run it unpacks them
// into %LOCALAPPDATA%\HauntedHouse (this takes a few seconds), then it starts
// the game window. No console window opens, and nothing needs to be installed.
//
// Any arguments are passed on to the game, for example:
//
//	HauntedHouse.exe --autoplay
//
// Build with build.sh in this folder (see the README).
package main

import (
	"archive/zip"
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
	"strings"
)

//go:embed runtime.zip
var runtimeZip []byte

//go:embed game.zip
var gameZip []byte

// fail shows an error (a message box on Windows, see errors_windows.go) and quits.
func fail(format string, args ...any) {
	showError(fmt.Sprintf(format, args...))
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
		fail("Could not unpack the game:\n%v", err)
	}
	if err := os.Rename(tmp, dir); err != nil {
		fail("Could not unpack the game:\n%v", err)
	}
	os.WriteFile(filepath.Join(dir, ".ready"), []byte("ok"), 0o644)
}

func main() {
	cache, err := os.UserCacheDir()
	if err != nil {
		cache = os.TempDir()
	}
	base := filepath.Join(cache, "HauntedHouse")

	// each Python and game version gets its own folder, so an updated exe never runs old files
	runtimeDir := filepath.Join(base, "runtime-"+shortHash(runtimeZip))
	if _, err := os.Stat(filepath.Join(runtimeDir, ".ready")); err != nil {
		extract(runtimeZip, runtimeDir)
	}
	gameDir := filepath.Join(base, "game-"+shortHash(gameZip))
	if _, err := os.Stat(filepath.Join(gameDir, ".ready")); err != nil {
		extract(gameZip, gameDir)
	}

	// pythonw.exe runs Python without a console window
	python := filepath.Join(runtimeDir, "python", "pythonw.exe")
	if runtime.GOOS != "windows" {
		python = filepath.Join(runtimeDir, "python", "bin", "python3")
	}

	// -I: isolated mode, so the player's own Python settings can't interfere
	// (HauntedHouse.py adds its own folder to the import path, so the package is found)
	args := append([]string{"-I", filepath.Join(gameDir, "HauntedHouse.py")}, os.Args[1:]...)
	cmd := exec.Command(python, args...)
	cmd.Dir = gameDir
	var stderr bytes.Buffer
	cmd.Stderr = &stderr
	if err := cmd.Run(); err != nil {
		details := strings.TrimSpace(stderr.String())
		if len(details) > 1500 {
			details = "..." + details[len(details)-1500:]
		}
		fail("The game stopped unexpectedly.\n\n%v\n%s", err, details)
	}
}
