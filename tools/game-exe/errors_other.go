//go:build !windows

package main

import (
	"fmt"
	"os"
)

// showError prints the error (used by test builds on Linux and macOS).
func showError(message string) {
	fmt.Fprintln(os.Stderr, message)
}
